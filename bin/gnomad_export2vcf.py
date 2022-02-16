#!/usr/bin/env python3

import sys
import random


def main() -> None:


    print("##fileformat=VCFv4.2")
    print("##INFO=<ID=AN,Number=1,Type=Integer,Description='Total number of alleles in called genotypes'>")
    print("##INFO=<ID=AC,Number=A,Type=Integer,Description='Allele count in genotypes'>")
    print("##INFO=<ID=NS,Number=1,Type=Integer,Description='Number of samples with data'>")
    print("##INFO=<ID=AC_Hom,Number=A,Type=Integer,Description='Allele counts in homozygous genotypes'>")
    print("##INFO=<ID=AC_Het,Number=A,Type=Integer,Description='Allele counts in heterozygous genotypes'>")
    print("##INFO=<ID=AC_Hemi,Number=A,Type=Integer,Description='Allele counts in hemizygous genotypes'>")
    print("##INFO=<ID=AF,Number=A,Type=Float,Description=Allele frequency'>")

    print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")

    filename = sys.argv[1]
    fh = open(filename, 'r')
    field_names = {}
    for line in fh.readlines():
        fields = line.rstrip().split(",")

        if fields[0] == 'Chromosome':
            for index, field in enumerate(fields):
                field_names[ field ] = index
            continue

        
        if random.randint(0,100) < 5:
            continue


        parts = []
        parts.append( fields[ field_names[ 'Chromosome']])
        parts.append( fields[ field_names[ 'Position']])
        parts.append( '.')
        parts.append( fields[ field_names[ 'Reference']])
        parts.append( fields[ field_names[ 'Alternate']])
        parts.append( '99')
        parts.append( 'PASS')

        AN = random.randint(10, 1000)
        AC = random.randint(0, AN)
        AC_Hom = random.randint(0,int(AC/2))
        AF = f"{AC/AN*1.0:.2f}"
        parts.append(f"AN={AN};AF={AF};AC={AC};AC_Hom={AC_Hom};")

        print( "\t".join( parts ))
            





if __name__ == "__main__":
    main()

