# Трасування затримок очікування замків у мікросекундах через eBPF
sudo bpftrace -e '
usdt:/usr/lib/postgresql/16/bin/postgres:postgresql:lock__wait__start {
    @start[tid] = nsecs;
}
usdt:/usr/lib/postgresql/16/bin/postgres:postgresql:lock__wait__done {
    if (@start[tid]) {
        @wait_dist_us = hist((nsecs - @start[tid]) / 1000);
        delete(@start[tid]);
    }
}'
