#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "execve_event.h"

/* Оголошення карти BPF_MAP_TYPE_PERF_EVENT_ARRAY */
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(__u32));
} events SEC(".maps");

SEC("tracepoint/syscalls/sys_enter_execve")
int tracepoint_sys_enter_execve(void *ctx)
{
    struct execve_event event = {};
    __u64 pid_tgid = bpf_get_current_pid_tgid();

    /* Витягуємо PID (старші 32 біти) та TGID */
    event.pid = (__u32)(pid_tgid >> 32);
    event.ppid = 0; /* У повноцінних проектах ppid витягують з task_struct */
    event.boot_time_ns = bpf_ktime_get_ns();
    
    /* Отримуємо назву поточного процесу */
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    /* Запис у кільцевий буфер поточного процесора */
    long err = bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    if (err) {
        /* При від'ємному значення err запис не вдався (наприклад, ENOSPC при переповненні) */
    }

    return 0;
}

char _license[] SEC("license") = "GPL";
