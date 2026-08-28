#!/bin/sh
set -eu

WORK=/var/tmp/mplab
IMG=$WORK/lun.img

mkdir -p "$WORK"
truncate -s 128M "$IMG"            # файл заявленої довжини, поки що порожній
modprobe dm-multipath
modprobe dm-round-robin

LOOP_A=$(losetup -f --show "$IMG") # /dev/loop0
LOOP_B=$(losetup -f --show "$IMG") # /dev/loop1 — ТОЙ САМИЙ файл
SZ=$(blockdev --getsz "$LOOP_A")   # 262144 — довжина В СЕКТОРАХ

dmsetup create patha --table "0 $SZ linear $LOOP_A 0"
dmsetup create pathb --table "0 $SZ linear $LOOP_B 0"
