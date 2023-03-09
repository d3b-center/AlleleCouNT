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
  list: { doc: list with position to run within crams using bamreadcount , type: File, inputBinding: { prefix: --list, position: 2 } }
  minDepth: { doc: provide minDepth to consider for tumor reads, type: int, default: 1, inputBinding: { prefix: --minDepth, position: 2} } 
  reference: { doc: provide reference, type: File, secondaryFiles: [ .fai ], inputBinding: { prefix: --reference, position: 2} } 
  patientbamcram: { doc: provide patient bam/cram file, type: File, secondaryFiles: [ { pattern: ".crai", required: false } ,{ pattern: ".bai",required: false } ], inputBinding: { prefix: --patientbamcram, position: 2} } 
  paternalbamcram: { doc: provide paternal bam/cram file, type: 'File?', secondaryFiles: [ { pattern: ".crai", required: false } ,{ pattern: ".bai",required: false } ], inputBinding: { prefix: --paternalbamcram, position: 2} } 
  maternalbamcram: { doc: provide maternal bam/cram file, type: 'File?',secondaryFiles: [ { pattern: ".crai", required: false } ,{ pattern: ".bai",required: false } ], inputBinding: { prefix: --maternalbamcram, position: 2} } 
  peddy:  { doc: provide patient peddy file, type: 'File?', inputBinding: { prefix: --peddy, position: 2} } 
outputs:
   loh_output_file_tool:
    type: File
    outputBinding:
     glob: $(inputs.bs_id)*.loh.out.tsv
    doc: output file required from LOH app