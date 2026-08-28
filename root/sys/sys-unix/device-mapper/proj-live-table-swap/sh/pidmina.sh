dmsetup table "$NAME"
#   0 262144 linear 7:0 0
#   262144 262144 linear 7:1 0
blockdev --getsz /dev/mapper/"$NAME"      # 524288 — удвічі більше
findmnt -n -o SOURCE,TARGET "$MNT"        # /dev/mapper/lab /var/tmp/dmlab/mnt

cat <&9 > "$WORK/tail.part"               # дочитуємо ТИМ САМИМ дескриптором
exec 9<&-
if [ "$SUM" = "$(cat "$WORK/head.part" "$WORK/tail.part" |
                 sha256sum | cut -d' ' -f1)" ]; then
    echo "дескриптор доніс той самий файл"
else
    echo "СУМИ РОЗІЙШЛИСЯ" >&2
    exit 1
fi
