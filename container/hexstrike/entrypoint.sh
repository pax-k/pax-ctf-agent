#!/bin/sh
set -eu

mkdir -p "${HOME}"
printf '%s\n' 'source /opt/pwndbg/gdbinit.py' > "${HOME}/.gdbinit"

exec "$@"
