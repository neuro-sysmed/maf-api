
import json
import tabulate
import sys
import re


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
            for db_project in db_projects:

                project_variant = maf_db.project_variant(db_project['id'], variant['id'])
#                print( project_variant )
                c_map = {'AN': 'allele_number', 'AC': 'allele_count', 'AC_Hom': 'allele_count_hom', 'AF': 'frequency'}
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
            if var_info:
                res.append(var)

        print( tabulate.tabulate(res, headers="firstrow", tablefmt='psql'))
