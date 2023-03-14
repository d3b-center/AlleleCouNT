#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
id: run_readcount_parser
doc: parser the bam-readcount output and extract inner join between data from vcf (germline) and cram/bam file (tumor)
requirements:
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: pgc-images.sbgenomics.com/d3b-bixu/loh:1.0.1
- class: ResourceRequirement
  coresMin: 16
  ramMin: 32000
- class: InitialWorkDirRequirement
  listing:
   - entryname: run_readcount_parse.py
     entry:
      $include: ../scripts/run_readcount_parse.py
   - entryname: tmp_list
     entry: $(inputs.list_dir) 
     writable: true
   - entryname: format_parser.py
     entry:
      $include: ../scripts/format_parser.py 
      
baseCommand: [ python3 ]
arguments:
- position: 1
  valueFrom: >-
    run_readcount_parse.py
  shellQuote: false      

inputs: 
  bs_id: { doc: provide sample id, type: string, inputBinding: { prefix: --sampleid, position: 2} }
  germline_file: { doc: provide tsv file from bcftool, type: File, inputBinding: { prefix: --tsv, position: 2 } }
  list_dir: { doc: list with position to run within crams using bamreadcount , type: Directory, inputBinding: { prefix: --list, position: 2 } }
  minDepth: { doc: provide minDepth to consider for tumor reads, type: int, default: 1, inputBinding: { prefix: --minDepth, position: 2} } 
  reference: { doc: provide reference, type: File, secondaryFiles: [ .fai ], inputBinding: { prefix: --reference, position: 2} } 
  patientbamcrams: { doc: provide patient bam/cram file, type: 'File[]', secondaryFiles: [ { pattern: ".crai", required: false } ,{ pattern: ".bai",required: false } ], inputBinding: { prefix: --patientbamcrams, position: 2} } 
  peddy:  { doc: provide patient peddy file, type: 'File?', inputBinding: { prefix: --peddy, position: 2} } 
  bamcramsampleID:  { doc: provide sample ID for cram/ bam files, type: 'string[]?', inputBinding: { prefix: --bamcramsampleID, position: 2} } 
outputs:
   loh_output_file_tool:
    type: File
    outputBinding:
     glob: $(inputs.bs_id)*loh.out.tsv
    doc: output file required from LOH app