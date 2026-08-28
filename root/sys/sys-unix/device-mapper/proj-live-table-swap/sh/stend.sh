#!/bin/sh
set -eu

WORK=/var/tmp/dmlab          # тут живуть файли-«носії»
MNT=$WORK/mnt                # сюди монтуємо
NAME=lab                     # → /dev/mapper/lab
BYTES=$((128 * 1024 * 1024)) # по 128 МіБ на файл

mkdir -p "$WORK" "$MNT"
truncate -s "$BYTES" "$WORK/a.img"
truncate -s "$BYTES" "$WORK/b.img"

LOOP_A=$(losetup -f --show "$WORK/a.img")
LOOP_B=$(losetup -f --show "$WORK/b.img")
SZ_A=$(blockdev --getsz "$LOOP_A")     # довжина В СЕКТОРАХ
SZ_B=$(blockdev --getsz "$LOOP_B")
echo "$LOOP_A: $SZ_A   $LOOP_B: $SZ_B"   # /dev/loop0: 262144   /dev/loop1: 262144
