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

def mafs_cmd(args) -> None:

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

        alts = r.alts
        afs  = r.info['AF']
        coverage =  r.info['AN']
        acs  = r.info['AC']

        for index, alt in enumerate(alts):
            af = afs[index]
            ac = acs[index]
            if af == 0:
                continue

#            print(r.chrom, r.pos, r.ref, alt, af)
            var_id = db.variant_add(r.chrom, r.pos, r.ref, alt)
            db.project_variant_add( project_id, var_id, af, coverage=coverage, alt_alleles=ac)
        count += 1
        if count % 1000 == 0:
            print(f"{count} (1000 vars in {(time.time() - start_time):.2f} seconds)...")
            start_time = time.time()

    



def main():

    commands = {'p':'project', 'm':'mafs', 'a':'annotation', 'e': 'export', 'h':'help'}

    parser = argparse.ArgumentParser(description='map import tool')
    parser.add_argument('-c', '--config', default="api.json", help="config file, can be overridden by parameters")
    parser.add_argument('command', nargs='+', help="{}".format(",".join(commands)))

    args = parser.parse_args()


    args.config = config_utils.readin_config_file( args.config )

    if len(args.command) == 0:
        args.command.append('help')

    command = args.command.pop(0)
    command = args_utils.valid_command(command, commands)

    global db
    db = maf_db.DB()
    db.connect( args.config.database )

    if command == 'project':
        project_cmd(args.command)
    elif command == 'mafs':
        mafs_cmd(args.command)
    elif command == 'export':
        export_cmd(args.command)
    elif command == 'annotation':
        args_utils.min_count_subcommand(1, len(args.command), name="acls")
        acls_command(args)

if __name__ == "__main__":
    main()
