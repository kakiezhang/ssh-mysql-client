import os
import subprocess
import shlex
import logger

log = logger.get(__name__)


def run(cmd):
    log.debug('[Run command]: {}'.format(cmd))
    os.system(cmd)


def run_with_output(cmd, shell=False):
    log.debug('[Run command]: {}'.format(cmd))
    fmt_cmd = shlex.split(cmd)
    p = subprocess.Popen(fmt_cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    rst = []
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if isinstance(line, bytes):
                line = line.decode()
            log.debug('[Output]: {}'.format(line))
            rst.append(line)

    if p.returncode == 0:
        log.debug('[Execution]: OK')
        return rst, True
    else:
        log.debug('[Execution]: FAILED')
        return None, False
