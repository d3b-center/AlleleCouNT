class: CommandLineTool
cwlVersion: v1.2

requirements:
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: "pgc-images.sbgenomics.com/d3b-bixu/loh:1.0.0"
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 16000
  - class: InitialWorkDirRequirement
    listing:
       - entryname: run_python.py
         entry:
           $include: ../scripts/run.py
       - entryname: format_parser.py
         entry:
           $include: ../scripts/format_parser.py  
baseCommand: [ python3 ]

arguments:
  - position: 1
    shellQuote: false
    valueFrom: >- 
        run_python.py	

inputs:
  sample_vcf_file_tool: {type: 'File', inputBinding: {prefix: -i, position: 2}, doc: "VCF file for the sample"}
  BS_ID: {type: string, inputBinding: {prefix: -id, position: 2}, doc: "Sample ID"}
  tsv_file: {type: 'File', inputBinding: {prefix: -I, position: 2}, doc: "tsv file from bcftool"}
  cram_file: {type: 'File',secondaryFiles: [.crai], inputBinding: {prefix: -c, position: 2}, doc: "VCF file for the sample"} 
  Reference: {type: 'File', inputBinding: {prefix: -r, position: 2}, doc: "VCF file for the sample"}
  output: {type: string, inputBinding: {prefix: -o, position: 2}, doc: "Output file"}

outputs:
  output_file:
    type: 'File?'
    outputBinding:
       glob: $(inputs.output).tsv
    doc: "Required file with VAF and Lost VAF"
