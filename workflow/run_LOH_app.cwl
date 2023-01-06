cwlVersion: v1.2
class: Workflow
id: LOH

requirements:
- class: StepInputExpressionRequirement

inputs:
  sample_vcf_file: {type: 'File', doc: "Input germline file for the sample"}
  BS_ID: {type: string, doc: "Sample ID"}
  output: {type: string, doc: "Output file name"}
  cram_file: {type: 'File', doc: "Tumor input cram file"}
  Reference: {type: 'File', doc: "Human reference"}

outputs:
  output_file: {type: 'File?', outputSource: pysam/output_file}

steps:

   bcftool:
    run: ../tools/run_bcftools.cwl
    in:
      sample_vcf_file_tool: sample_vcf_file
    out: [tmp_file]

   pysam:
    run: ../tools/run.cwl
    in:
      sample_vcf_file_tool: sample_vcf_file
      tsv_file: bcftool/tmp_file
      cram_file: cram_file
      Reference: Reference
      BS_ID: BS_ID
      output: output
    out: [output_file]