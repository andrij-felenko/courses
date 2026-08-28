SRC=/usr/share
OUT=/var/tmp/lab; mkdir -p "$OUT"

for b in 16K 128K 1M; do
  /usr/bin/time -f "%e с" \
    mksquashfs "$SRC" "$OUT/sq-$b.sqfs" -b $b -comp zstd \
               -Xcompression-level 15 -noappend -quiet -no-progress
done

/usr/bin/time -f "%e с" mkfs.erofs -zlz4hc,12 "$OUT/er-lz4hc.erofs" "$SRC"
/usr/bin/time -f "%e с" mkfs.erofs -zlzma,9 -Efragments,dedupe "$OUT/er-lzma.erofs" "$SRC"
