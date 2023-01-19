#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
id: run_bcftools
doc: runs bcftools to pull out required details from vcf file
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
baseCommand: [ sh ]
arguments:
- position: 1
  valueFrom: >-
    run_bcftools.sh	
  shellQuote: false
inputs:
  sample_vcf_file_tool: { type: File, doc: provide sample VCF file in gz format, inputBinding: { position: 1 } }

outputs:
  tmp_file:
    type: File
    outputBinding:
      glob: tmp_file.tsv
    doc: variant info using bcftool in tsv format