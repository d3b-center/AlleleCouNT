# Kids First Allele Counter (AlleleCouNT)

![data service logo](https://github.com/d3b-center/d3b-research-workflows/raw/master/doc/kfdrc-logo-sm.png)

The Kids First Allele Counter (aka AlleleCouNT) is a CWL workflow that assesses allele depth in normal and tumor DNA sequencing data across rare germline calls filtered by gnomad_3_1_1_AF_popmax (typically < 0.01). This preprocessing is designed to compute variant allele frequency (VAF) for proband germline and tumor samples and can also map germline VAF for family trios if trio germline VCF file is provided.

#### Basic info
- Dockerfile: https://github.com/d3b-center/bixtools/tree/master/LOH/1.0.1
- tested with
    - Seven Bridges Cavatica Platform: https://cavatica.sbgenomics.com/
    - cwltool: https://github.com/common-workflow-language/cwltool/releases/tag/3.1.20221201130942

### Application Description

The Kids First AlleleCouNT application is divided into two tools: Germline tool and Tumor tool.

#### Germline Tool

Germline tool filters germline annotations to retain variants based on gnomad_3_1_1_AF_popmax (typically < 0.01) or when gnomad_3_1_1_AF_popmax is not defined. It requires vcf file, proband sample id, ram as required inputs and peddy file as optional input which is required for family trios. It outputs variant information such as gene, chr, start, stop, ref/alt alleles, ref/alt allele depths, variant allele frequency and list of coordinates that will be an input to tumor tool.

#### Tumor Tool
Search in paired proband tumor sample for aligned reads in the regions where rare variants from the germline exist and exact allele/reference count, allele/reference depth, and calculate variant allele frequency(VAF). Tumor tool has the capability to search in multiple tumor samples for proband and if applicable, paternal and maternal tumor samples. To extract reads from the bam/cram files, this tool utilizes [bam-readcount](https://github.com/genome/bam-readcount) and wraps it with a python script to shape the output in a tabular format. 

### AlleleCouNT Inputs
```yaml
Germline tool
  # Required  
  BS_ID:{ doc: provide BS id for germline normal, type: string }
  frequency:{ doc: provide popmax cutoff for rare germline variants, type: 'float?', default: 0.01 }
  # Optional
  ram_germline:{  doc: Provide ram (in GB) based on the size of vcf, type: 'int?', default: 8}
  # Required for family trios otherwise not required
  peddy_file:{ doc: provide ped file for the trio, type: 'File?' }

Tumor tool
  # Required
  participant_id:{ doc: provide participant id for this run, type: string }
  bamscrams:{ doc: tumor input file in cram or bam format with their index file, type: 'File[]' , secondaryFiles: [ { pattern: ".crai", required: false }, { pattern: ".bai", required: false } ] }
  reference:{ doc: human reference in fasta format with index file, type: File,secondaryFiles: [ .fai ] }
  sample_vcf_file: { doc: provide germline vcf file for this sample, type: File }
  # Optional
  minDepth:{ doc: provide minDepth to consider for tumor reads, type: 'int?', default: 1 }
  bamcramsampleIDs: { doc: provide unique identifers (in the same order) for cram/bam files provided under bamcrams tag. Default is sample ID pulled from bam/cram files., type: 'string[]?' }
  ram_tumor:{  doc: Provide ram (in GB) for tumor tool based on the number cram/bam inputs, type: 'int?', default: 16} 
  minCore:{ type: 'int?', default: 16, doc: "Minimum number of cores for tumor tool based on the number cram/bam inputs" }
```
### AlleleCouNT schematic

![AlleleCouNT schematic](https://github.com/d3b-center/tumor-loh-app-dev/blob/master/docs/logo/loh.png)

### AlleleCouNT Output

AlleleCouNT application will output a tab-separated values file mapped data from germline tool and tumor tool. 
```yaml
output_file:{ type: File, doc: A tsv file with gathered data from germline and tumor tool }
```

#### Output headers

Preprocessing AlleleCouNT will generate a tab-separated values file with following headers:
| Headers | Description | 
|:-------:|:--------:|
| BS_ID | Sample Id for germline sample | 
| gene | Gene |
| chr | Chromosome |
| start | Start position |
| end | End position |
| ref | Reference allele |
| alt | Alternate Allele |
| proband_germline_ref_depth | Reference depth from germline from germline proband |
| proband_germline_alt_depth | Alternate depth from germline from germline proband |
| proband_germline_depth | Total number of reads overlapping a site from germline proband  |
| proband_germline_vaf | Fraction of reads with the alternate allele from germline proband |
| paternal_germline_ref_depth | Reference depth from germline from paternal germline |
| paternal_germline_alt_depth | Alternate depth from germline from paternal germline |
| paternal_germline_depth | Total number of reads overlapping a site from paternal germline |
| paternal_germline_vaf | Fraction of reads with the alternate allele from paternal germline |
| maternal_germline_ref_depth | Reference depth from maternal germline |
| maternal_germline_alt_depth | Alternate depth from maternal germline |
| maternal_germline_depth | Total number of reads overlapping a site from mother  |
| maternal_germline_vaf | Fraction of reads with the alternate allele from mother |
| proband_sample_id_tumor_vaf |  Proband variant allele frequency from specific tumor sample|
| proband_sample_id_tumor_depth | Depth of coverage from specific tumor sample | 
| proband_sample_id_tumor_alt_depth | Allele count at site from specific proband tumor sample|
| proband_sample_id_tumor_ref_depth | Reference count at site from specific proband tumor sample |

More information can be found [here](https://github.com/d3b-center/tumor-loh-app-dev/tree/master/docs/README.md)

### Running it locally on a laptop?

It is recommended to run this CWL workflow on a system with a high number of CPUs and memory (>=16 GB). The basic requirement is a running docker engine and CWL tools. Command line to run the AlleleCouNT workflow locally is:

```
cwltool workflow/run_LOH_app.cwl sample_input.yml
```
Note: Inputs to the workflow need to be defined in sample_input.yml.