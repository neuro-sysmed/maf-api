# maf-api

Replace missing gt with 0/0 and calculate AF and friends

bcftools  +setGT mito_medaka.vcf.gz --  -t . -n 0 | bcftools +fill-tags  - -O z -o mito_medaka_af.vcf.gz 