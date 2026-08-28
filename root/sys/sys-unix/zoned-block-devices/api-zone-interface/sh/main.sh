$ d=/sys/block/nullb0/queue
$ for f in zoned chunk_sectors nr_zones max_open_zones max_active_zones \
           zone_append_max_bytes zone_write_granularity; do
      printf '%-24s %s\n' "$f" "$(cat $d/$f)"
  done
zoned                    host-managed
chunk_sectors            524288
nr_zones                 32
max_open_zones           14
max_active_zones         14
zone_append_max_bytes    2097152
zone_write_granularity   4096
