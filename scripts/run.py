import argparse
import subprocess
import pandas as pd
import pysam
import format_parser as object

# coding=utf8
# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-i", "--Input", help = "Provide sample vcf file in gz format")

parser.add_argument("-I", "--tsv", help = "Provide bcftools output in tsv format")

parser.add_argument("-c", "--cram", help = "Provide cram file for the sample")

parser.add_argument("-r", "--ref", help = "Provide human reference in fasta format")

parser.add_argument("-id", "--Sample", help = "Provide Sample ID")

parser.add_argument("-o", "--output", help = "Output file name in tsv format")

# Read arguments from command line
args = parser.parse_args()

def get_VAF_pos(cram_path, chrom, pos,ref, alt, reference=None):
    """ Return VAF at a pos for an alt
        Args:
            cram_path (str): path to CRAM or BAM file
            chrom (str): locus chromosome name
            pos (int): 1-based locus coordinate
            reference: path to reference FASTA, required for CRAM
                (default None)
        Raises:
            IOError if CRAM provided without reference
                    if cram_path has neither cram nor bam extension
        Return:
            VAF for required Allele at the position given
    """
    if len(ref) >1 or len(alt) >1 : # excluding indels
        return("Indels are ignored at the moment")
    if cram_path.endswith('cram'):
        if not reference:
            raise IOError('Must provide reference with CRAM')
        cram = pysam.AlignmentFile(cram_path, 'rc', reference_filename=reference)
    elif cram_path.endswith('bam'):
        cram = pysam.AlignmentFile(cram_path, 'rb')
    else:
        raise IOError('File provided to "cram" argument must have .cram or .bam extension')

    mapq = []
    mq0 = 0
    aligned_reads = cram.fetch(chrom, pos-1, pos,multiple_iterators=False)
    total_reads=0
    count_required=0
    for read in aligned_reads:
        start=read.pos # read start position
        diff=pos-start #difference between start and pos
        seq=read.query_sequence
        if len(seq)>diff:
            if seq[diff-1] == alt:
                count_required=+1
            total_reads+=1 
    if total_reads == 0:
        return("No read found")
    else:          
        return(round(count_required/total_reads,4))

#extract gene list from vcf file
gene=object.read_gzip_file(args.Input) 
del gene[-1]

#read tsv file from bcftools 
df = pd.read_csv(args.tsv,sep = '\t')

#set up pandas dataframe
df.columns=["popmax","chr", "start", "stop", "ref","alt", "ref,alt depth", "Total depth", "VAF"]
df['gene']= gene
df = df[["gene","popmax","chr", "start", "stop", "ref","alt", "ref,alt depth", "Total depth", "VAF"]]

#remove entries with . as popmax
df=df[df.popmax != "."]
df['popmax'] = df['popmax'].astype(float)

#set criteria for rare variant
df=df[df.popmax < 0.01]
df=df.drop(['popmax'], axis=1)

list_VAF=[]

#run the for loop to calculate lost VAF
for index, row in df.iterrows():
    #print(row['chr'], row['start'])
    list_VAF.append(get_VAF_pos(args.cram,row['chr'],row['start'],row['ref'],row['alt'],args.ref))
df["Lost_VAF"]=list_VAF
df["BS_ID"]=args.Sample

#reorder the columns
df = df[["BS_ID","gene","chr", "start", "stop", "ref","alt", "ref,alt depth", "Total depth", "VAF","Lost_VAF"]]

#output_file in tsv format
output_file_name=(args.output)+".tsv"
df.to_csv(output_file_name, sep="\t",index=False)