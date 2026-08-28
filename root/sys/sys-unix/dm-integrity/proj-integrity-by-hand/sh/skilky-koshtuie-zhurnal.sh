run() {   # $1 — зайві прапорці формату («» або --integrity-bitmap-mode)
  sudo integritysetup format --batch-mode --integrity crc32c \
       --sector-size 4096 $1 /dev/loop0
  sudo integritysetup open $1 /dev/loop0 int0
  w0=$(awk '{print $7}' /sys/block/loop0/stat)
  sudo dd if=/dev/zero of=/dev/mapper/int0 bs=1M count=128 \
       oflag=direct conv=fsync
  w1=$(awk '{print $7}' /sys/block/loop0/stat)
  echo "на носій пішло $(( (w1-w0)/2048 )) МіБ на 128 МіБ корисних"
  sudo integritysetup close int0
}

sudo losetup -d /dev/loop0 && sudo rm -f /var/tmp/int0.img
sudo fallocate -l 512M /var/tmp/int0.img          # не діркавий, а справжній
sudo losetup --direct-io=on --find --show /var/tmp/int0.img
# /dev/loop0

run ""                            # журнальний режим
run "--integrity-bitmap-mode"     # бітова мапа
