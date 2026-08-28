mkfs.ext4 -q -b 4096 -L vlab "$LOOP_D"
mount "$LOOP_D" "$MNT"

head -c 40960 /dev/urandom > "$MNT/one.bin"
head -c 40960 /dev/urandom > "$MNT/two.bin"
head -c 40960 /dev/urandom > "$MNT/three.bin"
printf 'MARKER-ONE' | dd of="$MNT/one.bin" bs=1 seek=12288 conv=notrunc status=none

umount "$MNT"
sync
