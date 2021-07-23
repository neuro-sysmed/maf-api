#!/usr/bin/env python3
#
#
#

import argparse
import sys
import pprint as pp

sys.path.append(".")


from tabulate import tabulate
#from urllib.parse import urlparse

from kbr import config_utils
import kbr.string_utils as string_utils
import kbr.args_utils as args_utils
#import kbr.password_utils as password_utils
#import kbr.db_utils as db_utils

import maf.db as maf_db



def project_cmd(args) -> None:
    commands = {'c':'create', 'l':'list', 'u':'update', 'd': 'delete', 'h':'help'}
    if len(args) == 0:
        args.append('help')

    command = args.pop(0)
    command = args_utils.valid_command(command, commands)

    if command == 'create':
        name = args_utils.get_or_fail(args, "Missing project name")
        db.project_create(name)
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


def main():

    commands = {'p':'project', 'm':'mafs', 'a':'annotation', 'h':'help'}

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
        args_utils.min_count_subcommand(1, len(args.command), name="groups")
        groups_command(args)
    elif command == 'annotation':
        args_utils.min_count_subcommand(1, len(args.command), name="acls")
        acls_command(args)

if __name__ == "__main__":
    main()
