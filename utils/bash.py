# -*- coding: utf-8 -*-

import os
import subprocess
import shlex


def run(cmd):
    print('[Run command]: {}'.format(cmd))
    os.system(cmd)


def run_with_output(cmd, shell=False):
    print('[Run command]: {}'.format(cmd))
    fmt_cmd = shlex.split(cmd)
    p = subprocess.Popen(fmt_cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    rst = []
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if isinstance(line, bytes):
                line = line.decode()
                print('[Output]: {}'.format(line))
                rst.append(line)

    if p.returncode == 0:
        print('[Execution]: OK')
        return rst
    else:
        print('[Execution]: FAILED')
        return None
