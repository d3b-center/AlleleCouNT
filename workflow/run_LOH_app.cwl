#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
id: run_LOH_app
doc: This workflow runs bcftools to extract data and prepare list of locations from vcf and feed it into bam-readcount to compute VAF and later parse, merge germline and tumor data together

requirements:
- class: StepInputExpressionRequirement

inputs:
  BS_ID: {doc: provide sample id,type: string }
  frequency: { doc: provide popmax cutoff, type: float }
  peddy_file: { doc: Provide ped file for the trios, type: 'File?' }
  bam_cram_file: { doc: tumor input file in cram or bam format with their index file, type: 'File[]' , secondaryFiles: [ { pattern: ".crai", required: false }, { pattern: ".bai", required: false } ] }
  minDepth: { doc: provide minimum tumor depth to consider, type: int }
  reference: { doc: human reference in fasta format with index file, type: File,secondaryFiles: [ .fai ] }
  sample_vcf_file: { doc: provide germline vcf file for this sample, type: File }
  bamcramsampleIDs: { doc: provide germline vcf file for this sample, type: 'string[]?' }

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
    out:
      [ output_file_1_tool,output_file_2_tool]
  run_readcount_parser:
    run: ../tools/run_readcount_parser.cwl
    in:
      bs_id: BS_ID
      germline_file: run_gene_extract_list_prepare/output_file_1_tool
      list_dir: run_gene_extract_list_prepare/output_file_2_tool
      minDepth: minDepth
      reference: reference
      patientbamcrams : bam_cram_file
      peddy: peddy_file
      bamcramsampleID: bamcramsampleIDs
    out:
      [ loh_output_file_tool ]