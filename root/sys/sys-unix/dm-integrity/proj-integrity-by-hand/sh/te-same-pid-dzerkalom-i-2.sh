OFF=$(grep -abo '^3999$' /var/tmp/leg0.img | head -1 | cut -d: -f1)
printf 'X' | sudo dd of=/var/tmp/leg0.img bs=1 seek="$OFF" \
     conv=notrunc status=none
# …відкрити обидві цілі, зібрати масив, змонтувати…

sudo sha256sum /mnt/int/probe.txt        # той самий, що й до псування
MD=$(basename "$(readlink -f /dev/md/itest)")
echo check | sudo tee /sys/block/$MD/md/sync_action
cat /sys/block/$MD/md/mismatch_cnt
sudo dmesg | grep -E 'Checksum failed|read error corrected'
# device-mapper: integrity: dm-1: Checksum failed at sector 0x1a48
# md/raid1:md127: read error corrected (8 sectors at 6728 on dm-1)
