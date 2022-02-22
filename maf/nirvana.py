import json
import sys
import pprint as pp

import kbr.json_utils as json_utils


def parse_annotation(infile:str) -> list:
    
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
                        var = base_var.copy()
                        var[ 'dbsnp' ]  = ",".join(variant.get('dbsnp', []))
                        var[ 'gnomad'] = variant.get('gnomad',{}).get('allAn', "")

                        var[ 'transcript' ]  = transcript.get('transcript', "")
                        var[ 'cpos' ]  = transcript.get('cdsPos', "")
                        var[ 'npos' ]  = transcript.get('proteinPos', "")
                        var[ 'DNA_change' ]  = transcript.get('codons', "")
                        var[ 'AA_change' ]  = transcript.get('aminoAcids', "")                                        
                        var[ 'effect' ]  = ",".join(transcript.get('consequence', []))
    
                        var[ 'sift' ]  = transcript.get('siftPrediction', "")
                        var[ 'polyphen' ]  = transcript.get('polyPhenPrediction', "")


                        filtered.append( var )
#            filtered[ var ] = {}


#    pp.pprint( filtered )
    return filtered