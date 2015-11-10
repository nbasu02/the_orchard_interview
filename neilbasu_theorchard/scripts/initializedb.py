import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Base,
    )

from getpass import getpass
from ConfigParser import SafeConfigParser
from subprocess import call
import os


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def createdb():
    path = os.path.dirname(os.path.realpath(__file__))

    pg_user = raw_input("Please enter your postgresql user's username: ")
    pg_password = getpass('Please enter password: ')

    # Set settings username/pass to what user gave
    config_parser = SafeConfigParser()

    ini_filepath = os.path.join(path, '..', '..', 'development.ini')
    config_parser.read(ini_filepath)

    config_parser.set('app:main', 'sqlalchemy.url',
        'postgresql+psycopg2://%(username)s:%(password)s@localhost/neilbasu_theorchard' % {
            'username': pg_user,
            'password': pg_password
        })

    config_parser.set('app:main', 'testing.testdb',
        'postgresql+psycopg2://%(username)s:%(password)s@localhost/neilbasu_theorchard_testdb' % {
            'username': pg_user,
            'password': pg_password
        })

    with open(ini_filepath, 'wb') as ini_file:
        config_parser.write(ini_file)

    # Now to do some db setup
    dummy_env = os.environ.copy()
    # normally this sort of step would be done on identical environments, but that's not
    # guaranteed here
    dummy_env['PGPASSWORD'] = pg_password

    print('Attempting to drop database...')
    call('dropdb neilbasu_theorchard -U %(username)s' % {'username': pg_user},
        shell=True, env=dummy_env)
    call('dropdb neilbasu_theorchard_testdb -U %(username)s' % {'username': pg_user},
        shell=True, env=dummy_env)
    print('Creating new database...')
    call('createdb neilbasu_theorchard -U %(username)s' % {'username': pg_user},
        shell=True, env=dummy_env)
    call('createdb neilbasu_theorchard_testdb -U %(username)s' % {'username': pg_user},
        shell=True, env=dummy_env)
    print('Database created')


def main(argv=sys.argv):
    createdb()

    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)

    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
