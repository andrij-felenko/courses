for i in 0 1; do
  sudo truncate -s 256M /var/tmp/leg$i.img
  L=$(sudo losetup --find --show /var/tmp/leg$i.img)
  sudo integritysetup format --batch-mode --integrity crc32c \
       --sector-size 4096 "$L"
  sudo integritysetup open "$L" leg$i
done

sudo mdadm --create /dev/md/itest --level=1 --raid-devices=2 \
     --metadata=1.2 /dev/mapper/leg0 /dev/mapper/leg1
sudo mkfs.ext4 -q /dev/md/itest && sudo mount /dev/md/itest /mnt/int
seq 1 4000 | sudo tee /mnt/int/probe.txt >/dev/null
sudo sync && sudo umount /mnt/int && sudo mdadm --stop /dev/md/itest
sudo integritysetup close leg0 && sudo integritysetup close leg1
