""" mysqldump
Command: 
./smd 
OR 
python3 dump.py 
"""

import sys
from utils import shell

import consts
from sqlite.hole_pie import HolePie
import logger

log = logger.get(__name__)


def assign_argument():
    args = sys.argv
    if not args:
        raise Exception('no argv')

    if len(args) < 2:
        raise Exception('argv{} not enough'.format(args))

    global alias, extra_options
    _ = args.pop(0)  # filename
    alias = args[0]
    extra_options = ' '.join(args)

    log.info('[Param]: alias={} extra_options={}'.format(alias, extra_options))


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


def build_mysql_dump_conn():
    command = consts.LOCAL_DUMP_COMMAND.format(
        aim_user=aim_user,
        aim_pwd=aim_pwd,
        local_port=local_port,
        extra_options=extra_options,
    )
    log.info(command)
    shell.run(command)


def connect_mysql():
    if init_globals():
        build_ssh_conn()
        build_mysql_dump_conn()


def main():
    try:
        assign_argument()
    except Exception as e:
        log.warning(e)
        return

    connect_mysql()


if __name__ == '__main__':
    logger.setup()
    sys.exit(main())
