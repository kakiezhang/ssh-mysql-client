# -*- coding: utf-8 -*-

""" 
Command: 
./smc 
OR 
python3 index.py 
"""

import sys
import time
import argparse
from random import randint
from utils import bash
from sqlite.hole_pie import HolePie


HOLE_COMMAND = 'ssh -fNg -L {local_port}:{aim_host}:{aim_port} {proxy_user}@{proxy_host} -P {proxy_port}'
LOCAL_CLI_COMMAND = 'mysql -h127.0.0.1 -u"{aim_user}" -p"{aim_pwd}" -P{local_port} -A'
QUESTIONS = [
    {
        'col': 'aim_host',
        'desc': 'Please fill in the MySQL host:',
    },
    {
        'col': 'aim_port',
        'desc': 'Please fill in the MySQL port[default 3306]:',
        'default': 3306,
    },
    {
        'col': 'aim_user',
        'desc': 'Please fill in the MySQL username:',
    },
    {
        'col': 'aim_pwd',
        'desc': 'Please fill in the MySQL password:',
        'empty_allowed': True,
    },
    {
        'col': 'proxy_host',
        'desc': 'Please fill in the proxy host:',
    },
    {
        'col': 'proxy_port',
        'desc': 'Please fill in the proxy port[default 22]:',
        'default': 22,
    },
    {
        'col': 'proxy_user',
        'desc': 'Please fill in the proxy username:',
    },
    {
        'col': 'proxy_pwd',
        'desc': 'Please fill in the proxy password:',
        'empty_allowed': True,
    },
]


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

    print('[Param]: action={}, alias={}'.format(action, alias))


def random_free_port(retry=5):
    for i in range(0, retry):
        port = randint(9500, 9700)
        command = '/bin/sh -c "echo $(netstat -an|grep {}|wc -l)"'.format(port)
        rv = bash.run_with_output(command)
        if not rv:
            continue

        try:
            if int(rv[0]) == 0:
                print('[Func random_free_port]: find free port={}'.format(port))
                break
        except:
            raise

    return port


def lost_ssh_conn():
    command = '/bin/sh -c "pkill -f \'{}\'"'.format(aim_host)
    bash.run(command)


def init_ssh_conn():
    rv = HolePie().get_by_alias(alias)
    if not rv:
        print('Proxy[%s] not exist, abort!' % alias)
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
    rv = bash.run_with_output(command)
    if int(rv[0]) == 0:
        command = HOLE_COMMAND.format(
            local_port=local_port,
            aim_host=aim_host,
            aim_port=aim_port,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_user=proxy_user,
        )
        bash.run(command)


def build_mysql_conn():
    command = LOCAL_CLI_COMMAND.format(
        aim_user=aim_user,
        aim_pwd=aim_pwd,
        local_port=local_port,
    )
    bash.run(command)


def connect_mysql():
    if init_ssh_conn():
        build_ssh_conn()
        build_mysql_conn()


def create_proxy():
    print('The following records will be striped by symbols like blank, \\n, \\r\\n, etc.')
    params = {}

    for item in QUESTIONS:
        desc = item['desc']
        col = item['col']

        print(desc)
        line = sys.stdin.readline()
        line = line.strip().strip('\r\n').strip('\n')
        if not line:
            if 'default' in item:
                line = item['default']
            elif 'empty_allowed' in item and item['empty_allowed']:
                line = ''
            else:
                print('[Error]: The column cannot be NoneType or blank')
                break

        if col in params:
            continue

        params[col] = line

    params['local_port'] = random_free_port()
    params['alias'] = alias

    now = int(time.time())
    params['last_conn_time'] = params['create_time'] = params['update_time'] = str(now) 

    print(params)

    try:
        # sequence params and insert table
        row_id = HolePie().insert_row(*[params[col] for col in HolePie().no_pk_cols])
    except Exception as e:
        print('[Error]: {}'.format(e))
        return False

    return True


def main():
    assign_argument()

    if action == 'connect':
        connect_mysql()

    elif action == 'create':
        _ = HolePie().get_by_alias(alias)
        if not _:
            print('Create a new proxy[%s]' % alias)
            if create_proxy():
                print('Create proxy[%s] successfully!' % alias)
            else:
                print('Create proxy[%s] failed!' % alias)
        else:
            print('Proxy[%s] existed' % alias)
            print('Done!')

    elif action == 'overwrite':
        rv = HolePie().get_by_alias(alias)
        if not rv:
            print('Proxy[%s] not found and try to create a new one' % alias)
        else:
            print('Overwrite the proxy[%s]' % alias)
            HolePie().delete_by_id(rv[0])

        if create_proxy():
            print('Overwrite proxy[%s] successfully!' % alias)
        else:
            print('Overwrite proxy[%s] failed!' % alias)

    elif action == 'build_ssh':
        if init_ssh_conn():
            build_ssh_conn()
            print('Connect ssh proxy[%s] successfully!' % alias)

    elif action == 'lost_ssh':
        if init_ssh_conn():
            lost_ssh_conn()
            print('Disconnect ssh proxy[%s] successfully!' % alias)


if __name__ == '__main__':
    sys.exit(main())
