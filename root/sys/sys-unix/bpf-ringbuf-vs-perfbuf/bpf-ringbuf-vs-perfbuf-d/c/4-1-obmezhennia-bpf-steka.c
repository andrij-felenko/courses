// BPF-код для perfbuf (копіювання зі стека)
SEC("tracepoint/syscalls/sys_enter_openat")
int trace_openat_perfbuf(void *ctx) {
    struct event_t event = {}; // Виділення структури на стеку BPF!
    
    // Заповнення полів...
    event.timestamp = bpf_ktime_get_ns();
    event.pid = bpf_get_current_pid_tgid() >> 32;

    // Копіювання 288 байтів зі стека у буфер perf
    bpf_perf_event_output(ctx, &pb_map, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}
