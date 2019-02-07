#!/bin/bash

ROOT=$(cd $(dirname $0) 2>&1 > /dev/null; pwd)
PYTHON=""

# quick & dirty workaround, for missing coreutils under macOS
if [[ ! -n "$(command -v realpath)" ]]; then
  function realpath() {
    # pop -* options
    while true;
    do
      if [[ "$1" == "-"* ]]; then
        shift
      else
        break
      fi
    done
    pushd . > /dev/null
    if [ -d "$1" ]; then
      cd "$1"
      dirs -l +0
    else
      cd "`dirname \"$1\"`"
      cur_dir=`dirs -l +0`
      if [ "$cur_dir" == "/" ]; then
        echo "$cur_dir`basename \"$1\"`"
      else
        echo "$cur_dir/`basename \"$1\"`"
      fi
    fi
    popd > /dev/null;
  }

fi

if [[ -x $ROOT/../.virtualenv/bin/python ]]; then
  PYTHON=$(realpath "$ROOT/../.virtualenv/bin/python" -L -s)
fi

# echo "python binary: $PYTHON"
