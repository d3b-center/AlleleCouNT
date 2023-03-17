# Loss of Heterozygosity (LOH)

This CWL workflow assesses the loss of heterozygosity (LOH) in the tumor for rare germline variants (gnomad_3_1_1_AF_popmax < 0.01).

### Repo Description

This workflow is divided into two parts: 1) Germline tool and tumor tool

Here are the basic steps for the LOH assessment workflow:

* Filter germline annotations to retain variants with gnomad_3_1_1_AF_popmax < 0.01 performed by the germline tool (this gets us rare germline variants).
* Gather variant information (gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, VAF) covered by the germline tool.
* Search in a paired tumor sample (example match to above germline) and, if applicable, parental germline samples, for the same variant and calculate the VAF covered by tumor tool
* Create an output file with (BS_id, gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, VAF) for each of: proband germline, proband tumor, paternal germline, maternal germline covered by the tumor tool

(Optional) This workflow has the ability to analyze LOH for trios too. The input requirement for trios is a trio vcf, a peddy file, and a tumor cram file for the proband. Note: The user can provide multiple cram or bam files as per the need.

### Run it locally

It is recommended to run this workflow on a system with high number of CPUs and memory (>=16 GB). Basic requirment is a running docker engine, and CWL tools. Here is the command line to run it locally:

```
cwltool workflow/run_LOH_app.cwl sample_input.yml
```
Inputs to the workflow need to be defined in input_workflow.yml