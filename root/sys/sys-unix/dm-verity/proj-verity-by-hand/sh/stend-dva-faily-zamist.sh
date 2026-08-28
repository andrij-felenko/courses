#!/bin/sh
set -eu

WORK=/var/tmp/veritylab
MNT=$WORK/mnt
mkdir -p "$WORK" "$MNT"

truncate -s 64M "$WORK/data.img"
truncate -s  1M "$WORK/hash.img"

LOOP_D=$(losetup -f --show "$WORK/data.img")
LOOP_H=$(losetup -f --show "$WORK/hash.img")
echo "$LOOP_D $LOOP_H"            # /dev/loop0 /dev/loop1
