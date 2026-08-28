# Трасування подій пробудження kswapd та початку Direct Reclaim у реальному часі
sudo bpftrace -e '
tracepoint:vmscan:mm_vmscan_kswapd_wake {
    printf("kswapd woken for node %d, order %d\n", args->nid, args->order);
}
tracepoint:vmscan:mm_vmscan_direct_reclaim_begin {
    printf("Process %s (PID %d) entered Direct Reclaim (order %d)\n", 
           comm, pid, args->order);
}
'
