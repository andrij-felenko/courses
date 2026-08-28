#!/bin/sh
set -eu

WORK=/var/tmp/thinlab
mkdir -p "$WORK"

BLK=1024                                 # розмір блока пулу, у секторах → 512 КіБ
truncate -s 8M   "$WORK/meta.img"
truncate -s 512M "$WORK/data.img"        # рівно 1024 блоки
META=$(losetup -f --show "$WORK/meta.img")
DATA=$(losetup -f --show "$WORK/data.img")

dd if=/dev/zero of="$META" bs=4096 count=1 conv=fsync status=none
