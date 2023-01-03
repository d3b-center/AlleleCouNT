import re
import gzip
import argparse

def extract_format_fields_vcf(Lines,header):
    format_split=[]
    format_seg = Lines.split(",")
    for seg in format_seg:
        format_split.append(seg.split("|"))
    Fields = header.split("|")
    label="Gene"
    gene=''
   
    if label in Fields:
        index_to_pick=Fields.index(label)
        #print(format_split[Fields.index('PICK')]=='1')
        for split in format_split:
          #  print(split[Fields.index('CANONICAL')])
          #  print(split[Fields.index('TSL')])
            if split[Fields.index('PICK')] == '1':
                gene=split[index_to_pick-1]
                break
            elif split[Fields.index('CANONICAL')] == 'YES':
                gene=split[index_to_pick-1]
                break
       #     return_data.append(format_split[index_to_pick])
            elif split[Fields.index('SYMBOL')] == 'MODIFIER':
                modifier=Fields.index('MODIFIER')
                gene=split[modifier+1]
    
   # variant=[]
   # gene=[]
   # for index in range(0,len(x),1):
   #     if x[index] =='MODIFIER':
    #        if "&" not in x[index-1]:
     #           a=[x[index-1],x[index+1]]
      #          variant.append(a[0])
       #         gene.append(a[1])
        #    else:
         ###     for v in b:
         #           variant.append(v)    
                #a=[b,x[index+1]]
    #return(set(variant),set(gene))
    #print(return_data)
   # if gene == '':
   #     print(Lines)
    return gene
def read_gzip_file(file):
    #file_cut=2200000
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
        #else:
        #    sp= line_sep[0].split(",")
        #    if '##INFO=<ID=CSQ' in sp:
        #       CSQ_header=sp[3]   
    return(gene_list)              

#parser = argparse.ArgumentParser()
# Adding optional argument
#parser.add_argument("-i", "--Input", help = "Give input")
# Read arguments from command line
#args = parser.parse_args()            
#read_gzip_file(args.Input)