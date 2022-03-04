#!/usr/bin/env python3
#
# Kim Brugger (24.02.2022) kbr(at)brugger.dk

import sys
import os
import pprint as pp
import argparse
import gzip
import json


import kbr.json_utils as json_utils

import maf.nirvana as nirvana


sys.path.append('.')






def main():

    parser = argparse.ArgumentParser(description='nirvana-filter: ')


    parser.add_argument('-b', '--biotype', help="proteinCoding, etc")
    parser.add_argument('-r', '--region', help="region to report variants in")
    parser.add_argument('-g', '--gnomad-freq', help="max allele frequency in gnomad, -1 == all")

    parser.add_argument('-c', '--clinvar', help="clinvar significance: not provided, uncertain significance, benign, likely benign, likely pathogenic, pathogenic ")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('nirvana', nargs='+', help="nirvana output file")

    args = parser.parse_args()


    infile = args.nirvana[0]

    filter = {}
    if args.biotype:
        filter['bioType'] = args.biotype

    if args.clinvar:
        filter['inClinvar'] = args.clinvar

    if args.gnomad_freq:
        filter['allAf'] = float(args.gnomad_freq)


    n = nirvana.parse_annotation( infile, filter=filter )
    pp.pprint(n)


if __name__ == "__main__":
    main()