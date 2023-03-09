#!/usr/bin/env python3

import argparse
import pandas as pd
import subprocess
import re
import os
from threading import Thread

# coding=utf8
# Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument("--tsv", help="bcftool_output")
parser.add_argument("--sampleid", help="sampleid for the run")
parser.add_argument("--reference", help="human reference")
parser.add_argument("--patientbamcrams", help="provide bam/cram file for tumor")
parser.add_argument("--paternalbamcram", help="provide bam/cram file for tumor")
parser.add_argument("--maternalbamcram", help="provide bam/cram file for tumor")
parser.add_argument("--list", help="list from germline to check for in tumor")
parser.add_argument("--peddy", help="Peddy file")
parser.add_argument("--minDepth",default=1,help="min tumor depth required to be consider for output")
parser.add_argument("--test",help="test")

args = parser.parse_args()

def func_parse_data(bam_readcount_output_file,parse_data):
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
def extract_BS_id_peddy_file(peddy_file,column_label):
    pattern = 'BS_'
    paternal_id_uni = list(peddy_file[column_label].unique())
    for i in paternal_id_uni:
        i=str(i)
        if len(re.findall(pattern,i)):
            return(i)
    return None

class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
 
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
             
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def parse_bam_readcout_data(bamcram,ID):
    parse_data = []

    headers = [
        "chr",
        "start",
        "ref",
        "alt",
        "tumor_vaf",
        "tumor_alt_depth",
        "tumor_ref_depth",
    ]  # tumor headers
   
    #if candidate not in "patient":
    headers=["proband_"+ID+"_"+i if i not in ('chr', 'start', 'ref', 'alt') else i for i in headers ] #prepare headers for parental dataframes
    print(headers)
    read_file_name = ID+'_readcount.out'
    #rum bam-readcount
    cmd_bamreadcount ='bam-readcount -w1 -f '+args.reference+' '+bamcram+' -l '+ args.list +' > '+read_file_name
    subprocess.run(cmd_bamreadcount,shell=True)
    list_data = func_parse_data(read_file_name,parse_data)  # tumor data as a list
    df_readcount = pd.DataFrame(list_data, columns=headers) # convert to pandas with headers

    target_header= "proband_"+ID+"_tumor_depth"
    first_header= "proband_"+ID+"_tumor_ref_depth"
    second_header= "proband_"+ID+"_tumor_alt_depth"
    df_readcount[target_header] = df_readcount[first_header].astype(int) + df_readcount[second_header].astype(int)
    os.remove(read_file_name)
    #df_readcount
    return df_readcount


