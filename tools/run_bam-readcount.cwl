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

baseCommand: [ "bam-readcount" ]

arguments: ["-w1"]

inputs:
  cram_bam_file: { type: File, secondaryFiles: [ { pattern: ".crai", required: false } ,{ pattern: ".bai",required: false } ],doc: provide sample cram or bam file with index file, inputBinding: { position: 3 } }
  ref_file: { type: File, secondaryFiles: [.fai ], doc: human reference in fasta format with index file, inputBinding: { prefix: -f, position: 2 } }  
  list_file: { type: File, doc: list containing chr start and end to run bam-readcount tool for specific regions , inputBinding: { prefix: -l, position: 4 }}

stdout: "output_readcount.out"

outputs:
  readcount_file:
    type: stdout
    doc: raw bam-readcount output that requires parsing