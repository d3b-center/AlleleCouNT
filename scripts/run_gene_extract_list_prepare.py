#!/usr/bin/env python3

import argparse
import pandas as pd
from format_parser import read_vcf_gene_list
import re
import subprocess
import os
# coding=utf8
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-i", "--input", help="provide sample vcf file")
parser.add_argument("-id", "--sampleid", help="provide sample ID")
parser.add_argument("-freq", "--frequency", help="Frequency cutoff for popmax")
parser.add_argument("-ped", "--peddy", help="Peddy file")
# Read arguments from command line
args = parser.parse_args()


def extract_BS_id_peddy_file(peddy_file,column_label):
    pattern = 'BS_'
    paternal_id_uni = list(peddy_file[column_label].unique())
    for i in paternal_id_uni:
        i=str(i)
        if len(re.findall(pattern,i)):
            return(i)
    return None

def organize_clean_dataframe(bcftool_tsv,gene,args):
    
    bcftool_tsv["gene"] = gene

    # remove entries with . as popmax
    bcftool_tsv = bcftool_tsv[bcftool_tsv.popmax != "."]
    bcftool_tsv["popmax"] = bcftool_tsv["popmax"].astype(float)

    # set criteria for rare variant
    bcftool_tsv = bcftool_tsv[bcftool_tsv.popmax < float(args.frequency)]
    bcftool_tsv = bcftool_tsv.drop(["popmax"], axis=1)  # not required anymore

    # split columns
    bcftool_tsv[["proband_germline_ref_depth", "proband_germline_alt_depth"]] = bcftool_tsv["ref,alt depth" ].str.split(",", 1, expand=True)
    bcftool_tsv["BS_ID"] = args.sampleid    

    bcftool_tsv["proband_germline_vaf"] =  bcftool_tsv["proband_germline_vaf"].round(2)

    return bcftool_tsv

if not args.input.endswith('.vcf.gz'): #check input is in right format, important for security reasons
    raise Exception("Provide vcf file in .vcf.gz format")

cmd = 'bcftools query -l '+args.input
samples_vcfs = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
no_samples_vcf=samples_vcfs.count('\n')+1

# extract gene list from vcf file
gene = read_vcf_gene_list(args.input)
del gene[-1]  # last element in the list is end of the file which is not required

#fill VAF within the VAF
cmd_bcftools_tags ='bcftools +fill-tags '+args.input+' -o tmp.VAF.vcf.gz -- -t FORMAT/VAF'
subprocess.check_output(cmd_bcftools_tags, shell=True).decode('utf-8').strip()


cmd_bcftools="echo 'None'"

sample_list=args.sampleid
if (args.peddy): #check peddy file provided
    peddy_file = pd.read_csv(args.peddy, sep="\t",low_memory=False)
    paternal_id=extract_BS_id_peddy_file(peddy_file,"paternal_id")
    maternal_id=extract_BS_id_peddy_file(peddy_file,"maternal_id")
    if(paternal_id and maternal_id):
        sample_list=sample_list+','+paternal_id+','+maternal_id
    elif (paternal_id):
        sample_list=sample_list+','+paternal_id
    elif (maternal_id):
        sample_list=sample_list+','+maternal_id  

cmd_bcftools="bcftools query -f '%gnomad_3_1_1_AF\t%CHROM\t%POS\t%END\t%REF\t%ALT\t[%AD\t][%DP\t][%VAF\t]\n' --samples "+sample_list+" "+"tmp.VAF.vcf.gz > tmp_bcftool_germline.tsv"

subprocess.check_output(cmd_bcftools, shell=True).decode('utf-8').strip()

# read tsv file from bcftools
bcftool_tsv = pd.read_csv('tmp_bcftool_germline.tsv', sep="\t",low_memory=False)
del bcftool_tsv[bcftool_tsv.columns[-1]] #remove last empty columns

