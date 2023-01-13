#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

requirements:
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: pgc-images.sbgenomics.com/d3b-bixu/loh:1.0.0
- class: ResourceRequirement
  coresMin: 1
  ramMin: 4000
- class: InitialWorkDirRequirement
  listing:
  - entryname: run_python.py
    entry:
      $include: ../scripts/run_pysam.py
  - entryname: format_parser.py
    entry:
      $include: ../scripts/format_parser.py

inputs:
  BS_ID:
    doc: Sample ID
    type: string
    inputBinding:
      prefix: -id
      position: 2
  Reference:
    doc: VCF file for the sample
    type: File
    inputBinding:
      prefix: -r
      position: 2
  cram_file:
    doc: VCF file for the sample
    type: File
    secondaryFiles:
    - .crai
    inputBinding:
      prefix: -c
      position: 2
  output:
    doc: Output file
    type: string
    inputBinding:
      prefix: -o
      position: 2
  sample_vcf_file_tool:
    doc: VCF file for the sample
    type: File
    inputBinding:
      prefix: -i
      position: 2
  tsv_file:
    doc: tsv file from bcftool
    type: File
    inputBinding:
      prefix: -I
      position: 2

outputs:
  output_file:
    doc: Required file with VAF and Lost VAF
    type: File
    outputBinding:
      glob: $(inputs.output).tsv

baseCommand:
- python3
arguments:
- position: 1
  valueFrom: >-
    run_python.py	
  shellQuote: false
