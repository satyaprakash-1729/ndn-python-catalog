import pkg_resources
import argparse
from . import *
from ndn.app import NDNApp
from .storage.storage_factory import *
import asyncio as aio
from ndn.encoding import Name
from ndn.security import KeychainDigest
import logging
import sys


def process_cmd_opts():
    """
    Parse, process, and return cmd options.
    """
    def print_version():
        pkg_name = 'ndn-python-catalog'
        version = pkg_resources.require(pkg_name)[0].version
        print(pkg_name + ' ' + version)

    def parse_cmd_opts():
        parser = argparse.ArgumentParser(description='ndn-python-catalog')
        parser.add_argument('-v', '--version',
                            help='print current version and exit', action='store_true')
        parser.add_argument('-c', '--config',
                            help='path to config file')
        parser.add_argument('-r', '--catalog_name',
                            help="""catalog's routable prefix. If this option is specified, it 
                                    overrides the prefix in the config file""")
        args = parser.parse_args()
        return args

    args = parse_cmd_opts()
    if args.version:
        print_version()
        exit(0)
    return args


def config_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def process_config(cmdline_args):
    """
    Read and process config file. Some config options are overridden by cmdline args.
    """
    configuration = get_yaml(cmdline_args.config)
    if cmdline_args.catalog_name is not None:
        configuration['catalog_config']['catalog_name'] = cmdline_args.catalog_name
    return configuration


def main() -> int:
    cmdline_args = process_cmd_opts()
    config_logging()
    configuration = process_config(cmdline_args)
    storage = create_storage(configuration['db_config'])

    app = NDNApp()

    catalog_name = configuration['catalog_config']['catalog_name']
    read_handle = ReadHandle(app, storage, catalog_name)
    write_handle = WriteHandle(app, storage, read_handle)

    catalog = Catalog(Name.from_str(catalog_name),
        app, storage, read_handle, write_handle)
    aio.ensure_future(catalog.listen())

    try:
        app.run_forever()
    except FileNotFoundError:
        logging.error('Error: could not connect to NFD.')
    return 0


if __name__ == "__main__":
    main()
