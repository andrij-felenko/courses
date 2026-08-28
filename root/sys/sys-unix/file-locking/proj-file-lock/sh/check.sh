#!/bin/sh
# check.sh — чи справді замок щось міняє.
set -eu
DIR=$(mktemp -d)
N=200          # скільки разів кожен примірник додає одиницю
P=8            # скільки примірників одночасно

run() {
    prog=$1
    : > "$DIR/ctr"; : > "$DIR/log"
    i=0
    while [ "$i" -lt "$P" ]; do
        "./$prog" "$DIR/ctr" "$DIR/log" "$N" &
        i=$((i + 1))
    done
    wait
    printf '%-14s у файлі %-7s рядків %-7s різних чисел %-7s треба %s\n' \
        "$prog" "$(cat "$DIR/ctr")" "$(wc -l < "$DIR/log")" \
        "$(awk '{print $4}' "$DIR/log" | sort -u | wc -l)" "$((P * N))"
}

run counter-flock
run counter-posix
run counter-ofd
run counter-none
rm -rf "$DIR"
