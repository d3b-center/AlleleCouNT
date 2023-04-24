#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
id: run_LOH_app
doc: This CWL workflow assesses the loss of heterozygosity (LOH) in the tumor for rare germline variants. Order of operations- This workflow runs bcftools to extract data and prepare list of locations from vcf and feed it into bam-readcount to compute VAF and later parse, merge germline and tumor data together. Github- https://github.com/d3b-center/tumor-loh-app-dev

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
  output_file: { type: File, doc: output file from LOH app, outputSource: run_readcount_parser/loh_output_file_tool }

steps:
  run_gene_extract_list_prepare:
    run: ../tools/run_gene_extract_list_prepare.cwl
    in:
      bs_id: BS_ID
      sample_vcf_file_tool: sample_vcf_file
      frequency_tool: frequency
      peddy_file_tool: peddy_file
      ram: ram_germline
    out:
      [ output_file_1_tool,output_file_2_tool,log_output]
  run_readcount_parser:
    run: ../tools/run_readcount_parser.cwl
    in:
      participant_id: participant_id
      germline_file: run_gene_extract_list_prepare/output_file_1_tool
      list_dir: run_gene_extract_list_prepare/output_file_2_tool
      minDepth: minDepth
      reference: reference
      patientbamcrams : bamscrams
      peddy: peddy_file
      bamcramsampleID: bamcramsampleIDs
      ram: ram_tumor
      minCore: minCore
    out:
      [ loh_output_file_tool,log_output ]