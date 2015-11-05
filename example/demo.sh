#!/usr/bin/env bash

set -o errexit

options=""
if [ $1 != "" ]; then
    options=$1
fi

CXX=${CXX:-g++}
CFLAGS=${CFLAGS:--g -O0}
GDB=${GDB:-gdb}

sys=$(uname)
case ${sys} in
    Darwin)
        READLINK=greadlink
        ;;
    Linux)
        READLINK=readlink
        ;;
    *)
        echo "Unsupported system ${sys}"; exit 1
esac

basedir=$(dirname "$(${READLINK} -f "$(dirname $0)")")

echo "Building two-mode demo.."
echo "${CXX} ${CFLAGS} two-mode.cc -o two-mode -pthread -std=c++11"
${CXX} ${CFLAGS} two-mode.cc -o two-mode -pthread -std=c++11
echo "Launching..."
./two-mode &> /dev/null &
pid=$!
sleep 1

function cleanup_and_die {
    [ -z ${pid} ] || kill -TERM ${pid}
}
trap cleanup_and_die SIGINT
trap cleanup_and_die SIGTERM
trap cleanup_and_die EXIT

echo "Running uniq-stacks..."
${GDB} two-mode --pid=${pid} \
    --batch \
    -ex "source ${basedir}/uniq-stacks.py" \
    -ex "uniq-stacks ${options}"
