# D3B:Loss of Heterozygosity (LOH)

LOH CWL workflow assesses the loss of heterozygosity(LOH) in the tumor for rare germline variants (gnomad_3_1_1_AF_popmax < 0.01).

### Repo Description


This workflow is divided into two tools: Germline tool and tumor tool.


Here are the basic steps for the LOH assessment workflow:

* Filter germline annotations to retain variants with gnomad_3_1_1_AF_popmax < 0.01 or gnomad_3_1_1_AF_popmax not defined performed by the germline tool (this gets us rare germline variants).
* Gather variant information (gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, VAF) covered by the germline tool.
* Search in a paired tumor sample (example match to above germline) and, if applicable, parental germline samples, for the same variant and calculate the VAF covered by tumor tool.
* LOH will create an output file with headers (BS_id, gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, VAF) for each of: proband germline, proband tumor, paternal germline, maternal germline covered by the tumor tool.


(Optional) This workflow has the ability to analyze LOH for trios, with multiple tumor samples. The input requirement for trios is a trio vcf, a peddy file, and a tumor cram file for the proband. Note: The user can provide multiple.cram or.bam files as needed.

### Cavatica Application

This workflow has been deployed on [cavatica](https://cavatica.sbgenomics.com/u/d3b-bixu/tumor-loh-dev/apps/Loss_of_Heterozygosity) with a [test run](https://cavatica.sbgenomics.com/u/d3b-bixu/tumor-loh-dev/tasks/89708628-085f-40ce-a15b-2d850d81eead/)

### Running it locally on a laptop?


It is recommended to run this workflow on a system with a high number of CPUs and memory (>=16 GB). The basic requirement is a running Docker engine and CWL tools. Here is the command line to run the LOH workflow locally:


```
cwltool workflow/run_LOH_app.cwl sample_input.yml
```
Note: Inputs to the workflow need to be defined in sample_input.yml.