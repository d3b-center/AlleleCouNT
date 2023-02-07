#!/bin/sh

#script that runs bam-readcount tool https://github.com/genome/bam-readcount 

bam-readcount -w1 -f $2 $1 -l $3 > output_readcount.out
