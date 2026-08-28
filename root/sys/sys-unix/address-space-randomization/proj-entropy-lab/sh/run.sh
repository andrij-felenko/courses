#!/bin/sh
# run.sh — N прогонів зонда з байт-у-байт однаковим оточенням.
#   sh run.sh 500 ./probe > plain.txt
N=${1:-500}
BIN=${2:-./probe}

i=0
while [ "$i" -lt "$N" ]; do
	env -i "$BIN"
	i=$((i + 1))
done
