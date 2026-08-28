#!/usr/bin/env bash
set -euo pipefail

# Відкриваємо дескриптор 19 для запису у виділений файл трасування
exec 19> "/tmp/deployment_trace_$$.log"
export BASH_XTRACEFD=19

set -x
echo "Цей рядок іде у стандартний вивід"
ls /etc/hosts
# Усі службові рядки '+' опиняються у файлі /tmp/deployment_trace_$$.log
