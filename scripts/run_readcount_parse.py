#!/usr/bin/env python3

import argparse
import pandas as pd


def func_parse_data(args, parse_data):
    # taken from https://github.com/genome/bam-readcount/tree/master/tutorial
    # Per-base/indel data fields
    # IMPORTANT: this relies on Python 3.6+ to maintain insertion order
    # Each field is a key with value a function to convert to the
    # appropriate data type
    base_fields = {
        "base": str,
        "count": int,
        "avg_mapping_quality": float,
        "avg_basequality": float,
        "avg_se_mapping_quality": float,
        "num_plus_strand": int,
        "num_minus_strand": int,
        "avg_pos_as_fraction": float,
        "avg_num_mismatches_as_fraction": float,
        "avg_sum_mismatch_qualities": float,
        "num_q2_containing_reads": int,
        "avg_distance_to_q2_start_in_q2_reads": float,
        "avg_clipped_length": float,
        "avg_distance_to_effective_3p_end": float,
    }

    # Open the bam-readcount output file and read it line by line
    # Note that the output has no header, so we consume every line
    with open(args.bam_readcount_output) as in_fh:
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
                # Skip zero-depth bases
                if depth == 0:
                    continue
                if base_data["base"] == "=":
                    continue
                # Skip reference bases and bases with no counts
                if base_data["base"] == reference_base:  # or base_data['count'] == 0:
                    continue
                # Calculate an allele frequency (VAF) from the base counts
                vaf = base_data["count"] / depth
                # Filter on minimum depth and VAF
                if depth >= int(args.minDepth):  # minDepth
                    if (
                        base_data["base"][0] == "-" and len(base_data["base"]) > 1
                    ):  # convert bam-readcount deletion type to maf file format
                        reference_base_tmp = reference_base
                        reference_base = base_data["base"][1:]
                        base_data["base"] = reference_base_tmp
                    if (
                        base_data["base"][0] == "+" and len(base_data["base"]) > 1
                    ):  # convert bam-readcount insertion type to maf file format
                        base_data["base"] = reference_base + base_data["base"][1:]

                    row = [
                        chrom,
                        position,
                        reference_base,
                        base_data["base"],
                        "%0.2f" % (vaf),
                        depth,
                        base_data["count"],
                    ]

                    parse_data.append(row)
    return parse_data


# coding=utf8
# Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--bam_readcount_output", help="bam_readcount_output")
parser.add_argument("-t", "--tsv", help="provide bcftools output in tsv format")
parser.add_argument("-id", "--sampleid", help="sampleid for the run")
parser.add_argument(
    "-min", "--minDepth", help="min tumor depth required to be consider for output"
)
args = parser.parse_args()

parse_data = []
headers = [
    "chr",
    "start",
    "ref",
    "alt",
    "vaf_tumor",
    "alt_depth_tumor",
    "ref_depth_tumor",
]  # tumor headers

list_data = func_parse_data(args, parse_data)  # tumor
df_readcount = pd.DataFrame(list_data, columns=headers)

# read tsv file from bcftools
bcftool_tsv = pd.read_csv(args.tsv, sep="\t")  # germline

merge_dataframe = pd.merge(
    bcftool_tsv, df_readcount, how="inner", on=["chr", "start", "ref", "alt"]
)

merge_dataframe["tumor_depth"] = merge_dataframe["ref_depth_tumor"].astype(
    int
) + merge_dataframe["alt_depth_tumor"].astype(int)
merge_dataframe = merge_dataframe[
    [
        "BS_ID",
        "gene",
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "ref_depth_germline",
        "alt_depth_germline",
        "germline_depth",
        "germline_vaf",
        "ref_depth_tumor",
        "alt_depth_tumor",
        "tumor_depth",
        "vaf_tumor",
    ]
]

# output_file in tsv format
output_file_name = args.sampleid + ".loh.out.tsv"
merge_dataframe.to_csv(output_file_name, sep="\t", index=False)
