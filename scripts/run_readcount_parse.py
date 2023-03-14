#!/usr/bin/env python3

import argparse
import pandas as pd
import subprocess
import re
import os
import sys
from format_parser import extract_BS_id_peddy_file
from format_parser import CustomThread
from format_parser import func_parse_bamread_data
# coding=utf8
# Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument("--tsv", help="bcftool_output_file")
parser.add_argument("--sampleid", help="patient primary sampleid for this run")
parser.add_argument("--reference", help="human reference")
parser.add_argument("--patientbamcrams",nargs='+',help="provide one or more bam/cram file for patient tumor")
parser.add_argument("--list", help="path to directory containing regions from germline run to consider in tumor")
parser.add_argument("--peddy", help="Peddy file containing parental information")
parser.add_argument("--minDepth",default=1,help="min tumor depth required to be consider for tumor output")
parser.add_argument("--bamcramsampleID",nargs='+',help="Array of sample IDs for provided for cram/bam files in the same order as inputs")

args = parser.parse_args()

def worker(region_list,bamcram,read_file_name,ID,headers):
    # Run the function for a specific region and returns required pandas dataframe
    # Each thread will run it's own subprocess to speed up the computation"

    cmd_bamreadcount ='bam-readcount -w1 -f '+args.reference+' '+bamcram+' -l '+ region_list +' > '+read_file_name
    subprocess.run(cmd_bamreadcount,shell=True)

    parse_data = []
    list_data = func_parse_bamread_data(read_file_name,parse_data,args.minDepth)  # tumor data as a list
    df_readcount_thread = pd.DataFrame(list_data, columns=headers) # convert to pandas with headers

    target_header= "proband_"+ID+"_tumor_depth"
    first_header= "proband_"+ID+"_tumor_ref_depth"
    second_header= "proband_"+ID+"_tumor_alt_depth"
    
    df_readcount_thread[target_header] = df_readcount_thread[first_header].astype(int) + df_readcount_thread[second_header].astype(int)
    os.remove(read_file_name)

    return df_readcount_thread

def parse_bam_readcout_data(bamcram,ID,path_lists):

    #This function operates on bam/crams files to prepare headers, read regions from dir of list,fire threads and collect data to merge them together
    # Function will return required data for given bamcram file and lists
    headers = [
        "chr",
        "start",
        "ref",
        "alt",
        "tumor_vaf",
        "tumor_alt_depth",
        "tumor_ref_depth",
    ]  # tumor headers
   
    headers=["proband_"+ID+"_"+i if i not in ('chr', 'start', 'ref', 'alt') else i for i in headers ] #prepare headers for parental dataframes
    
    ext_file=args.sampleid+".list"
   
    current_path = os.getcwd()
    list_dir_path = path_lists#os.path.join(current_path,'tmp_list') 
    count_list_files=0
    
    list_files_found=[]
    for x in os.listdir(list_dir_path):
        if x.endswith(ext_file):
            list_files_found.append(x)
    
    fired_cram_thread=[]
    for thread_list in range(0,len(list_files_found),1):
        read_file_name =ID+"."+list_files_found[thread_list]+'.readcount.out'
        bamread_outfile_name = os.path.join(list_dir_path,read_file_name) 
        bamread_input_list_name = os.path.join(list_dir_path,list_files_found[thread_list])
        thread_per_bamcram = CustomThread(target=worker, args=(bamread_input_list_name,bamcram,bamread_outfile_name,ID,headers))
        thread_per_bamcram .start()
        fired_cram_thread.append(thread_per_bamcram)
    patient_thread_frame=[]
    for thread_per_bamcram in fired_cram_thread:
        patient_thread_frame.append(thread_per_bamcram.join())   

    df_readcount = pd.concat(patient_thread_frame)
    df_readcount.sort_values(by='start', ascending=False)

    return df_readcount


if __name__ == "__main__":

    # read tsv file from bcftools
    bcftool_tsv = pd.read_csv(args.tsv, sep="\t")  # germline
    sample_array=[]
    
    cram_files = args.patientbamcrams#.split(',')
    if args.bamcramsampleID:
        sample_array = args.bamcramsampleID#.split(' ')
    else:
        for file_address in cram_files:
            cmd_samtools="samtools samples -T SM -X "+file_address+" "+file_address+".crai" # check of bam 
            result=subprocess.run(cmd_samtools,shell=True,capture_output=True, text=True, check=True)
            sample=result.stdout.split()[0]
            if len(re.findall("BS_",sample)):
                sample_array.append(sample)
                print("BS ID found: Using it for "+file_address, file=sys.stdout)
            else:
                file_name=file_address.split("/")[-1]
                nameroot=file_name.split(".")[0]
                print("Using nameroot for "+file_name, file=sys.stdout)
                sample_array.append(nameroot)

    fired_thread=[]
    patient_tumor_df=[]
    for index,file_address in enumerate(cram_files):
        t1 = CustomThread(target=parse_bam_readcout_data, args=(file_address,sample_array[index],args.list))
        t1.start()
        fired_thread.append(t1)
    merge_dataframe=bcftool_tsv
    for thread_running in fired_thread:
        patient_tumor_df=thread_running.join()
    #t2 = CustomThread(target=parse_bam_readcout_data, args=(args.paternalbamcram,"paternal"))
    #t3 = CustomThread(target=parse_bam_readcout_data, args=(args.maternalbamcram,"maternal"))
        merge_dataframe = pd.merge(merge_dataframe, patient_tumor_df, how="inner", on=["chr", "start", "ref", "alt"])
    
    # output_file in tsv format
    loh_output_file_name = args.sampleid + ".loh.out.tsv"
    merge_dataframe.to_csv(loh_output_file_name, sep="\t", index=False)      
    
    #
#    os.remove(args.tsv)
#    for list_file in os.listdir(args.list): # deleting files from the tmp folder
#        print(list_file)
#        if list_file.endswith(".list"):
#            os.remove(list_file)
    #os.remove(*+"."+args.sampleid+".list")
    
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