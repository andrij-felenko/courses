# Перевірка частки запитів у режимі RCU-walk
$ sudo bpftrace -e '
kprobe:lookup_fast {
    @total = count();
    if (arg1 & 0x0040) { // 0x0040 відповідає прапорцю LOOKUP_RCU
        @rcu_walk = count();
    } else {
        @ref_walk = count();
    }
}
interval:s:5 {
    print(@total);
    print(@rcu_walk);
    print(@ref_walk);
    clear(@total); clear(@rcu_walk); clear(@ref_walk);
}'