if (args.peddy):
    if(paternal_id and maternal_id ):
        bcftool_tsv.columns = [
        "popmax",
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "ref,alt depth",
        "ref,alt depth_paternal",
        "ref,alt depth_maternal",
        "proband_germline_depth",
        "paternal_germline_depth",
        "maternal_germline_depth",
        "proband_germline_vaf",
        "paternal_germline_vaf",
        "maternal_germline_vaf"
        ]
        # split columns
        bcftool_tsv[["paternal_ref_depth_germline", "paternal_alt_depth_germline"]] = bcftool_tsv["ref,alt depth_paternal"].str.split(",", 1, expand=True)    
        bcftool_tsv[["maternal_ref_depth_germline", "maternal_alt_depth_germline"]] = bcftool_tsv["ref,alt depth_maternal"].str.split(",", 1, expand=True)    
        bcftool_data_processed=organize_clean_dataframe(bcftool_tsv,gene,args)

        bcftool_data_processed = bcftool_data_processed[
            [
            "BS_ID",
            "gene",
            "chr",
            "start",
            "end",
            "ref",
            "alt",
            "proband_germline_ref_depth",
            "proband_germline_alt_depth",
            "paternal_ref_depth_germline",
            "paternal_alt_depth_germline",
            "maternal_ref_depth_germline",
            "maternal_alt_depth_germline",
            "proband_germline_depth",
            "paternal_germline_depth",
            "maternal_germline_depth",
            "proband_germline_vaf",
            "paternal_germline_vaf",
            "maternal_germline_vaf",
            ]
        ]

        bcftool_data_processed["paternal_germline_vaf"] = bcftool_data_processed["paternal_germline_vaf"].round(2)
        bcftool_data_processed["maternal_germline_vaf"] = bcftool_data_processed["maternal_germline_vaf"].round(2)
        
    elif(maternal_id):
        bcftool_tsv.columns = [
        "popmax",
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "ref,alt depth",
        "ref,alt depth_maternal",
        "proband_germline_depth",
        "maternal_germline_depth",
        "proband_germline_vaf",
        "maternal_germline_vaf"
        ]  
        bcftool_tsv[["maternal_ref_depth_germline", "maternal_alt_depth_germline"]] = bcftool_tsv["ref,alt depth_maternal"].str.split(",", 1, expand=True)       

        bcftool_data_processed = organize_clean_dataframe(bcftool_tsv,gene,args)
        bcftool_data_processed = bcftool_data_processed[
            [
            "BS_ID",
            "gene",
            "chr",
            "start",
            "end",
            "ref",
            "alt",
            "proband_germline_ref_depth",
            "proband_germline_alt_depth",
            "maternal_ref_depth_germline",
            "maternal_alt_depth_germline",
            "proband_germline_depth",
            "maternal_germline_depth",
            "proband_germline_vaf",
            "maternal_germline_vaf",
            ]
        ]

        bcftool_data_processed["maternal_germline_vaf"] = bcftool_data_processed["maternal_germline_vaf"].round(2)
    elif(paternal_id):
        bcftool_tsv.columns = [
        "popmax",
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "ref,alt depth",
        "ref,alt depth_paternal",
        "proband_germline_depth",
        "paternal_germline_depth",
        "proband_germline_vaf",
        "paternal_germline_vaf",
        ]      
        bcftool_tsv[["paternal_ref_depth_germline", "paternal_alt_depth_germline"]] = bcftool_tsv["ref,alt depth_paternal"].str.split(",", 1, expand=True)  
        bcftool_tsv[["proband_germline_ref_depth", "proband_germline_alt_depth"]] = bcftool_tsv["ref,alt depth"].str.split(",", 1, expand=True)
        bcftool_data_processed=organize_clean_dataframe(bcftool_tsv,gene,args)

        bcftool_data_processed = bcftool_data_processed[
            [
            "BS_ID",
            "gene",
            "chr",
            "start",
            "end",
            "ref",
            "alt",
            "proband_germline_ref_depth",
            "proband_germline_alt_depth",
            "paternal_ref_depth_germline",
            "paternal_alt_depth_germline",
            "proband_germline_depth",
            "paternal_germline_depth",
            "germline_vaf",
            "paternal_germline_vaf",
            ]
        ]

        bcftool_data_processed["paternal_germline_vaf"] = bcftool_data_processed["paternal_germline_vaf"].round(2)
    else:
        # set up pandas dataframe
        bcftool_tsv.columns = [
        "popmax",
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "ref,alt depth",
        "proband_germline_depth",
        "proband_germline_vaf",
        ]
        bcftool_data_processed=organize_clean_dataframe(bcftool_tsv,gene,args)

        bcftool_data_processed =  bcftool_data_processed[
        [
            "BS_ID",
            "gene",
            "chr",
            "start",
            "end",
            "ref",
            "alt",
            "proband_germline_ref_depth",
            "proband_germline_alt_depth",
            "proband_germline_depth",
            "proband_germline_vaf",
        ]
        ]
else:
    # set up pandas dataframe
    bcftool_tsv.columns = [
    "popmax",
    "chr",
    "start",
    "end",
    "ref",
    "alt",
    "ref,alt depth",
    "proband_germline_depth",
    "proband_germline_vaf",
    ]
    bcftool_data_processed=organize_clean_dataframe(bcftool_tsv,gene,args)

    bcftool_data_processed =  bcftool_data_processed[
    [
        "BS_ID",
        "gene",
        "chr",
        "start",
        "end",
        "ref",
        "alt",
        "proband_germline_ref_depth",
        "proband_germline_alt_depth",
        "proband_germline_depth",
        "proband_germline_vaf",
    ]
    ]

list_output_file_name=args.sampleid+".list_bam-readcount.tsv"
germline_output_file=args.sampleid+".germline.output.tsv"
bcftool_data_processed.to_csv(germline_output_file, sep="\t", index=False)

list_readcount = bcftool_data_processed[["chr", "start", "end"]]
list_readcount.rename(columns={"chr": "chromosome"})
list_readcount.to_csv(list_output_file_name, sep="\t", index=False)

#subprocess.run('rm tmp.VAF.vcf.gz tmp_bcftool_germline.tsv', shell=True)
os.remove("tmp.VAF.vcf.gz") # removing temo files
os.remove("tmp_bcftool_germline.tsv")
