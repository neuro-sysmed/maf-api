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
        return self.send_response(data={"name":"MAF-API", "version":f"{version}"})
#        self.render('index.html', title='My title', message='Hello world')


class ProjectsHandler ( tornado.BaseHandler ):

    def endpoint(self):
        return("/projects")

    def get(self):
        logger.debug("get projects")
        projects = db.projects()     
        return self.send_response(data=projects)


class ProjectHandler ( tornado.BaseHandler ):

    def endpoint(self):
        return("/project")

    def get(self, project_id:str):
        logger.debug("get project")
        data = db.projects(project_id)
        if data is None:
            return self.send_response_404()

        return self.send_response(data=data)


class VariantIdHandler ( tornado.BaseHandler ):

    def endpoint(self):
        return("/variant/[id]/")

    def get(self, variant_id:str):
        logger.debug("get variant")
        data = db.variant_get_by_id(variant_id)
        if data is None:
            return self.send_response_404()

        return self.send_response(data=data)


class VariantHandler ( tornado.BaseHandler ):

    def endpoint(self):
        return("/variant/[chrom]/[pos]/[ref]/[alt]/")

    def get(self, chrom:str, pos:int, ref:str, alt:str) -> None:
        logger.debug("get variant")
        data = db.variant_get(chrom, pos, ref, alt)
        if data is None:
            return self.send_response_404()

        return self.send_response(data=data)


class RegionHandler ( tornado.BaseHandler ):

    def endpoint(self):
        return("/region/chrom/start/end/")

    def get(self, chrom:str, start:int, end:int) -> None:
        logger.debug("get region")
        data = db.region_get(chrom, start, end)
        if data is None:
            return self.send_response_404()

        return self.send_response(data=data)



def main():
    parser = argparse.ArgumentParser(description='maf-rest-api: ')


    parser.add_argument('-c', '--config', default="api.json", help="config file, can be overridden by parameters")

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-p', '--port', help="Port to bind to")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")

    args = parser.parse_args()

    config = config_utils.readin_config_file( args.config )
    if 'logfile' not in config:
        config.logfile= None

    if args.port:
        config.server.port = args.port

    if args.logfile:
        config.logfile = args.logfile
    
    print(config)


    logger.init(name=config.name, log_file=config.logfile )
    logger.set_log_level( args.verbose )

    if 'database' in config:
        global db
        db = maf_db.DB()
        db.connect( config.database )

    urls = [('/', RootHandler),
            ('/projects/?', ProjectsHandler),
            ('/project/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?', ProjectHandler),
            ('/variant/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?', VariantIdHandler),
            ('/variant/(\w+)/(\d+)/(\w+)/(\w+)/?', VariantHandler),
            ('/region/(\w+)/(\d+)/(\d+)/?', RegionHandler),
#            ('/mafs/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?', MafHandler), 
            ] 


    logger.info(f"Running on port: {config.get('port', 8008)}")
    try:
        tornado.run_app(urls, port=config.get('port', 8008))
    except KeyboardInterrupt:
        logger.info(f'stopping maf_api')



 

if __name__ == "__main__":
    main()