#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
id: kf-loss-of-heterozygosity-preprocessing
label: Kids First Loss of Heterozygosity
doc: | 
 # Kids First Loss of Heterozygosity (LOH)

  ![data service logo](https://github.com/d3b-center/d3b-research-workflows/raw/master/doc/kfdrc-logo-sm.png)

  The Kids First Loss of Heterozygosity Preprocessing (aka LOH) is a CWL workflow that assesses the loss of heterozygosity in the tumor for rare germline calls filtered by gnomad_3_1_1_AF_popmax (typically < 0.01) or when gnomad_3_1_1_AF_popmax is not defined. This preprocessing is designed to compute variant allele frequency (VAF) for multiple proband tumor samples and can also map germline VAF for family trios if trio germline VCF file is provided.
  
  #### Basic info
  - Dockerfile: https://github.com/d3b-center/bixtools/tree/master/LOH/1.0.1
  - tested with
    - Seven Bridges Cavatica Platform: https://cavatica.sbgenomics.com/
    - cwltool: https://github.com/common-workflow-language/cwltool/releases/tag/3.1.20221201130942

  ### Description

  The Kids First Loss of Heterozygosity application is divided into two tools: Germline tool and Tumor tool.

  #### Germline Tool

  Germline tool filters germline annotations to retain variants based on gnomad_3_1_1_AF_popmax (typically < 0.01) or when gnomad_3_1_1_AF_popmax is not defined. It requires vcf file, proband sample id, ram as required inputs and peddy file as optional input which is required for family trios. It outputs variant information such as gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, variant allele frequency and list of coordinates that will be an input to tumor tool.

  #### Tumor Tool
  Tumor tool search in paired proband tumor sample for aligned reads in the regions where rare variants from the germline tool exists and exact allele/reference count, allele/reference depth and calculate the variant allele frequency VAF. Tumor tool have the capability to search multiple tumor samples for proband and if applicable, parental and maternal tumor samples. To exact reads from the bam/cram files, this tool utilizes [bam-readcount](https://github.com/genome/bam-readcount) and wraps it with python script to shape the output in a tabular format. 

  ### LOH Inputs
  ```
  Germline tool
    # Required  
    BS_ID: { doc: provide BS id for germline normal,type: string }
    frequency: { doc: provide popmax cutoff for rare germline variants, type: 'float?', default: 0.01 }
    # Optional
    ram_germline: {  doc: Provide ram (in GB) based on the size of vcf,type: 'int?', default: 8}
    # Required for family trios otherwise not required
    peddy_file: { doc: provide ped file for the trio, type: 'File?' }
  Tumor tool
    # Required
    participant_id: { doc: provide participant id for this run, type: string }
    bamscrams: { doc: tumor input file in cram or bam format with their index file, type: 'File[]' , secondaryFiles: [ { pattern: ".crai", required: false }, { pattern: ".bai", required: false } ] }
    reference: { doc: human reference in fasta format with index file, type: File, secondaryFiles: [ .fai ], "sbg:suggestedValue": { class: File, path: 60639014357c3a53540ca7a3, name: Homo_sapiens_assembly38.fasta, secondaryFiles: [{class: File, path: 60639016357c3a53540ca7af, name: Homo_sapiens_assembly38.fasta.fai}]} }
    sample_vcf_file: { doc: provide germline vcf file for this sample, type: File }
    # Optional
    minDepth: { doc: provide minDepth to consider for tumor reads, type: 'int?', default: 1 }
    bamcramsampleIDs: { doc: provide unique identifers (in the same order) for cram/bam files provided under bamcrams tag. Default is sample ID pulled from bam/cram files., type: 'string[]?' }
    ram_tumor: {  doc: Provide ram (in GB) for tumor tool based on the number cram/bam inputs, type: 'int?', default: 16} 
    minCore: { type: 'int?', default: 16, doc: "Minimum number of cores for tumor tool based on the number cram/bam inputs" }
  ```

  ### LOH Output

  LOH application will output a tab-separated values file mapped data from germline tool and tumor tool. 
  ```
  output_file: { type: File, doc: A tsv file with gathered data from germline and tumor tool}
  ```

requirements:
- class: StepInputExpressionRequirement

inputs:
  BS_ID: { doc: provide BS id for germline normal,type: string }
  participant_id: { doc: provide participant id for this run, type: string }
  frequency: { doc: provide popmax cutoff for rare germline variants, type: 'float?', default: 0.01 }
  peddy_file: { doc: provide ped file for the trio, type: 'File?' }
  bamscrams: { doc: tumor input file in cram or bam format with their index file, type: 'File[]' , secondaryFiles: [ { pattern: ".crai", required: false }, { pattern: ".bai", required: false } ] }
  minDepth: { doc: provide minDepth to consider for tumor reads, type: 'int?', default: 1 }
  reference: { doc: human reference in fasta format with index file, type: File,secondaryFiles: [ .fai ] }
  sample_vcf_file: { doc: provide germline vcf file for this sample, type: File }
  bamcramsampleIDs: { doc: provide unique identifers (in the same order) for cram/bam files provided under bamcrams tag. Default is sample ID pulled from bam/cram files., type: 'string[]?' }
  ram_germline: {  doc: Provide ram (in GB) based on the size of vcf,type: 'int?', default: 8} 
  ram_tumor: {  doc: Provide ram (in GB) size and number of cram/bam inputs, type: 'int?', default: 16} 
  minCore: { type: 'int?', default: 16, doc: "Minimum number of cores for tumor tool" }
outputs:
  output_file: { type: File, doc: output file from LOH app, outputSource: run_tumor_tool/loh_output_file_tool }

steps:
  run_germline_tool:
    run: ../tools/run_gene_extract_list_prepare.cwl
    in:
      bs_id: BS_ID
      sample_vcf_file_tool: sample_vcf_file
      frequency_tool: frequency
      peddy_file_tool: peddy_file
      ram: ram_germline
    out:
      [ output_file_1_tool,output_file_2_tool,log_output]
  run_tumor_tool:
    run: ../tools/run_readcount_parser.cwl
    in:
      participant_id: participant_id
      germline_file: run_germline_tool/output_file_1_tool
      list_dir: run_germline_tool/output_file_2_tool
      minDepth: minDepth
      reference: reference
      patientbamcrams : bamscrams
      peddy: peddy_file
      bamcramsampleID: bamcramsampleIDs
      ram: ram_tumor
      minCore: minCore
    out:
      [ loh_output_file_tool,log_output ]
         
"sbg:license": Apache License 2.0
"sbg:publisher": KFDRC
"sbg:categories":
- VAF
- LOH
- WGS
- WXS
- GVCF
- TRIOS
"sbg:links":
- id: 'https://github.com/d3b-center/tumor-loh-app-dev/releases/tag/v1.0.2'
  label: github-release      