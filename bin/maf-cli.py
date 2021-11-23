#!/usr/bin/env python3
#
#
#

import argparse
import sys
import pprint as pp
import time

sys.path.append(".")


from tabulate import tabulate
#from urllib.parse import urlparse

from pysam import VariantFile


from kbr import config_utils
import kbr.string_utils as string_utils
import kbr.args_utils as args_utils
#import kbr.password_utils as password_utils
#import kbr.db_utils as db_utils

import maf.db as maf_db
import maf.facade as facade


def export_cmd(args) -> None:
    commands = {'a':'all', 'u':'unannotated', 'h':'help'}
    if len(args) == 0:
        args.append('help')

    command = args.pop(0)
    command = args_utils.valid_command(command, commands)

    if command == 'all':
#        facade.print_vcf()
        print("##fileformat=VCFv4.2")
        print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")
        for v in db.variants():
            print("\t".join([v['chrom'], str(v['pos']), ".", v['ref'], v['alt'], '.','.','.']))
    elif command == 'unannotated':
        facade.print_vcf(unannotated=True)
    



def query_cmd(args:list=[], as_json:bool=False) -> None:

    if 'help' in args:
        print("Help:")
        print("Query variants")
        print("==========================")
        print("query region:[chrom:from-to] region:[chrom]")
        print("query region:[chrom:from-to] region:[chrom] r:[chr1,chr2,...]")
        print("query frequency:[less than fraction, eg 0.1]")
        print("query f:[less than fraction, eg 0.1]")
        print("query project:[name] p:[p1,p2,p3]")
        print("query columns:[AN,AC, AC_Hom, AF] (defaults: AN + AF)")
        sys.exit(1)



    args_mapping = {'r': 'region', 'f': 'frequency', 'p': 'project', 'c':'columns'}
    args = args_utils.group_args(args, args_mapping)
    if 'columns' not in args:
        args['columns'] = ['AN','AF']


    facade.query(db, columns=args['columns'], regions=args.get('region', None), projects=args.get('project', None), frequency=args.get('frequency', 1.0), as_json=as_json)




def project_cmd(args) -> None:
    commands = {'c':'create', 'l':'list', 'u':'update', 'd': 'delete', 'h':'help'}
    if len(args) == 0:
        args.append('help')

    command = args.pop(0)
    command = args_utils.valid_command(command, commands)

    if command == 'create':
        name = args_utils.get_or_fail(args, "Missing project name")
        print(db.project_create(name))
    elif command == 'list':
        projects = db.projects()
        print( tabulate(projects, headers={'id':'id', 'name':'name'}, tablefmt='psql'))
    elif command == 'update':
        id = args_utils.get_or_fail(args, "Missing project id")
        name = args_utils.get_or_fail(args, "Missing project name")
        db.project_update({'id': id, 'name':name})
    elif command == 'delete':
        id = args_utils.get_or_fail(args, "Missing project id")
        db.project_delete(id)
    else:
        print("Help\n-----------------")
        print("import project list")
        print("import project create <project name>")
        print("import project update <id> <new project name>")
        print("import project delete <id>")

def import_cmd(args) -> None:

    name = args_utils.get_or_fail(args, "Missing project name")
    project_id = db.project_create(name)

    vcf = args_utils.get_or_fail(args, "Missing vcf file")
    vcf_in = VariantFile(vcf)  # auto-detect input format
    count = 0
    print("Importing variants ...")
    start_time = time.time()
    for r in vcf_in.fetch():
        if 'AC0' in r.filter or 'AS_VQSR' in r.filter:
            continue

        if 'AF' not in r.info:
            print(f"No AF! {r}")
            continue

        an =  r.info['AN']

        alts = r.alts
        afs  = r.info['AF']
        acs  = r.info['AC']
        ac_homs  = r.info['AC_Hom']

        for index, alt in enumerate(alts):
            af = afs[index]
            ac = acs[index]
            ac_hom = ac_homs[index]
            if af == 0:
                continue

#            print(r.chrom, r.pos, r.ref, alt, af)
            var_id = db.variant_add(r.chrom, r.pos, r.ref, alt)
            db.project_variant_add( project_id, var_id, allele_number=an, allele_count=ac,  allele_count_hom=ac_hom, frequency=af)

        count += 1
        if count % 1000 == 0:
            print(f"{count} (1000 vars in {(time.time() - start_time):.2f} seconds)...")
            start_time = time.time()

    



def main():

    commands = {'q': 'query', 'p':'project', 'i':'import', 'a':'annotate', 'e': 'export', 'h':'help'}

    parser = argparse.ArgumentParser(description='map import tool')
    parser.add_argument('-c', '--config', default="api.json", help="config file, can be overridden by parameters")
    parser.add_argument('command', nargs='*', help="{}".format(",".join(commands.values())))

    args = parser.parse_args()

    args_utils.min_count(1, len(args.command),
                         msg="maf-cli takes one of the following commands: {}".format(args_utils.pretty_commands(commands)))


    args.config = config_utils.readin_config_file( args.config )
    if len(args.command) == 0:
        args.command.append('help')

    command = args.command.pop(0)
    command = args_utils.valid_command(command, commands)

    global db
    db = maf_db.DB()
    db.connect( args.config.database )

    if command == 'query':
        query_cmd(args.command)
    if command == 'project':
        project_cmd(args.command)
    elif command == 'import':
        import_cmd(args.command)
    elif command == 'export':
        export_cmd(args.command)
    elif command == 'annotate':
        args_utils.min_count_subcommand(1, len(args.command), name="acls")
        acls_command(args)
    elif command == 'help':
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
