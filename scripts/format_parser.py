#!/usr/bin/env python3

import re
import gzip
import argparse


def extract_format_fields_vcf(lines, header):
    ''' Returns gene for single variant call by parsing format field from vcf
        Args:
            Lines : format field from vcf file
            header: CSQ header from vcf file
        Return:
            Returns Gene name (a string) for single variant call from the format field
    '''
    format_split = []
    format_seg = lines.split(",")
    for seg in format_seg:
        format_split.append(seg.split("|"))
    Fields = header.split("|")
    label = "Gene"
    gene = ''
    if label in Fields:
        index_to_pick = Fields.index(label)
        for split in format_split:
            if split[Fields.index('PICK')] == '1': #Get gene if pick field in the format is 1
                gene = split[index_to_pick-1]
                break
            elif split[Fields.index('CANONICAL')] == 'YES': #Get gene if canonical field in the format is YES
                gene = split[index_to_pick-1]
                break
            elif split[Fields.index('SYMBOL')] == 'MODIFIER': #else select gene that is next to modifer field 
                modifier = Fields.index('MODIFIER')
                gene = split[modifier+1]
    return gene


def read_vcf_gene_list(file):
    ''' Returns list of gene for variants called within the vcf file
        Args:
            file : VCF file in gz format
        Return:
            list of gene extracted from format field within a vcf file
    '''
    '''
    if not (file.endswith('gz')):
        raise IOError('vcf file required in gzip format')
    with gzip.open(file, 'rb') as f:
        Lines = f.readlines()

    threshold_count = 10000000001  # very large number
    data = []
    gene_list = []
    for count, line in enumerate(Lines):
        line_sep = re.split(r'\t+', line.decode('utf-8'))
        sp = line_sep[0].split(",")
        if '#CHROM' in line_sep:
            threshold_count = count
        elif '##INFO=<ID=CSQ' in sp:
            CSQ_header = sp[3]
        elif count > threshold_count:
            gene_list.append(extract_format_fields_vcf(
                line_sep[7], CSQ_header))
            data.append(line_sep)
    '''        
    gene_list = []
    with (gzip.open if file.endswith("gz") else open)(file, 'rt') as f:
        # grab CSQ description string from header; contains field names separated by |
        for line in f:
            if line.startswith('##INFO=<ID=CSQ'):
                CSQ_header = line.split(',')[3]
                break
        # Reach the end of the header (lines that start with #) and process the first record 
        for line in f:
            if not line.startswith('#'):
                gene_list.append(extract_format_fields_vcf(line.split('\t')[7], CSQ_header))
                break
        # Process remaining records
        for line in f:
            gene_list.append(extract_format_fields_vcf(line.split('\t')[7], CSQ_header))    
    return (gene_list)
