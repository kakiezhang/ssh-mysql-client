""" mysqlclient
Command: 
./smc 
OR 
python3 client.py 
"""

import sys
import time
import argparse
from random import randint
from utils import shell

import consts
from sqlite.hole_pie import HolePie
import logger

log = logger.get(__name__)


def assign_argument():
    ap = argparse.ArgumentParser()

    ap.add_argument('alias', type=str, help='choose a MySQL proxy alias')
    ap.add_argument('-c', '--create', help='create a MySQL proxy', action='store_true')
    ap.add_argument('-o', '--overwrite', help='overwrite a MySQL proxy', action='store_true')
    ap.add_argument('-s', '--signal', type=str, choices=['start', 'stop'], help='build or lost ssh proxy')

    options = ap.parse_args()

    global action, alias

    alias = options.alias
    signal = options.signal

    action = 'connect' if not options.create else 'create'
    action = action if not options.overwrite else 'overwrite'

    if signal == 'start':
        action = 'build_ssh'
    elif signal == 'stop':
        action = 'lost_ssh'

    log.debug('[Param]: action={}, alias={}'.format(action, alias))


def random_free_port(retry=5):
    for i in range(0, retry):
        port = randint(9500, 9700)
        command = '/bin/sh -c "echo $(netstat -an|grep {}|wc -l)"'.format(port)
        rv, ok = shell.run_with_output(command)
        if not ok or not rv:
            continue

        try:
            if int(rv[0]) == 0:
                log.info('[Func random_free_port]: find free port={}'.format(port))
                break
        except:
            raise

    return port


def lost_ssh_conn():
    command = '/bin/sh -c "pkill -f \'{}\'"'.format(aim_host)
    shell.run(command)


def init_globals():
    rv = HolePie().get_by_alias(alias)
    if not rv:
        log.warning('Proxy[%s] not exist, abort!' % alias)
        return False

    global aim_user, aim_pwd, aim_host,\
        aim_port, proxy_host, proxy_port,\
        proxy_user, proxy_pwd, local_port

    _, _, aim_host, aim_port, aim_user,\
        aim_pwd, local_port, proxy_host,\
        proxy_port, proxy_user, proxy_pwd,\
        _, _, _ = rv

    return True


def build_ssh_conn():
    command = '/bin/sh -c "echo $(ps -ef|grep ssh|grep \'{}:{}\'|grep -v grep|wc -l)"'.format(local_port, aim_host)
    rv, ok = shell.run_with_output(command)
    if not ok or not rv:
        log.warning('can\'t build available ssh connection')

    if int(rv[0]) == 0:
        log.info('building ssh connection...')
        command = consts.HOLE_COMMAND.format(
            local_port=local_port,
            aim_host=aim_host,
            aim_port=aim_port,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_user=proxy_user,
        )
        shell.run(command)
    else:
        log.info('using built ssh connection')


def build_mysql_cli_conn():
    command = consts.LOCAL_CLI_COMMAND.format(
        aim_user=aim_user,
        aim_pwd=aim_pwd,
        local_port=local_port,
    )
    log.info(command)
    shell.run(command)


def connect_mysql():
    if init_globals():
        build_ssh_conn()
        build_mysql_cli_conn()


def create_proxy():
    log.info('The following records will be striped by symbols like blank, \\n, \\r\\n, etc.')
    params = {}

    for item in consts.QUESTIONS:
        desc = item['desc']
        col = item['col']

        log.info(desc)
        line = sys.stdin.readline()
        line = line.strip().strip('\r\n').strip('\n')
        if not line:
            if 'default' in item:
                line = item['default']
            elif 'empty_allowed' in item and item['empty_allowed']:
                line = ''
            else:
                log.warning('[Error]: The column cannot be NoneType or blank')
                break

        if col in params:
            continue

        params[col] = line

    params['local_port'] = random_free_port()
    params['alias'] = alias

    now = int(time.time())
    params['last_conn_time'] = params['create_time'] = params['update_time'] = str(now) 

    log.debug(params)

    try:
        # sequence params and insert table
        row_id = HolePie().insert_row(*[params[col] for col in HolePie().no_pk_cols])
    except Exception as e:
        log.warning('[Error]: {}'.format(e))
        return False

    return True


def main():
    assign_argument()

    if action == 'connect':
        connect_mysql()

    elif action == 'create':
        _ = HolePie().get_by_alias(alias)
        if not _:
            log.info('Create a new proxy[%s]' % alias)
            if create_proxy():
                log.info('Create proxy[%s] successfully!' % alias)
            else:
                log.warning('Create proxy[%s] failed!' % alias)
        else:
            log.info('Proxy[%s] existed' % alias)
            log.info('Done!')

    elif action == 'overwrite':
        rv = HolePie().get_by_alias(alias)
        if not rv:
            log.info('Proxy[%s] not found and try to create a new one' % alias)
        else:
            log.info('Overwrite the proxy[%s]' % alias)
            HolePie().delete_by_id(rv[0])

        if create_proxy():
            log.info('Overwrite proxy[%s] successfully!' % alias)
        else:
            log.warning('Overwrite proxy[%s] failed!' % alias)

    elif action == 'build_ssh':
        if init_globals():
            build_ssh_conn()
            log.info('Connect ssh proxy[%s] successfully!' % alias)

    elif action == 'lost_ssh':
        if init_globals():
            lost_ssh_conn()
            log.info('Disconnect ssh proxy[%s] successfully!' % alias)


if __name__ == '__main__':
    logger.setup()
    sys.exit(main())
