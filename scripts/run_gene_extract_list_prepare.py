#!/usr/bin/env python3

import argparse
import pandas as pd
import re
import subprocess
import os
import sys
from format_parser import read_vcf_gene_list
from format_parser import extract_BS_id_peddy_file
from datetime import datetime
import logging

#logging.debug('a debug messag is not shown')
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

def main():
    
    logger= logging#.getLogger(__name__)
    logger_time=datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    name='germline.'+str(logger_time)+'.loh.log'
    logger.basicConfig(filename=name,format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')

    logger.info('Starting germline run')

    if not args.input.endswith('.vcf.gz'): #check input is in right format, important for security reasons
        logger.Exception("Provide vcf file in .vcf.gz format")

    cmd_samples = 'bcftools query -l '+args.input
    samples_vcfs = subprocess.check_output(cmd_samples, shell=True).decode('utf-8').strip()
    no_samples_vcf=samples_vcfs.count('\n')+1

    # extract gene list from vcf file
    logger.info('Extracting genes from vcf file')
    gene = read_vcf_gene_list(args.input)
   # del gene[-1]  # last element in the list is end of the file which is not required

    sample_list=args.sampleid
    if (args.peddy): #check peddy file provided
        logger.info('Reading peddy file')
        peddy_file = pd.read_csv(args.peddy, sep="\t",low_memory=False)
        paternal_id=extract_BS_id_peddy_file(peddy_file,"paternal_id")
        maternal_id=extract_BS_id_peddy_file(peddy_file,"maternal_id")
        if(paternal_id and maternal_id):
            logger.info('Paternal and maternal IDs found')
            sample_list=sample_list+','+paternal_id+','+maternal_id
        elif (paternal_id):
            logger.info('Paternal and maternal IDs found')
            sample_list=sample_list+','+paternal_id
        elif (maternal_id):
            logger.info('Paternal and maternal IDs found')
            sample_list=sample_list+','+maternal_id  
    logger.info('Running bcftool plugin to add VAF')
    cmd_bcftools_tags ='bcftools +fill-tags '+args.input+' -- -t FORMAT/VAF'
    plugin=subprocess.Popen(cmd_bcftools_tags,shell=True,stdout=subprocess.PIPE)#.decode('utf-8').strip()

    logger.info('Running bcftool to extract data from vcf file into a tmp file')
    cmd_bcftools_test="bcftools query -f '%gnomad_3_1_1_AF\t%CHROM\t%POS\t%END\t%REF\t%ALT\t[%AD\t][%DP\t][%VAF\t]\n' --samples "+sample_list+" "+"-o tmp_bcftool_germline.tsv"
    bcftool_tool=subprocess.run(cmd_bcftools_test,shell=True,stdin=plugin.stdout)

    # read tsv file from bcftools
    logger.info('Reading tmp file from bcftool')
    bcftool_tsv = pd.read_csv('tmp_bcftool_germline.tsv', sep="\t",low_memory=False)
    
    del bcftool_tsv[bcftool_tsv.columns[-1]] #remove last  empty columns
    
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
            logger.info('applying popmax filter and cleaning data for final germline output') 
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

            logger.info('applying popmax filter and cleaning data for final germline output') 
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

            logger.info('applying popmax filter and cleaning data for final germline output') 
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
                "proband_germline_vaf",
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

            logger.info('applying popmax filter and cleaning data for final germline output') 
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

    list_output_file_name="list_bam-readcount."+args.sampleid+".list"
    germline_output_file=args.sampleid+".germline.output.tsv"

    logger.info('Writing final germline output file') 
    bcftool_data_processed.to_csv(germline_output_file, sep="\t", index=False)

    list_readcount = bcftool_data_processed[["chr", "start", "end"]]
    list_readcount.rename(columns={"chr": "chromosome"})

    #split DataFrame into chunks    
    chunks=int(len(list_readcount)/32)+1 #Number of lists
    dirName='tmp_list'
    current_path = os.getcwd()
    list_dir_path = os.path.join(current_path,dirName) 
   
    logger.info('Preparing tmp_list dir with 32 lists as input to tumor tool') 
    if not os.path.exists(list_dir_path):
        os.mkdir(list_dir_path)
        logger.info("Directory  %s  created " % dirName )
    else:    
        logger.info("Directory  %s exists " % dirName)
    
    list_df = [list_readcount[i:i+chunks] for i in range(0,len(list_readcount),chunks)]
    
    #listing list to the files
    for index,chunk in enumerate(list_df):
        list_out_name=str(index)+"."+list_output_file_name
        fullname = os.path.join(dirName, list_out_name) 
        chunk.to_csv(fullname, sep="\t", index=False)
    
    #remove tmp file
    logger.info('Removing tmp file') 
    os.remove("tmp_bcftool_germline.tsv")

    logger.info('Done') 

if __name__ == "__main__":
    main()
        