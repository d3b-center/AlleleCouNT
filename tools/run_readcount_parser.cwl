#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
id: run_readcount_parser
doc: parser the bam-readcount output and extract inner join between data from vcf (germline) and cram/bam file (tumor)
requirements:
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: pgc-images.sbgenomics.com/d3b-bixu/loh:1.0.0
- class: ResourceRequirement
  coresMin: 1
  ramMin: 4000
- class: InitialWorkDirRequirement
  listing:
  - entryname: run_readcount_parse.py
    entry:
      $include: ../scripts/run_readcount_parse.py
baseCommand: [ python3 ]
arguments:
- position: 1
  valueFrom: >-
    run_readcount_parse.py
  shellQuote: false      

inputs: 
  bs_id: { doc: provide sample id, type: string, inputBinding: { prefix: --sampleid, position: 2} }
  tsv_file: { doc: provide tsv file from bcftool, type: File, inputBinding: { prefix: --tsv, position: 2 } }
  bam_readcount_output: { doc: output file after running bam-readcount tool , type: File, inputBinding: { prefix: --bam_readcount_output, position: 2 } }
  minDepth: { doc: provide minDepth to consider for tumor reads, type: string, inputBinding: { prefix: --minDepth, position: 2} } 
outputs:
   loh_output_file_tool:
    type: File
    outputBinding:
     glob: $(inputs.bs_id)*
    doc: output file required from LOH app