if __name__ == "__main__":
    #patient_tumor_df=pd.DataFrame()
    #parse_bam_readcout_data(args.patientbamcram,"patient")

    #t1 = CustomThread(target=parse_bam_readcout_data, args=(args.paternalbamcram,"patient"))
    #t1.start()
    #t1.join()
    #patient_tumor_df=t1.join()

    # read tsv file from bcftools
    bcftool_tsv = pd.read_csv(args.tsv, sep="\t")  # germline
    
    cram_files = args.patientbamcrams.split(',')
    for file in cram_files:
        t1 = CustomThread(target=parse_bam_readcout_data, args=(args.paternalbamcram,args.sampleid))
        t1.start()
    
    merge_dataframe=bcftool_tsv
    for i in range(0,len(cram_files),1):
        patient_tumor_df=t1.join()
    #t2 = CustomThread(target=parse_bam_readcout_data, args=(args.paternalbamcram,"paternal"))
    #t3 = CustomThread(target=parse_bam_readcout_data, args=(args.maternalbamcram,"maternal"))
    
        merge_dataframe = pd.merge(merge_dataframe, patient_tumor_df, how="inner", on=["chr", "start", "ref", "alt"])
    #merge_dataframe["tumor_depth"] = merge_dataframe["ref_depth_tumor"].astype(int) + merge_dataframe["alt_depth_tumor"].astype(int)

    # output_file in tsv format
    loh_output_file_name = args.sampleid + ".loh.out.tsv"
    '''
    if (args.peddy): #check peddy file provided
        #t1.start()
        #patient_tumor_df=t1.join()
       # merge_dataframe = pd.merge(bcftool_tsv, patient_tumor_df, how="inner", on=["chr", "start", "ref", "alt"])
       # merge_dataframe["tumor_depth"] = merge_dataframe["ref_depth_tumor"].astype(int) + merge_dataframe["alt_depth_tumor"].astype(int)

        peddy_file = pd.read_csv(args.peddy, sep="\t",low_memory=False)
        paternal_id=extract_BS_id_peddy_file(peddy_file,"paternal_id")
        maternal_id=extract_BS_id_peddy_file(peddy_file,"maternal_id")
        if(paternal_id and maternal_id and args.paternalbamcram and args.maternalbamcram ):
            t1.start()
            #t2.start()
            #t3.start()
            patient_tumor_df=t1.join()
            #paternal_tumor_df=t2.join()
            #maternal_tumor_df=t3.join()
            merge_dataframe = pd.merge(bcftool_tsv, patient_tumor_df, how="inner", on=["chr", "start", "ref", "alt"])
            merge_dataframe["tumor_depth"] = merge_dataframe["ref_depth_tumor"].astype(int) + merge_dataframe["alt_depth_tumor"].astype(int)
            #paternal_tumor_df=parse_bam_readcout_data(args.paternalbamcram,"paternal")
            #paternal_tumor_df=pd.DataFrame()
            #maternal_tumor_df=pd.DataFrame()
            #t1 = CustomThread(target=parse_bam_readcout_data, args=(args.paternalbamcram,"paternal"))
            #t2 = CustomThread(target=parse_bam_readcout_data, args=(args.maternalbamcram,"maternal"))
            #maternal_tumor_df=parse_bam_readcout_data(args.maternalbamcram,"maternal")
            
            
            #paternal_tumor_df["paternal_tumor_depth"] = paternal_tumor_df["paternal_ref_depth_tumor"].astype(int) + paternal_tumor_df["paternal_alt_depth_tumor"].astype(int)
            #maternal_tumor_df["maternal_tumor_depth"] = maternal_tumor_df["maternal_ref_depth_tumor"].astype(int) + maternal_tumor_df["maternal_alt_depth_tumor"].astype(int)
            #patient_paternal_maternal_df = pd.merge(pd.merge(merge_dataframe,paternal_tumor_df, how="inner", on=["chr", "start", "ref", "alt"]),maternal_tumor_df,how="inner", on=["chr", "start", "ref", "alt"])
        
            #loh_output_file_name = args.sampleid+".patient.paternal.maternal" + ".loh.out.tsv"
            #patient_paternal_maternal_df.to_csv(loh_output_file_name, sep="\t", index=False)
        
        elif (paternal_id and args.paternalbamcram):
            paternal_tumor_df=parse_bam_readcout_data(args.paternalbamcram,"paternal")
            paternal_tumor_df["paternal_tumor_depth"] = paternal_tumor_df["paternal_ref_depth_tumor"].astype(int) + paternal_tumor_df["paternal_alt_depth_tumor"].astype(int)
            patient_paternal_df = pd.merge(merge_dataframe,paternal_tumor_df, how="inner", on=["chr", "start", "ref", "alt"])
        
            loh_output_file_name = args.sampleid+".patient.paternal" + ".loh.out.tsv"
            patient_paternal_df.to_csv(loh_output_file_name, sep="\t", index=False)
        elif (maternal_id and args.maternalbamcram ):
            maternal_tumor_df=parse_bam_readcout_data(args.maternalbamcram,"maternal")
            maternal_tumor_df["maternal_tumor_depth"] = maternal_tumor_df["maternal_ref_depth_tumor"].astype(int) + maternal_tumor_df["maternal_alt_depth_tumor"].astype(int)
            patient_maternal_df = pd.merge(merge_dataframe,maternal_tumor_df, how="inner", on=["chr", "start", "ref", "alt"])

            loh_output_file_name = args.sampleid+".patient.maternal" + ".loh.out.tsv"
            patient_maternal_df.to_csv(loh_output_file_name, sep="\t", index=False)
        else: # if no sample id exist within peddy file
            loh_output_file_name = args.sampleid+".patient" + ".loh.out.tsv"
            merge_dataframe.to_csv(loh_output_file_name, sep="\t", index=False)    
         
    else:
        loh_output_file_name = args.sampleid+".patient" + ".loh.out.tsv"
    '''    
    merge_dataframe.to_csv(loh_output_file_name, sep="\t", index=False)      
    

    #os.remove(args.tsv)
    #os.remove(args.list)

'''
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
    '''