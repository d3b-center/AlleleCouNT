# Kids First Loss of Heterozygosity (LOH)

![data service logo](https://github.com/d3b-center/d3b-research-workflows/raw/master/doc/kfdrc-logo-sm.png)

Preprocessing LOH assesses the loss of heterozygosity (LOH) in the tumor for rare germline variants. 
Order of operations: This workflow runs bcftools to extract data and prepare list of locations from vcf provided and feed it into bam-readcount to compute VAF and later parse, merge germline and tumor data together. 

## Inputs

- BS_ID : Sample id for proband
- frequency: cut off for rare germline variants based on gnomad_3_1_1_AF_popmax tag
- ram_germline : provide ram for germline tool which is directly related with size of VCF file provide in sample_vcf_file
- peddy_file: details about the family trio
- participant_id: provide participant_id for proband. It is used just to name the output file.
- bamscrams: provide multiple bam/cram files for proband and family trios 
- reference: human reference file in fasta format
- sample_vcf_file: vcf file to exact germline calls
- minDepth: minimum depth of the reads that should be considered in the tunor analysis
- bamcramsampleIDs: provide bam/cram sampleids in the same order as provided in bamscrams. 
- ram_tumor: ram for tumor tool, which is strongly connected with the size of the cram files and number of cram files provided 
- mincore: provide number of processor. Each cram will be split into 32 parts for multiprocessing and results will be merge back. High number of processors are recommended. 

## Output

- output_file: a tsv file with mapped variant data from germline and tumor tool containing germline VAF and tumor VAF

## Demo Proband-only Cavatica Task

![LOH schematic](https://github.com/d3b-center/tumor-loh-app-dev/blob/master/docs/logo/proband_run.png)

## Demo Family-trio Cavatica Task

![LOH schematic](https://github.com/d3b-center/tumor-loh-app-dev/blob/master/docs/logo/proband_run.png)