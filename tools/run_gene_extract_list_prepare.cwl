#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool
id: run_gene_extract_list_prepare
label: run_germline
doc: collects info from bcftool and add gene, prepare directory of list for bam-readcount tool
requirements:
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: pgc-images.sbgenomics.com/d3b-bixu/loh:1.0.1
- class: InlineJavascriptRequirement  
- class: ResourceRequirement
  coresMin: 8
  ramMin: ${ return inputs.ram * 1000 } 
- class: InitialWorkDirRequirement
  listing:
  - entryname: run_gene_extract_list_prepare.py
    entry:
      $include: ../scripts/run_gene_extract_list_prepare.py
  - entryname: format_parser.py
    entry:
      $include: ../scripts/format_parser.py
baseCommand: [ python3 ]
arguments:
- position: 1
  valueFrom: >-
    run_gene_extract_list_prepare.py	
  shellQuote: false      

inputs: 
  bs_id: { doc: provide sample id, type: string, inputBinding: { prefix: --sampleid, position: 2} }
  sample_vcf_file_tool: { doc: provide vcf file for germline, type: File, inputBinding: { prefix: --input, position: 2 }  }
  frequency_tool: { doc: provide popmax cutoff for rare disease, type: float, inputBinding: { prefix: --frequency, position: 2 }  }
  peddy_file_tool: { doc: provide ped file for the trios, type: 'File?', inputBinding: { prefix: --peddy, position: 2 } }
  ram: { doc: provide ram (in GB) based on number of crams files, type: 'int?', default: 16 } 

outputs:
   output_file_1_tool:
    type: File
    outputBinding:
     glob: $(inputs.bs_id)*.germline.output.tsv
    doc: output file with VAF from germline
   output_file_2_tool:
    type: Directory
    outputBinding:
      glob: "tmp_list"
    doc: directory containing region lists to run on tumor as an input to bam-readcount
   log_output:
    type: File
    outputBinding:
     glob: "*loh.log"
    doc: output file with VAF from germline