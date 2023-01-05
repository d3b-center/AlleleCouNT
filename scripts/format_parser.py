import re
import gzip
import argparse

def extract_format_fields_vcf(Lines,header):
    ''' Returns gene for single variant call
        Args:
            Lines : format field from vcf file
            header: CSQ header from vcf file
        Return:
            Gene for single variant call
    ''' 
    format_split=[]
    format_seg = Lines.split(",")
    for seg in format_seg:
        format_split.append(seg.split("|"))
    Fields = header.split("|")
    label="Gene"
    gene=''
    if label in Fields:
        index_to_pick=Fields.index(label)
        for split in format_split:
            if split[Fields.index('PICK')] == '1':
                gene=split[index_to_pick-1]
                break
            elif split[Fields.index('CANONICAL')] == 'YES':
                gene=split[index_to_pick-1]
                break
            elif split[Fields.index('SYMBOL')] == 'MODIFIER':
                modifier=Fields.index('MODIFIER')
                gene=split[modifier+1]
    return gene

def read_gzip_file(file):
    ''' Returns list of gene for variants called within the vcf file
        Args:
            file : VCF file 
        Return:
            Gene list
    ''' 
    if not(file.endswith('gz')):
        raise IOError('vcf file required in gzip format')
    with gzip.open(file, 'rb') as f:
        Lines = f.readlines()

    threshold_count=10000000001 # Very large number
    data=[]
    gene_list=[]
    for count,line in enumerate(Lines):
        line_sep=re.split(r'\t+', line.decode('utf-8'))
        sp= line_sep[0].split(",")
        if '#CHROM' in line_sep:
            threshold_count=count
        elif '##INFO=<ID=CSQ' in sp:
               CSQ_header=sp[3] 
        elif count > threshold_count:
            gene_list.append(extract_format_fields_vcf(line_sep[7],CSQ_header))
            data.append(line_sep)
    return(gene_list)              