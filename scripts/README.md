### Germline tool

Germline tool filters germline annotations to retain variants with gnomad_3_1_1_AF_popmax < 0.01(this gets us rare germline variants) and gathers variant information (gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, VAF).

#### usage
```

python3 run_gene_extract_list_prepare.py --help
usage: run_gene_extract_list_prepare.py [-h] [-i INPUT] [-id SAMPLEID] [-freq FREQUENCY] [-ped PEDDY]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        provide sample vcf file
  -id SAMPLEID, --sampleid SAMPLEID
                        provide sample ID
  -freq FREQUENCY, --frequency FREQUENCY
                        Frequency cutoff for popmax
  -ped PEDDY, --peddy PEDDY
                        Peddy file

```

### Tumor tool

Tumor tool search in a paired tumor sample (example match to above germline) and, if given, parental germline samples, for the same variant and calculate the VAF and creates an output file with (BS_id, gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, VAF) for each of: proband germline, proband tumor, paternal germline, maternal germline

(Optional) This tool has the ability to analyze LOH for trios too with multiple tumor samples.

```
python3 run_readcount_parse.py --help
usage: run_readcount_parse.py [-h] [--tsv TSV] [--sampleid SAMPLEID] [--reference REFERENCE]
                              [--patientbamcrams PATIENTBAMCRAMS [PATIENTBAMCRAMS ...]] [--list LIST] [--peddy PEDDY]
                              [--minDepth MINDEPTH] [--bamcramsampleID BAMCRAMSAMPLEID [BAMCRAMSAMPLEID ...]]

optional arguments:
  -h, --help            show this help message and exit
  --tsv TSV             bcftool output file in tsv format
  --sampleid SAMPLEID   patient primary sampleid for this run
  --reference REFERENCE
                        human reference
  --patientbamcrams PATIENTBAMCRAMS [PATIENTBAMCRAMS ...]
                        provide one or more bam/cram file for patient tumor
  --list LIST           path to directory containing regions created by germline run to consider in tumor
  --peddy PEDDY         peddy file containing parental information
  --minDepth MINDEPTH   min tumor depth required to be consider for tumor output
  --bamcramsampleID BAMCRAMSAMPLEID [BAMCRAMSAMPLEID ...]
                        array of sample IDs provided for cram/bam files in the same order as input cram/bam files
```