// BPF-код для ringbuf (Zero-Copy)
SEC("tracepoint/syscalls/sys_enter_openat")
int trace_openat_ringbuf(void *ctx) {
    struct event_t *event;

    // 1. Резервування пам'яті безпосередньо в буфері ядра
    event = bpf_ringbuf_reserve(&rb_map, sizeof(*event), 0);
    if (!event)
        return 0; // Буфер переповнено

    // 2. Прямий запис за адресою буфера (без стека BPF!)
    event->timestamp = bpf_ktime_get_ns();
    event->pid = bpf_get_current_pid_tgid() >> 32;

    // 3. Публікація події
    bpf_ringbuf_submit(event, 0);
    return 0;
}
