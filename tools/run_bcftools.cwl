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
  - entryname: run_bcftools.sh
    entry:
      $include: ../scripts/run_bcftools.sh

inputs:
  sample_vcf_file_tool:
    doc: Sample VCF file
    type: File
    inputBinding:
      position: 1

outputs:
  tmp_file:
    doc: Extract variant info using bcftool in tsv format
    type: File
    outputBinding:
      glob: tmp_file.tsv

baseCommand:
- sh
arguments:
- position: 1
  valueFrom: >-
    run_bcftools.sh	
  shellQuote: false
