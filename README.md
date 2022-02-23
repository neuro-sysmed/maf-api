# maf-api

Replace missing gt with 0/0 and calculate AF and friends

bcftools  +setGT mito_medaka.vcf.gz --  -t . -n 0 | bcftools +fill-tags  - -O z -o mito_medaka_af.vcf.gz 




# Extract ppmi cohorts

Participant_Status.csv from ppmi website along with variant calls.

Liftover with CrossMap (https://sourceforge.net/projects/crossmap)
liftOverChainFile=hg19ToHg38.over.chain.gz

# Get column names.
head -n1 Participant_Status.csv | perl -pe 's/,/\t/g' | col_ids

# Columns we want:
head -n5 Participant_Status.csv | awk -F, '{print $1, $3}'

# get cohorts:
cat  Participant_Status.csv | awk -F, '{print  $3}' | sort | uniq 
"Early Imaging (original study participants only)"
"Healthy Control"
"Parkinson's Disease"
"Prodromal"
"SWEDD"

# extract healthy individuals:
cat Participant_Status.csv | awk -F, '{gsub(/"/, "", $1);  print  $1,$3}'  | egrep Healthy  | awk '{print "PPMI_SI_" $1}' > ppmi_healthy

bcftools view --force-samples -U -S ppmi_healthy ppmi.feb.1.2015.liftover.vcf | bcftools +fill-tags -- > ppmi.feb.1.2015.liftover.healthy.vcf




cat Participant_Status.csv | awk -F, '{gsub(/"/, "", $1);  print  $1,$3}'  | egrep Disease  | awk '{print "PPMI_SI_" $1}' > ppmi_pd

bcftools view --force-samples -U -S ppmi_pd ppmi.feb.1.2015.liftover.vcf | bcftools +fill-tags -- > ppmi.feb.1.2015.liftover.healthy.vcf

./annotate_variation.pl --buildver hg38 --downdb seq humandb/hg38_seq
./retrieve_seq_from_fasta.pl humandb/hg38_refGene.txt -seqdir humandb/hg38_seq -format refGene -outfile humandb/hg38_refGeneMrna.fa
./annotate_variation.pl -webfrom annovar -downdb avdblist -buildver hg38 .
./annotate_variation.pl -buildver hg38 -downdb -webfrom annovar avsnp150 humandb/
./annotate_variation.pl -buildver hg38 -downdb -webfrom annovar gnomad_exome  humandb/
./annotate_variation.pl -buildver hg38 -downdb cytoBand  humandb/
./annotate_variation.pl -buildver hg38 -downdb clinvar_20210501 humandb/
./annotate_variation.pl -buildver hg38 -downdb -webfrom annovar dbnsfp42c humandb/ # sift etc


./convert2annovar.pl --format vcf ../dbdump.vcf > dbdump.avinput

./table_annovar.pl dbdump.avinput  humandb/ -buildver hg38 -out dbdump_out -remove -protocol refGene,cytoBand,gnomad_exome,avsnp150 -operation g,r,f,f -nastring . -csvout -polish  


```
#Nirvana

singularity exec --bind /home/:/home/ ../docker-nirvana/nirvana.sif dotnet /opt/nirvana/Nirvana.dll -c /home/refs/nirvana/Cache/GRCh38/Both -r /home/refs/nirvana/References/Homo_sapiens.GRCh38.Nirvana.dat --sd /home/refs/nirvana/SupplementaryAnnotation/GRCh38 -i dbdump.vcf -o dbdump

```


