#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
doc: |-
  This workflow runs bcftools to extract data from vcf and feed it into pysam to compute lost VAF

requirements:
- class: StepInputExpressionRequirement

inputs:
  BS_ID:
    doc: Sample ID
    type: string
  Reference:
    doc: Human reference in Fasta format
    type: File
  cram_file:
    doc: Tumor input cram file
    type: File
  output:
    doc: Output file name
    type: string
  sample_vcf_file:
    doc: Input germline file for the sample
    type: File

outputs:
  output_file:
    type: File
    outputSource: run_pysam/output_file

steps:
  run_bcftools:
    in:
      sample_vcf_file_tool: sample_vcf_file
    run: ../tools/run_bcftools.cwl
    out:
    - tmp_file
  run_pysam:
    in:
      BS_ID: BS_ID
      Reference: Reference
      cram_file: cram_file
      output: output
      sample_vcf_file_tool: sample_vcf_file
      tsv_file: run_bcftools/tmp_file
    run: ../tools/run_pysam.cwl
    out:
    - output_file
id: run_LOH_app
