/* Kernel C: eBPF Tracepoint for socket connect audit */
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

SEC("tracepoint/syscalls/sys_enter_connect")
int trace_connect(struct trace_event_raw_sys_enter *ctx) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    struct sockaddr_in *user_addr = (struct sockaddr_in *)ctx->args[1];
    
    u32 dest_ip = 0;
    u16 dest_port = 0;
    bpf_probe_read_user(&dest_ip, sizeof(dest_ip), &user_addr->sin_addr.s_addr);
    bpf_probe_read_user(&dest_port, sizeof(dest_port), &user_addr->sin_port);
    
    bpf_trace_printk("C2 Probe DETECTED: PID %d -> IP %x:%d\n", 
                     pid_tgid >> 32, dest_ip, dest_port);
    return 0;
}

char _license[] SEC("license") = "GPL";
