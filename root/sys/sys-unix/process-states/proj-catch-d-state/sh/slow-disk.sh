#!/bin/bash
# slow-disk.sh — потрібні права root. Робить D, з якого не виводить SIGKILL.
set -e
IMG=/var/tmp/slow.img

modprobe dm-delay || true
truncate -s 64M "$IMG"
LOOP=$(losetup --find --show "$IMG")
dmsetup create slowdisk --table "0 $(blockdev --getsz "$LOOP") delay $LOOP 0 3000"

dd if=/dev/mapper/slowdisk of=/dev/null bs=4k count=1 iflag=direct &
victim=$!

sleep 0.5
echo "--- поки триває читання:"
ps -o pid,stat,wchan:28,comm -p $victim

kill -9 $victim
sleep 0.5
echo "--- через півсекунди після kill -9:"
ps -o pid,stat,wchan:28,comm -p $victim

wait $victim || true
echo "--- операція завершилася — аж тепер сигнал подіяв"

dmsetup remove slowdisk
losetup -d "$LOOP"
rm -f "$IMG"
