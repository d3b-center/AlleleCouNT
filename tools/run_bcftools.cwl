class: CommandLineTool
cwlVersion: v1.2

requirements:
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: "pgc-images.sbgenomics.com/d3b-bixu/loh:1.0.0"
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 4096
  - class: InitialWorkDirRequirement
    listing:
       - entryname: run_bcftools
         entry:
           $include: ../scripts/run_bcftools.sh
baseCommand: [ sh ]
#stdout: "montage.out"
#stderr: "montage.err"
arguments:
  - position: 1
    shellQuote: false
    valueFrom: >- 
        run_bcftools	

inputs:
    sample_vcf_file_tool:
     type: 'File'
     inputBinding:
       position: 1 
     doc: "Sample VCF file"  

#    test: {type: 'File?', inputBinding: {prefix: --test, position: 2}, doc: "Gene level CNV file"}

outputs:
  tmp_file:
    type: 'File?'
    outputBinding:
       glob: tmp_file.tsv  
    doc: "Extract variant info using bcftool in tsv format"