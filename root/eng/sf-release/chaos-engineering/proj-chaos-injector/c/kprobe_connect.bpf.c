/* Простір ядра: eBPF kprobe-перехоплювач (kprobe_connect.bpf.c) */
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

extern u32 target_chaos_pid;

SEC("kprobe/__x64_sys_connect")
int BPF_KPROBE(trace_connect, struct pt_regs *regs) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    if (pid == target_chaos_pid) {
        /* Примусово підміняємо результат виконання ядра на помилку тайм-ауту */
        bpf_override_return(regs, -ETIMEDOUT);
        return 0;
    }
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
