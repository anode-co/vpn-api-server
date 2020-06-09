#!/usr/bin/env python3
import argparse
import yaml
import json
from simplecgi import (
    Route,
    ApiHttpServer,
)
from views import (
    PersonView,
    AuthorizeClientView
)
from hades import (
    DatabaseManager,
)
from models import (
    CjdnsRouteManager,
)

database_manager = DatabaseManager(
    DatabaseManager.DB_TYPE_SQLITE3,
    {
        'file': 'db.sqlite3'
    },
    in_verbose_mode=True
)


routes = [
    Route(path='/people/', view=PersonView(database_manager)),
    # Route(path='/authorize/', view=AuthorizeClientView(database_manager)),
]

default_config_file = 'config.yaml'


def parse_arguments():
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c'
        '--config',
        help="Specify a config file",
        default=default_config_file,
        type=argparse.FileType('r')
    )
    return parser.parse_args()


def get_config(config_file):
    """Read the config file."""
    output = []
    with open(config_file) as file:
        output = yaml.load(file, Loader=yaml.Loader)
    print(json.dumps(output))
    return output


if __name__ == '__main__':
    args = parse_arguments()
    config = get_config(args.c__config.name)

    route_manager = CjdnsRouteManager(database_manager, config['cjdns'])

    port = config['api_server']['port']
    server = ApiHttpServer('localhost', port)

    routes.append(
        Route(path='/authorize/', view=AuthorizeClientView(database_manager, route_manager)),
    )
    print(dir(routes[1].view))
    server.add_routes(routes)

    print("\n")
    print('Starting server on port {}, use <Ctrl + F2> to stop'.format(port))
    server.run()
