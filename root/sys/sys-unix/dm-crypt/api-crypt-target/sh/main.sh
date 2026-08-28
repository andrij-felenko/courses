truncate -s 64M /tmp/disk.img
loop=$(losetup --find --show /tmp/disk.img)

# ключ: 512 бітів = 64 байти = 128 шістнадцяткових цифр (XTS бере два по 256)
key=$(head -c 64 /dev/urandom | xxd -p -c 64)

# поля: <шифр> <ключ> <зсув IV> <пристрій> <зсув> <к-сть опцій> <опції>
dmsetup create demo --table \
  "0 $(blockdev --getsz $loop) crypt aes-xts-plain64 $key 0 $loop 0 1 sector_size:4096"

dmsetup table demo            # ключ затерто нулями
dmsetup status demo           # порожньо: змінного стану немає
dmsetup remove demo && losetup -d $loop
