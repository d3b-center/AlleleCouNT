#!/usr/bin/env python3

import argparse
import pandas as pd
from format_parser import read_vcf_gene_list

# coding=utf8
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-i", "--input", help="provide sample vcf file")
parser.add_argument("-t", "--tsv", help="provide bcftools output in tsv format")
parser.add_argument("-id", "--sampleid", help="provide sample ID")

# Read arguments from command line
args = parser.parse_args()

# extract gene list from vcf file
gene = read_vcf_gene_list(args.input)
del gene[-1]  # last element in the list is end of the file which is not required

# read tsv file from bcftools
bcftool_tsv = pd.read_csv(args.tsv, sep="\t")

# set up pandas dataframe
bcftool_tsv.columns = [
    "popmax",
    "chr",
    "start",
    "end",
    "ref",
    "alt",
    "ref,alt depth",
    "germline_depth",
    "germline_vaf",
]
bcftool_tsv["gene"] = gene

# remove entries with . as popmax
bcftool_tsv = bcftool_tsv[bcftool_tsv.popmax != "."]
bcftool_tsv["popmax"] = bcftool_tsv["popmax"].astype(float)

# set criteria for rare variant
bcftool_tsv = bcftool_tsv[bcftool_tsv.popmax < 0.01]
bcftool_tsv = bcftool_tsv.drop(["popmax"], axis=1)  # not required anymore

# split columns
bcftool_tsv[["ref_depth_germline", "alt_depth_germline"]] = bcftool_tsv[
    "ref,alt depth"
].str.split(",", 1, expand=True)

bcftool_tsv["BS_ID"] = args.sampleid

bcftool_tsv = bcftool_tsv[
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
    ]
]

bcftool_tsv["germline_vaf"] = bcftool_tsv["germline_vaf"].round(2)
bcftool_tsv.to_csv("bcftool_file.tsv", sep="\t", index=False)

list_readcount = bcftool_tsv[["chr", "start", "end"]]
list_readcount.rename(columns={"chr": "chromosome"})
list_readcount.to_csv("list_bam-readcount.tsv", sep="\t", index=False)
