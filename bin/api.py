#!/usr/bin/env python3

''' REST API for vmail'''

import argparse

import pprint as pp

import kbr.log_utils as logger
import kbr.config_utils as config_utils
import kbr.version_utils as version_utils

import kbr.tornado   as tornado

import maf.db as maf_db

db = None


version = version_utils.as_string()

class RootHandler ( tornado.BaseHandler ):

    def endpoint(self):
        return("/")

    def get(self):

        self.canRead( self.endpoint() )
        return self.send_response(data={"name":"MAF-API", f"version":"{version}"})
#        self.render('index.html', title='My title', message='Hello world')



def main():
    parser = argparse.ArgumentParser(description='maf-rest-api: ')


    parser.add_argument('-c', '--config', default="api.json", help="config file, can be overridden by parameters")

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-p', '--port', help="Port to bind to")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")

    args = parser.parse_args()

    config = config_utils.readin_config_file( args.config )

    if args.port:
        config.server.port = args.port

    if args.logfile:
        config.logfile = args.logfile


    logger.init(name=config.name, log_file=config.logfile )
    logger.set_log_level( args.verbose )

    if 'database' in config:
        global db
        db = <PROJECT>_db.DB()
        db.connect( config.database )

    urls = [('/', RootHandler),
            ('/projects/?', ProjectsHandler),
            # f647fa3e-1292-496e-ba26-7e085782eee7
            ('/project/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?', ProjectHandler),
            ('/variant/(\w+)/(\w+)/(\w+)/?', VariantHandler),
            ('/region/(\w+)/(\d+)/(\d+)/?', RegionHandler),
            ] 

    tornado.run_app( urls, **config.server )


if __name__ == "__main__":
    main()