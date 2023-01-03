cwlVersion: v1.2
class: Workflow
id: LOH

requirements:
- class: ScatterFeatureRequirement
- class: MultipleInputFeatureRequirement
- class: StepInputExpressionRequirement
- class: SubworkflowFeatureRequirement
- class: InlineJavascriptRequirement

inputs:
  sample_vcf_file: {type: 'File', doc: "Input histology file"}
  BS_ID: {type: string, doc: "C"}
  output: {type: string, doc: "C"}
  vcf: {type: 'File', doc: "Input histology file"}
 # tsv_file: {type: 'File', doc: "Input histology file"}
  cram_file: {type: 'File', doc: "Input histology file"}
  REF: {type: 'File', doc: "Input histology file"}

outputs:
#  tmp_file: {type: File, outputSource: bcftool/tmp_file}
  output_file: {type: File, outputSource: pysam/output_file}

steps:

   bcftool:
    run: ../tools/run_bcftools.cwl
    in:
      sample_vcf_file_tool: sample_vcf_file
    out: [tmp_file]

   pysam:
    run: ../tools/run.cwl
    in:
      vcf: vcf
      tsv_file: bcftool/tmp_file
      cram_file: cram_file
      REF: REF
      BS_ID: BS_ID
      output: output
    out: [output_file]