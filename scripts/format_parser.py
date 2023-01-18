#!/usr/bin/env python3

import re
import gzip
import argparse


def extract_format_fields_vcf(lines, header):
    """Returns gene for single variant call by parsing format field from vcf
    Args:
        Lines : format field from vcf file
        header: CSQ header from vcf file
    Return:
        Returns Gene name (a string) for single variant call from the format field
    """
    format_split = []
    format_seg = lines.split(",")
    for seg in format_seg:
        format_split.append(seg.split("|"))
    Fields = header.split("|")
    label = "Gene"
    gene = ""
    if label in Fields:
        index_to_pick = Fields.index(label)
        for split in format_split:
            # Get gene if pick field in the format is 1
            if split[Fields.index("PICK")] == "1":
                gene = split[index_to_pick - 1]
                break
            # Get gene if canonical field in the format is YES
            elif split[Fields.index("CANONICAL")] == "YES":
                gene = split[index_to_pick - 1]
                break
            # Get gene if TSL field in the format is 1
            elif split[Fields.index("TSL")] == "1":
                gene = split[index_to_pick - 1]
                break
            # Get gene if BIOTYPE field in the format is protein_coding
            elif split[Fields.index("BIOTYPE")] == "protein_coding":
                gene = split[index_to_pick - 1]
                break
            # else select gene that is next to modifer field
            elif split[Fields.index("SYMBOL")] == "MODIFIER":
                modifier = Fields.index("MODIFIER")
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
        for line in f:
            gene_list.append(extract_format_fields_vcf(line.split("\t")[7], CSQ_header))
    return gene_list
