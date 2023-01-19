#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
id: run_pysam
doc: collects info from bcftool and add gene, lost of VAF, total reads from cram, vcf to final output 
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
baseCommand: [ python3 ]
arguments:
- position: 1
  valueFrom: >-
    run_python.py	
  shellQuote: false      

inputs: 
  bs_id: { doc: provide sample id, type: string, inputBinding: { prefix: --sampleid, position: 2} }
  cram_file: { doc: provide cram/bam file for the sample, type: File, secondaryFiles: [.crai], inputBinding: { prefix: --cram, position: 2 } }
  output: { doc: output file name, type: string, inputBinding: { prefix: --output, position: 2 } }
  reference: { doc: provide human reference in fasta format, type: 'File?', secondaryFiles: [.fai ], inputBinding: { prefix: --ref , position: 2 } }
  sample_vcf_file_tool: { doc: provide vcf file, type: File, inputBinding: { prefix: --input, position: 2 }  }
  tsv_file: { doc: tsv file from bcftool , type: File, inputBinding: { prefix: --tsv, position: 2 } }

outputs:
   output_file:
    type: File
    outputBinding:
     glob: $(inputs.output)*
    doc: output file with VAF and Lost VAF