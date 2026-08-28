/* uprobe_tracer.bpf.c - eBPF програма ядра */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

/* Структура події для відправки у userspace */
struct event {
    u32 pid;
    u64 duration_ns;
};

/* Хеш-карта для збереження часу входу: PID -> start_timestamp */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, u32);
    __type(value, u64);
} entry_times SEC(".maps");

/* Ring Buffer для передачі подій */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} ringbuf SEC(".maps");

/* Uprobe: спрацьовує при вході в compute_hash */
SEC("uprobe/compute_hash")
int BPF_UPROBE(trace_entry) {
    u64 ts = bpf_ktime_get_ns();
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    bpf_map_update_elem(&entry_times, &pid, &ts, BPF_ANY);
    return 0;
}

/* Uretprobe: спрацьовує при виході з compute_hash */
SEC("uretprobe/compute_hash")
int BPF_URETPROBE(trace_exit) {
    u64 exit_ts = bpf_ktime_get_ns();
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    u64 *entry_ts = bpf_map_lookup_elem(&entry_times, &pid);
    if (!entry_ts) {
        return 0; /* Не знайшли вхідної мітки часу */
    }

    u64 duration = exit_ts - *entry_ts;
    bpf_map_delete_elem(&entry_times, &pid);

    /* Зарезервувати місце в Ring Buffer для події */
    struct event *e = bpf_ringbuf_reserve(&ringbuf, sizeof(*e), 0);
    if (!e) {
        return 0;
    }

    e->pid = pid;
    e->duration_ns = duration;
    bpf_ringbuf_submit(e, 0);

    return 0;
}

char _license[] SEC("license") = "GPL";
