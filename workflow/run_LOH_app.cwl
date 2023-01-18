#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
id: run_LOH_app
doc: This workflow runs bcftools to extract data from vcf and feed it into pysam to compute lost VAF

requirements:
- class: StepInputExpressionRequirement

inputs:
  bs_id: {doc: provide sample id,type: string }
  cram_file: { doc: tumor input file in cram or bam format with index file,type: File }
  output: { doc: provide output file name, type: string }
  reference: { doc: human reference in fasta format with index file, type: 'File?' }
  sample_vcf_file: { doc: provide germline file for this sample, type: File }

outputs:
  output_file: { type: File, doc: output file from this app, outputSource: run_pysam/output_file }

steps:
  run_bcftools:
    run: ../tools/run_bcftools.cwl
    in:
      sample_vcf_file_tool: sample_vcf_file
    out: [ tmp_file ]
  run_pysam:
    run: ../tools/run_pysam.cwl
    in:
      bs_id: bs_id
      cram_file: cram_file
      output: output
      reference: reference
      sample_vcf_file_tool: sample_vcf_file
      tsv_file: run_bcftools/tmp_file
    out: [output_file]
