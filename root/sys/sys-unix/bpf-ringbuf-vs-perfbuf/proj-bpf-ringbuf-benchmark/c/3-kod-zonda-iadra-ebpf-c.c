// BPF kernel space code - C only (виняток §5 AUTHORING: простір ядра Linux)
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define TASK_COMM_LEN 16
#define PATH_MAX_LEN 256

// Структура події трасування
struct event_t {
    u64 timestamp_ns;
    u32 pid;
    u32 cpu_id;
    char comm[TASK_COMM_LEN];
    char filename[PATH_MAX_LEN];
};

// 1. Карта BPF Ring Buffer
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 512 * 1024); // 512 КБ глобального буфера
} rb_events SEC(".maps");

// 2. Карта Perf Event Array
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(int));
    __uint(value_size, sizeof(int));
} pb_events SEC(".maps");

SEC("tracepoint/syscalls/sys_enter_openat")
int handle_openat(struct trace_event_raw_sys_enter *ctx) {
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32;

    // --- Сценарій A: BPF Ring Buffer (Zero-Copy) ---
    struct event_t *event = bpf_ringbuf_reserve(&rb_events, sizeof(*event), 0);
    if (event) {
        event->timestamp_ns = bpf_ktime_get_ns();
        event->pid = pid;
        event->cpu_id = bpf_get_smp_processor_id();
        bpf_get_current_comm(&event->comm, sizeof(event->comm));
        
        // Зчитування аргументу filename з простору користувача
        const char *fname_ptr = (const char *)BPF_CORE_READ(ctx, args[1]);
        bpf_probe_read_user_str(&event->filename, sizeof(event->filename), fname_ptr);

        // Публікація без копіювання зі стека!
        bpf_ringbuf_submit(event, 0);
    }

    // --- Сценарій B: Perf Event Array (Копіювання зі стека) ---
    // Увага: структура event_t має розмір ~288 байт. Вона займає більше половини
    // 512-байтового стека BPF, що небезпечно при глибоких викликах!
    struct event_t stack_event = {};
    stack_event.timestamp_ns = bpf_ktime_get_ns();
    stack_event.pid = pid;
    stack_event.cpu_id = bpf_get_smp_processor_id();
    bpf_get_current_comm(&stack_event.comm, sizeof(stack_event.comm));

    bpf_perf_event_output(ctx, &pb_events, BPF_F_CURRENT_CPU, &stack_event, sizeof(stack_event));

    return 0;
}

char LICENSE[] SEC("license") = "GPL";
