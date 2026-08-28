// bpf_tracer.c - Програма BPF на мові C (libbpf)
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

SEC("kprobe/do_sys_openat2")
int BPF_KPROBE(trace_openat2, int dfd, const char *filename) {
    char buf[256];
    bpf_probe_read_user_str(buf, sizeof(buf), filename);
    bpf_printk("Kprobe openat2: %s\n", buf);
    return 0;
}

SEC("uprobe/bash_readline")
int BPF_UPROBE(trace_readline) {
    bpf_printk("Uprobe readline entered\n");
    return 0;
}

SEC("uretprobe/bash_readline")
int BPF_URETPROBE(trace_readline_ret, const char *ret_str) {
    char buf[256];
    bpf_probe_read_user_str(buf, sizeof(buf), ret_str);
    bpf_printk("Uretprobe readline result: %s\n", buf);
    return 0;
}

char _license[] SEC("license") = "GPL";
