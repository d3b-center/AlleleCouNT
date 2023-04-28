#!/usr/bin/env python3

import argparse
import pandas as pd
import subprocess
import re
import os
from loh_functions import extract_BS_id_peddy_file
from loh_functions import CustomThread
from loh_functions import func_parse_bamread_data
from datetime import datetime
import logging

# coding=utf8
# Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument("--tsv", help="bcftool output file in tsv format")
parser.add_argument("--participant_id", help="patient participant id for this run")
parser.add_argument("--reference", help="human reference")
parser.add_argument(
    "--patientbamcrams",
    nargs="+",
    help="provide one or more bam/cram file for patient tumor",
)
parser.add_argument(
    "--list_dir",
    help="path to directory containing regions created by germline run to consider in tumor",
)
parser.add_argument("--peddy", help="peddy file containing parental information")
parser.add_argument(
    "--minDepth",
    default=1,
    help="min tumor depth required to be consider for tumor output",
)
parser.add_argument(
    "--bamcramsampleID",
    nargs="+",
    help="array of sample IDs provided for cram/bam files in the same order as input cram/bam files",
)

args = parser.parse_args()

# define logging variable as global
logger = logging


def worker(region_list, bamcram, read_file_name, ID, headers):
    # Run the function for a specific region and returns required pandas dataframe
    # Each thread will run it's own subprocess to speed up the computation"

    cmd_bamreadcount = (
        "bam-readcount -w1 -f "
        + args.reference
        + " "
        + bamcram
        + " -l "
        + region_list
        + " > "
        + read_file_name
    )
    subprocess.run(cmd_bamreadcount, shell=True)

    list_data = func_parse_bamread_data(
        read_file_name, args.minDepth
    )  # tumor data as a list
    df_readcount_thread = pd.DataFrame(
        list_data, columns=headers
    )  # convert to pandas with headers

    os.remove(read_file_name)

    return df_readcount_thread


def parse_bam_readcout_data(bamcram, ID, path_lists):
    # This function operates on bam/crams files to prepare headers,
    # read regions from dir of list, fire threads and collect data to merge them together
    # Function will return required data for given bamcram file and lists
    headers = [
        "chr",
        "start",
        "ref",
        "alt",
        "tumor_vaf",
        "tumor_depth",
        "tumor_alt_depth",
        "tumor_ref_depth",
    ]  # tumor headers

    headers = [
        "proband_" + ID + "_" + i if i not in ("chr", "start", "ref", "alt") else i
        for i in headers
    ]  # prepare headers for parental dataframes

    ext_file = ".list"

    current_path = os.getcwd()
    list_dir_path = path_lists
    count_list_files = 0

    # reading lists from tmp_list dir
    list_files_found = []
    for x in os.listdir(list_dir_path):
        if x.endswith(ext_file):
            list_files_found.append(x)

    # dividing work into 32 parts per cram file
    logger.info("Sample: %s firing 32 threads per cram file for all the regions" % ID)
    fired_cram_thread = []
    for thread_list in range(0, len(list_files_found), 1):
        read_file_name = ID + "." + list_files_found[thread_list] + ".readcount.out"
        bamread_outfile_name = os.path.join(list_dir_path, read_file_name)
        bamread_input_list_name = os.path.join(
            list_dir_path, list_files_found[thread_list]
        )
        thread_per_bamcram = CustomThread(
            target=worker,
            args=(bamread_input_list_name, bamcram, bamread_outfile_name, ID, headers),
        )
        thread_per_bamcram.start()
        fired_cram_thread.append(thread_per_bamcram)
    patient_thread_frame = []
    for thread_per_bamcram in fired_cram_thread:
        patient_thread_frame.append(thread_per_bamcram.join())
    logger.info("Sample: %s joining threads for this cram file " % ID)

    # joining results from threads together
    df_readcount = pd.concat(patient_thread_frame)
    df_readcount = df_readcount.astype(
        {
            "start": "uint32",  # position
            str(headers[4]): "float32",  # vaf
            str(headers[5]): "uint16",  # total_depth
            str(headers[6]): "uint16",  # alt_depth
            str(headers[7]): "uint16",  # ref_depth
        }
    )
    df_readcount.sort_values(["start", "chr"], ascending=[True, True])

    logger.info("Sample: %s return the pandas dataframe " % ID)
    return df_readcount.convert_dtypes()


def main():
    # setting up logger variable
    logger_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    name = "tumor." + str(logger_time) + ".loh.log"
    logger_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    logger.basicConfig(
        filename=name,
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("Starting bamreadcount run")

    # read tsv file from bcftools
    logger.info("Reading germline input")
    bcftool_tsv = pd.read_csv(args.tsv, sep="\t", low_memory=False)  # germline
    sample_array = []

    cram_files = args.patientbamcrams
    # check if user provided identifers for each cram file or not
    if args.bamcramsampleID:
        logger.info("User provided identifers for bam/cram files")
        sample_array = args.bamcramsampleID
        if len(sample_array) != len(cram_files):
            logger.Exception("provide same number of identifiers as to bam/cram files")
        logger.info("Using user provided enums: %s " % sample_array)

    else:
        logger.info("Extracting identifiers from cram/bam files")
        for file_address in cram_files:
            cmd_samtools = (
                "samtools samples -T SM -X "
                + file_address
                + " "
                + file_address
                + ".crai"
            )  # check of bam
            result = subprocess.run(
                cmd_samtools, shell=True, capture_output=True, text=True, check=True
            )
            sample = result.stdout.split()[0]

            if len(re.findall("BS_", sample)):
                sample_array.append(sample)
                logger.info("BS ID found: Using it for %s " % file_address)
            else:
                file_name = file_address.split("/")[-1]
                nameroot = file_name.split(".")[0]
                logger.info("Using nameroot for %s  " % file_name)
                sample_array.append(nameroot)

    fired_threads = []
    patient_tumor_df = []

    # Firing threads per cram file provided by the user
    for index, file_address in enumerate(cram_files):
        logger.info("Firing thread for %s  " % file_address)
        fire_thread = CustomThread(
            target=parse_bam_readcout_data,
            args=(file_address, sample_array[index], args.list_dir),
        )
        fire_thread.start()
        fired_threads.append(fire_thread)

    merge_dataframe = bcftool_tsv.convert_dtypes()  # convert to appropriate datatype

    logger.info("Joining sample based threads")
    for thread_running in fired_threads:
        patient_tumor_df = thread_running.join()
        merge_dataframe = pd.merge(
            merge_dataframe,
            patient_tumor_df,
            how="left",
            on=["chr", "start", "ref", "alt"],
            indicator=False,
        )

    logger.info("Joined all cram file based threads and merged data")
    # output_file in tsv format
    loh_output_file_name = args.participant_id + ".germline.tumor.version2.loh.out.tsv"
    logger.info("Writing loh app output file")
    merge_dataframe.to_csv(loh_output_file_name, sep="\t", index=False)

    logger.info("Tumor tool run sucessfully")


if __name__ == "__main__":
    main()
