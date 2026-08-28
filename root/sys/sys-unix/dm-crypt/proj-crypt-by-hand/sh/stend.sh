#!/bin/sh
set -eu

WORK=/var/tmp/cryptlab
IMG=$WORK/disk.img
NAME=byhand                  # → /dev/mapper/byhand
HDR=2048                     # секторів образу, відданих «під заголовок»
SECTORS=8192                 # довжина шифрованого пристрою, у секторах

mkdir -p "$WORK"
truncate -s $(( (HDR + SECTORS) * 512 )) "$IMG"
LOOP=$(losetup -f --show "$IMG")

( umask 077; dd if=/dev/urandom of="$WORK/key.bin" bs=64 count=1 status=none )
KEY=$(od -An -tx1 -v "$WORK/key.bin" | tr -d ' \n')
[ ${#KEY} -eq 128 ] || { echo "ключ мусить дати 128 шістнадцяткових цифр" >&2; exit 1; }
