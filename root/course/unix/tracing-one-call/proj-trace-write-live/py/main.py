#!/usr/bin/env python3
"""Автоматизоване вимірювання затримок write() через BCC."""

from bcc import BPF
import time

bpf_code = """
#include <uapi/linux/ptrace.h>

BPF_HASH(start, u32);
BPF_HISTOGRAM(dist);

int trace_sys_enter_write(struct tracepoint__syscalls__sys_enter_write *args) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 ts = bpf_ktime_get_ns();
    start.update(&pid, &ts);
    return 0;
}

int trace_sys_exit_write(struct tracepoint__syscalls__sys_exit_write *args) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 *tsp = start.lookup(&pid);
    if (tsp != 0) {
        u64 delta = bpf_ktime_get_ns() - *tsp;
        dist.increment(bpf_log2l(delta / 1000)); // затримка в мікросекундах (log2)
        start.delete(&pid);
    }
    return 0;
}
"""

b = BPF(text=bpf_code)
b.attach_tracepoint(tp="syscalls:sys_enter_write", fn_name="trace_sys_enter_write")
b.attach_tracepoint(tp="syscalls:sys_exit_write", fn_name="trace_sys_exit_write")

print("Збір статистики затримок write() (натисніть Ctrl+C для виводу)...")
try:
    time.sleep(5)
except KeyboardInterrupt:
    pass

print("\nРозподіл затримок write() (мікросекунди, log2 масштаб):")
b["dist"].print_log2_hist("мкс")
