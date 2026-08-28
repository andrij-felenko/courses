ct_of() {
    dd if="$IMG" bs=512 skip=$(( HDR + $1 )) count=1 status=none |
        sha256sum | cut -c1-16
}

# той самий текст — в ІНШИЙ сектор
dd if="$WORK/plain.bin" of=/dev/mapper/"$NAME" bs=512 seek=200 count=1 \
   oflag=direct status=none && sync
echo "сектор 100: $(ct_of 100)"     # 4e0b9a13c7f6d2a8
echo "сектор 200: $(ct_of 200)"     # b71c05ee4a930f62   ← інші байти

# той самий текст — У ТОЙ САМИЙ сектор, удруге
dd if="$WORK/plain.bin" of=/dev/mapper/"$NAME" bs=512 seek=100 count=1 \
   oflag=direct status=none && sync
echo "сектор 100: $(ct_of 100)"     # 4e0b9a13c7f6d2a8   ← ті самі байти
