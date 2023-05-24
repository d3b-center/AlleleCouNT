#!/usr/bin/env python3

import re
import gzip
import logging
from threading import Thread
import pandas as pd


class CustomThread(Thread):
    # overriding join function in standard threads
    # With this in place join function will return data structure from the function
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None
    ):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def func_parse_bamread_data(bam_readcount_output_file, minDepth, headers):
    # Initially taken from https://github.com/genome/bam-readcount/tree/master/tutorial
    # adapted to get more specific data
    # Per-base/indel data fields
    # IMPORTANT: this relies on Python 3.6+ to maintain insertion order
    # Each field is a key with value a function to convert to the
    # appropriate data type
    parse_data = []

    base_fields = {"base": str, "count": int}
    ref_list = []
    # Open the bam-readcount output file and read it line by line
    # Note that the output has no header, so we consume every line
    prevLine = []
    with open(bam_readcount_output_file) as in_fh:
        for line in in_fh:
            # Strip newline from end of line
            line = line.strip()
            # Fields are tab-separated, so split into a list on \t
            fields = line.split("\t")
            # The first four fields contain overall information about the position
            chrom = fields[0]  # Chromosome/reference
            position = int(fields[1])  # Position (1-based)
            reference_base = fields[2]  # Reference base
            depth = int(fields[3])  # Depth of coverage
            # The remaining fields are data for each base or indel
            # Iterate over each base/indel
            ref_count = 0
            for base_data_string in fields[4:]:
                # We will store per-base/indel data in a dict
                base_data = {}
                # Split the base/indel data on ':'
                base_values = base_data_string.split(":")
                # Iterate over each field of the base/indel data
                for i, base_field in enumerate(base_fields.keys()):
                    # Store each field of data, converting to the appropriate
                    # data type
                    base_data[base_field] = base_fields[base_field](base_values[i])

                # Skip reference bases and store ref count in ref_list
                if base_data["base"] == reference_base:
                    ref_count = base_data["count"]
                    ref_list.append(
                        [chrom, position, base_data["base"], ref_count]
                    )  # store ref count data
                    continue
                # Skip zero-depth bases
                if depth == 0:
                    continue
                # bases with no counts
                if base_data["base"] == "=" or base_data["count"] == 0:
                    continue
                # Calculate an allele frequency (VAF) from the base counts
                vaf = base_data["count"] / depth
                # Filter on minimum depth and VAF
                if depth >= int(minDepth):  # minDepth
                    if (
                        base_data["base"][0] == "-" and len(base_data["base"]) > 1
                    ):  # convert bam-readcount deletion calls type to maf file format
                        if len(prevLine) > 3:
                            ref_base = prevLine[2] + base_data["base"][1:]
                            alt_base = prevLine[2]
                            row = [
                                prevLine[0],
                                prevLine[1],
                                ref_base,
                                alt_base,
                                "%0.2f" % (vaf),
                                depth,
                                base_data["count"],
                                ref_count,
                            ]
                            parse_data.append(row)
                            ref_list.append(
                                [prevLine[0], prevLine[1], ref_base, ref_count]
                            )
                            continue
                    if (
                        base_data["base"][0] == "+" and len(base_data["base"]) > 1
                    ):  # convert bam-readcount insertion calls type to maf file format
                        base_data["base"] = reference_base + base_data["base"][1:]

                    row = [
                        chrom,
                        position,
                        reference_base,
                        base_data["base"],
                        "%0.2f" % (vaf),
                        depth,
                        base_data["count"],
                        ref_count,
                    ]
                    parse_data.append(row)  # calls
                prevLine = fields  # save previous line fields
    # add ref count to parse data
    parse_df = pd.DataFrame(parse_data, columns=headers)
    ref_df = pd.DataFrame(ref_list, columns=["chr", "start", "ref", "ref_count"])
    merge_df = pd.merge(parse_df, ref_df, how="left", on=["chr", "start", "ref"])
    merge_df = merge_df.drop(columns=[headers[-1]])
    merge_df = merge_df.rename(columns={"ref_count": headers[-1]})
    return merge_df


def extract_format_fields_vcf(lines, header):
    """Returns gene for single variant call by parsing format field from vcf
    Args:
        Lines : format field from vcf file
        header: CSQ header from vcf file
    Return:
        Returns Gene name (a string) for single variant call from the format field
    """
    format_split = [seg.split("|") for seg in lines.split(",")]
    fields = header.split("|")
    label = "Gene"
    gene = ""
    if label in fields:
        index_to_pick = fields.index(label)
        for split in format_split:
            # Get gene if pick field in the format is 1
            if (
                len(split) > 120
            ):  # run only with list elements with more than 120 in length that contains gene info
                if split[fields.index("PICK")] == "1":
                    gene = split[index_to_pick - 1]
                    break
                # Get gene if canonical field in the format is YES
                elif split[fields.index("CANONICAL")] == "YES":
                    gene = split[index_to_pick - 1]
                    break
                # Get gene if TSL field in the format is 1
                elif split[fields.index("TSL")] == "1":
                    gene = split[index_to_pick - 1]
                    break
                # Get gene if BIOTYPE field in the format is protein_coding
                elif split[fields.index("BIOTYPE")] == "protein_coding":
                    gene = split[index_to_pick - 1]
                    break
                # else select gene that is next to modifer field
                elif split[fields.index("SYMBOL")] == "MODIFIER":
                    modifier = fields.index("MODIFIER")
                    gene = split[modifier + 1]
    return gene


def read_vcf_gene_list(file):
    """Returns list of gene for variants called within the vcf file
    Args:
        file : VCF file for a sample of interest
    Return:
        list of gene extracted from format field within a vcf file
    """
    gene_list = []
    vcf_calls = []

    chunks = 8  # fire 25 threads at a time

    with (gzip.open if file.endswith("gz") else open)(file, "rt") as f:
        # grab CSQ description string from header; contains field names separated by |
        for line in f:
            if line.startswith("##INFO=<ID=CSQ"):
                CSQ_header = line.split(",")[3]
                break
        # Reach the end of the header (lines that start with #) and process the first record
        for line in f:
            if not line.startswith("#"):
                gene_list.append(
                    extract_format_fields_vcf(line.split("\t")[7], CSQ_header)
                )
                break
        # Process remaining records
        gene_list = [extract_format_fields_vcf(line, CSQ_header) for line in f]

    return gene_list


def extract_BS_id_peddy_file(peddy_file, column_label):
    """Returns sample id for the parent from the peddy file
    Args:
        file : peddy file and column label with the peddy file
    Return:
        Returns sample id for the parent from the peddy file
    """
    pattern = "BS_"  # recognize this pattern
    paternal_id_uni = list(peddy_file[column_label].unique())
    for i in paternal_id_uni:
        i = str(i)
        if len(re.findall(pattern, i)):
            return i
    return None
