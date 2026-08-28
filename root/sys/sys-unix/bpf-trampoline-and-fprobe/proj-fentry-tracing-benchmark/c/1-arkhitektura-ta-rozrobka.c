#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

/* Мапа BPF для збереження результатів вимірювання затримок (в наносекундах) */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 2);
    __type(key, u32);
    __type(value, u64);
} bench_stats SEC(".maps");

/* 
 * 1. ТРАДИЦІЙНИЙ KPROBE
 * Індекс 0 у мапі: накопичує час роботи обробника kprobe
 */
SEC("kprobe/do_sys_openat2")
int BPF_KPROBE(bench_kprobe_entry, int dfd, const char *filename)
{
    u64 ts_start = bpf_ktime_get_ns();
    u32 key = 0;
    u64 *val = bpf_map_lookup_elem(&bench_stats, &key);
    if (val) {
        u64 delta = bpf_ktime_get_ns() - ts_start;
        __sync_fetch_and_add(val, delta);
    }
    return 0;
}

/* 
 * 2. СУЧАСНИЙ FENTRY (BPF Trampoline)
 * Індекс 1 у мапі: накопичує час роботи обробника fentry
 */
SEC("fentry/do_sys_openat2")
int BPF_PROG(bench_fentry_entry, int dfd, const char *filename, struct open_how *how)
{
    u64 ts_start = bpf_ktime_get_ns();
    u32 key = 1;
    u64 *val = bpf_map_lookup_elem(&bench_stats, &key);
    if (val) {
        u64 delta = bpf_ktime_get_ns() - ts_start;
        __sync_fetch_and_add(val, delta);
    }
    return 0;
}
