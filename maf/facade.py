
import json
from kbr import args_utils
import tabulate
import sys
import re

import kbr.args_utils as args_utils


def print_vcf(unannotated:bool=False) -> None:

    print("##fileformat=VCFv4.2")
    print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")
    for v in maf_db.variants():
        print("\t".join([v['chrom'], v['pos'], ".", v['ref'], v['alt'], '.','.','.']))



def query(maf_db, columns:list, regions:list=None, projects:list=None, frequency:float=1.0, as_json:bool=False) -> None:

    db_projects = maf_db.projects()
    if projects is not None and projects != []:
        filtered_projects = []
        for db_project in db_projects:

            if db_project['name'] in projects:
                filtered_projects.append( db_project )

        db_projects = filtered_projects

    res = ['chrom', 'position', 'reference', 'alt']

    for db_project in db_projects:
        for column in columns:
            res.append(f"{db_project['name']} {column}")

    res = [res]

    variants = []
    if regions is not None and regions != []:
        for region in regions:
            fields = re.split(r":|-", region)
            variants += maf_db.variants_in_region( *fields, )
#            print( variants )
    else:
        variants = maf_db.variants(order='chrom, pos')


    if as_json:
        print(json.dumps(variants))
    else:
        for variant in variants:
            var = [variant['chrom'], variant['pos'], variant['ref'], variant['alt']]
            var_info = False
            var_lowest_freq = 1.0
            for db_project in db_projects:

                project_variant = maf_db.project_variant(db_project['id'], variant['id'])
#                print( project_variant )
                c_map = {'AN': 'allele_number', 'AC': 'allele_count', 'AC_Hom': 'allele_count_hom', 'AF': 'frequency'}
#                print( project_variant[ 'frequency' ] )
                if project_variant is not None and  var_lowest_freq > float(project_variant[ 'frequency' ]):
                    var_lowest_freq = float(project_variant[ 'frequency' ])

                for column in columns:
                    if column not in c_map:
                        raise RuntimeError(f"Unknown column {column}")
                    if project_variant is None:
                       var.append("")                             
                    else:
                        var.append( project_variant[c_map[ column ]])
                        var_info = True
#                var.append( project_variant['allele_number'])
#                var.append( project_variant['allele_count_hom'])
#                var.append( project_variant['frequency'])
            if var_info and var_lowest_freq < float(frequency):
                res.append(var)

        print( tabulate.tabulate(res, headers="firstrow", tablefmt='psql'))


def calc_frequencies(maf_db) -> None:

    for variant in maf_db.variants():
        freqs = maf_db.project_afs(variant_id=variant['id'])
        allele_number = 0
        allele_count  = 0
        allele_count_hom = 0
        frequency = 0
        for freq in freqs:
            allele_number    += freq['allele_number']
            allele_count     += freq['allele_count']
            allele_count_hom += freq['allele_count_hom']

        frequency = allele_count/allele_number*1.0
        
        variant['allele_number']    = allele_number
        variant['allele_count']     = allele_count
        variant['allele_count_hom'] = allele_count_hom
        variant['frequency']        = frequency
        maf_db.variant_update( variant )
    

def import_annotations(maf_db, args ):



    filename = args_utils.get_or_fail(args, 'annotation filename missing')
    fh = open(filename, 'r')
    field_names = {}
    for line in fh.readlines():
        fields = line.rstrip().split(",")

        if fields[0] == 'Chr':
            for index, field in enumerate(fields):
                field_names[ field ] = index
            continue


        gene_name = fields[ field_names['Gene.refGene'] ]
        if gene_name == '.':
            continue

        gene_details = fields[ field_names['GeneDetail.refGene'] ]
        if gene_details in ['UTR', 'intronic']:
            continue


        chrom       = fields[ field_names['Chr'] ]
        pos         = fields[ field_names['Start'] ]
        ref         = fields[ field_names['Ref'] ]
        alt         = fields[ field_names['Alt'] ]


        effect       = fields[ field_names['ExonicFunc.refGene'] ]
        aa_changes   = fields[ field_names['AAChange.refGene'] ]
        ExAC_all     = fields[ field_names['ExAC_ALL'] ]
        dbsnp_id     = fields[ field_names['avsnp147'] ]
        sift         = fields[ field_names['SIFT_pred'] ]
        polyphen     = fields[ field_names['Polyphen2_HDIV_pred'] ]
        aa_changes = aa_changes.replace("\t", ";").replace('"','')

        if aa_changes == ".":
            continue
        
        for aa_change in aa_changes.split(";"):
            print(f'|{aa_changes}|')
            gene_name, transcript, exon, cnum, pnum = aa_change.split(r":")
            print(gene_name, transcript, exon, cnum, pnum)

            gene = maf_db.genes( name=gene_name, transcript=transcript )
            if gene is None or gene == []:
                gene = maf_db.gene_create(name=gene_name, transcript=transcript )
                gene = maf_db.genes( name=gene_name, transcript=transcript )
            gene = gene[0]

            variant = maf_db.variant_get(chrom, pos, ref, alt)

            print( f"gene_id={gene['id']}, variant_id={variant['id']}, ")

            maf_db.variant_annotation_add(gene['id'], variant['id'], 
                                            dbsnp=dbsnp_id,
                                            effect=effect,
                                            npos=pnum,
                                            cpos=cnum,
                                            DNA_change=cnum,
                                            AA_change=pnum,
                                            polyphen=polyphen,
                                            sift=sift)

            



