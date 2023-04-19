# D3B:Loss of Heterozygosity (LOH)

This CWL workflow assesses the loss of heterozygosity(LOH) in the tumor for rare germline variants (gnomad_3_1_1_AF_popmax < 0.01). This workflow has been deployed on [cavatica](https://cavatica.sbgenomics.com/u/d3b-bixu/tumor-loh-dev/apps/Loss_of_Heterozygosity) with a [test run](https://cavatica.sbgenomics.com/u/d3b-bixu/tumor-loh-dev/tasks/89708628-085f-40ce-a15b-2d850d81eead/)

### Repo Description

This workflow is divided into two tools: Germline tool and tumor tool.

Here are the basic steps for the LOH assessment workflow:

* Filters germline annotation to retain variants with gnomad_3_1_1_AF_popmax < 0.01 performed by the germline tool (this gets us rare germline variants).
* Gather variant information (gene, chr, start, stop, ref/alt alleles, ref allele depth, alt allele depth, germline_VAFs) covered by the germline tool.
* Search in a paired tumor sample (example match to above germline) and, if applicable, parental germline samples, for the same variant and calculate the VAF covered by tumor tool.
* Create an output file with (BS_id, gene, chr, start, stop, ref alleles, alt alleles, ref allele depth, alt allele depth, VAF) for each of: proband germline, proband tumor, paternal germline, maternal germline covered by the tumor tool.


(Optional) This workflow has the ability to analyze LOH for trios, with multiple tumor samples. The input requirement for family trios is a trio vcf, a peddy file, and a tumor cram file for the proband. Note: The user can provide multiple .cram or.bam files.


### Running it locally on a laptop?


It is recommended to run this workflow on a system with a high number of CPUs and memory (>=16 GB). The basic requirement is a running Docker engine and CWL tools. Here is the command line to run the LOH workflow locally:


```
cwltool workflow/run_LOH_app.cwl sample_input.yml
```
Note: Inputs to the workflow need to be defined in sample_input.yml.

### Output headers

| Header | Description | 
|:-------:|:--------:|
| BS_ID | Sample Id for germline sample | 
| gene | Gene |
| chr | Chromosome |
| start | Start position |
| end | End position |
| ref | Reference allele |
| alt | Alternate Allele |
| proband_germline_ref_depth | Reference depth from germline for proband |
| proband_germline_alt_depth | Alternate depth from germline for proband |
| proband_germline_depth | total number of reads overlapping a site for proband  |
| proband_germline_vaf | The fraction of reads with the alternate allele for proband |
| paternal_germline_ref_depth | Reference depth from germline for father |
| paternal_germline_alt_depth | Alternate depth from germline for father |
| paternal_germline_depth | total number of reads overlapping a site for father |
| paternal_germline_vaf | The fraction of reads with the alternate allele for father |
| maternal_germline_ref_depth | Reference depth from germline for mother |
| maternal_germline_alt_depth | Alternate depth from germline for mother |
| maternal_germline_depth | total number of reads overlapping a site for mother  |
| maternal_germline_vaf | The fraction of reads with the alternate allele for mother |
| proband_Sample_ID_tumor_vaf | Variant Allele frequency from tumor for proband |
| proband_BS_DE26D072_tumor_depth | Depth of coverage | 
| proband_BS_DE26D072_tumor_alt_depth | Allele count at site for proband |
| proband_BS_DE26D072_tumor_ref_depth | Reference count at site for proband |