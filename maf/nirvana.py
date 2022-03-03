import sys
import re
import pprint as pp

import kbr.json_utils as json_utils


def _position_info(locus:dict, sample_list:list, filter:dict={}, unknown_as_ref=True) -> dict:
    
#    print( filter )

    # if gt == . unknown_as_ref will transform it to 0/0

    res = {}

    samples = len(sample_list)
    base_var = { 'chrom': locus['chromosome'],
                 'pos': locus[ 'position' ],
                 'ref': locus['refAllele']}

#    alts = dict(enumerate(locus['altAlleles']))
    alts = dict([(value, key + 1) for key, value in enumerate(locus['altAlleles'])])
#    print( alts )

    gts = {}
    for index, sample in enumerate(locus['samples']):
        if 'isEmpty' in sample:
            continue
#        print( sample) 
        if unknown_as_ref and sample['genotype'] in ["./.", ".", ".|."]:
            sample['genotype'] = "0/0"

        gts[ sample[ 'genotype'] ] = gts.get(sample[ 'genotype'], [])
        gts[ sample[ 'genotype'] ].append( sample_list[index])


    gts_af = {}
    for gt in gts:
        a1, a2 = re.split("/|\|", gt)
        if a1 == a2:
            gts_af[ gt ] = 2*len(gts[gt])/(samples * 2)
        else:
            gts_af[ gt ] = len(gts[gt])/(samples * 2)


#    pp.pprint( gts_af )


    for variant in locus['variants']:

        print_variant = False
        if filter == {}:
            print_variant = True

#        pp.pprint( variant )
        var = base_var.copy()
        var['alt'] = variant['altAllele']
        if len(variant['refAllele']) < 10 and len(variant['altAllele']) < 10:
            var[ 'vid'] = f"{variant['chromosome']}-{variant['begin']}-{variant['refAllele']}-{variant['altAllele']}"
        for transcript in variant.get('transcripts', []):
            for key in transcript:
                if key in filter and transcript[ key ] in filter[ key ]:
                    print_variant = True
                    for k in ['hgnc', 'consequence', 'isCanonical', 'transcript', 'siftPrediction', 'polyPhenPrediction', 'cdsPos', 'aminoAcids']:
                        if k not in transcript:
                            continue

                        if isinstance(transcript[k], list):
                            var[ k ] = ";".join(transcript[k])
                        else:
                            var[ k ] = transcript[k]
                    break

            else:
                pass


        if 'inClinvar' in filter and 'clinvar' in variant:
            print_variant = False

        for clinvar in variant.get('clinvar', []):

            if 'inClinvar' in filter and filter['inClinvar'] in clinvar['significance']:
                print_variant = True

            for k in ['significance', 'reviewStatus', 'phenotypes']:
                if k not in clinvar:
                    continue
                if isinstance(clinvar[k], list):
                    var[ k ] = ";".join(clinvar[k])
                else:
                    var[ k ] = clinvar[k]


        if 'gnomad' in variant:
            if 'allAf' in filter and float( filter['allAf']) < variant['gnomad'].get('allAf', 1.0):
                print_variant = True

        for mitomap in variant.get('mitomap', []):
            for k in ['diseases', 'status', 'significance']:
                if k not in mitomap:
                    continue
                if isinstance(mitomap[k], list):
                    var[ k ] = ";".join(mitomap[k])
                else:
                    var[ k ] = mitomap[k]


        if print_variant:
            print(var)

    return res






def parse_annotation(infile:str, filter:dict={}) -> list:


    annotations = json_utils.read( infile )

    samples = annotations['header'].get('samples',[])
    filtered = []


    for position in annotations['positions']:
#        pp.pprint( annotation )
#        base_var = { 'chrom': position['chromosome'],
#                     'pos': position[ 'position' ],
#                     'ref': annotation['refAllele']}

        gts = _position_info( position, samples, filter=filter )
        continue
        sys.exit()
#       alts = annotation['altAlleles']


        for variant in annotation['variants']:
            if 1:

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