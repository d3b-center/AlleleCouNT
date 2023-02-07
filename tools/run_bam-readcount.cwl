#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
id: run_bam-readcount
doc: runs bam-readcount to read cram/bam file for the positions given in the list and generate ouput for parsing further
requirements:
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: pgc-images.sbgenomics.com/d3b-bixu/loh:1.0.0
- class: ResourceRequirement
  coresMin: 1
  ramMin: 4000
- class: InitialWorkDirRequirement
  listing:
  - entryname: run_bam-readcount.sh
    entry:
      $include: ../scripts/run_bam-readcount.sh
baseCommand: [ "sh" ]
arguments:
- position: 1
  valueFrom: >-
    run_bam-readcount.sh	
  shellQuote: false
inputs:
  cram_bam_file: { type: File, secondaryFiles: [ { pattern: ".crai", required: false } ,{ pattern: ".bai",required: false } ],doc: provide sample cram or bam file with index file, inputBinding: { position: 1 } }
  ref_file: { type: File, secondaryFiles: [.fai ], doc: human reference in fasta format with index file, inputBinding: { position: 2 } }  
  list_file: { type: File, doc: list containing chr start and end to run bam-readcount tool for specific regions , inputBinding: { position: 3 }}
outputs:
  readcount_file:
    type: 'File'
    outputBinding:
      glob: "output_readcount.out"
    doc: raw bam-readcount output that requires parsing