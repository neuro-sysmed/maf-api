import json
import sys
import gzip
import pprint as pp

import kbr.json_utils as json_utils


def parse_annotation(infile:str) -> list:


    if ".gz" in infile:
        with gzip.open(infile, 'rt', encoding='UTF-8') as zipfile:
            annotations = json.load(zipfile)
    else:
        annotations = json_utils.read( infile )

#    print( annotations )

#    for k in annotations.keys():
#        print( k )

    filtered = []

    for annotation in annotations['positions']:
#        pp.pprint( annotation )
        for alt in annotation['altAlleles']:
            base_var = { 'chrom': annotation['chromosome'],
                    'pos': annotation[ 'position' ],
                    'ref': annotation['refAllele'],
                    'alt': alt}

            for variant in annotation['variants']:

                if 'transcripts' in variant:
                    for transcript in variant['transcripts']:
                        if transcript['bioType'] !=  'protein_coding':
                            continue

                        var = base_var.copy()

                        var[ 'dbsnp' ]  = ",".join(variant.get('dbsnp', []))
                        var[ 'gnomad'] = variant.get('gnomad',{}).get('allAn', "")

                        var[ 'gene' ]  = transcript.get('hgnc', "")
                        var[ 'transcript' ]  = transcript.get('transcript', "")
                        var[ 'canonical']   =  transcript.get('isCanonical', False)
                        var[ 'cpos' ]  = transcript.get('cdsPos', "")
                        var[ 'npos' ]  = transcript.get('proteinPos', "")
                        var[ 'DNA_change' ]  = transcript.get('codons', "")
                        var[ 'AA_change' ]  = transcript.get('aminoAcids', "")                                        
                        var[ 'effect' ]  = ",".join(transcript.get('consequence', []))
    
                        var[ 'sift' ]  = transcript.get('siftPrediction', "")
                        var[ 'polyphen' ]  = transcript.get('polyPhenPrediction', "")


                        filtered.append( var )
#                        return filtered
#                sys.exit()
#            filtered[ var ] = {}


#    pp.pprint( filtered )
    return filtered