#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

/* Визначення структури події */
struct my_event_t {
    __u32 pid;
    __u64 timestamp;
    char comm[16];
};

/* Оголошення PERF_EVENT_ARRAY карти */
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(__u32));
} my_perf_map SEC(".maps");

SEC("kprobe/sys_execve")
int bpf_prog1(struct pt_regs *ctx)
{
    struct my_event_t event = {};

    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.timestamp = bpf_ktime_get_ns();
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    /* Відправка події у userspace */
    bpf_perf_event_output(ctx, &my_perf_map, BPF_F_CURRENT_CPU, &event, sizeof(event));

    return 0;
}

char _license[] SEC("license") = "GPL";
