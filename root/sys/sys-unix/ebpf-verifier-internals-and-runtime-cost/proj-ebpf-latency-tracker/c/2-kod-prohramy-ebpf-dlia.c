#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

/* Структура події, що надсилається у простір користувача */
struct event_t {
    __u32 pid;
    __u32 tgid;
    __u64 duration_ns;
    __s32 ret_code;
    char comm[16];
};

/* Хеш-карта для збереження часу старту операції: ключ = pid_tgid, значення = u64 */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, __u64);
    __type(value, __u64);
} start_times SEC(".maps");

/* Кільцевий буфер подій */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); /* 256 KB буфер */
} events SEC(".maps");

SEC("kprobe/do_sys_openat2")
int BPF_KPROBE(trace_openat_enter)
{
    __u64 pid_tgid = bpf_get_current_pid_tgid();
    __u64 ts = bpf_ktime_get_ns();

    /* Зберігаємо стартовий час за ідентифікатором потоку */
    bpf_map_update_elem(&start_times, &pid_tgid, &ts, BPF_ANY);
    return 0;
}

SEC("kretprobe/do_sys_openat2")
int BPF_KRETPROBE(trace_openat_exit, long ret)
{
    __u64 pid_tgid = bpf_get_current_pid_tgid();
    __u64 *start_ts = bpf_map_lookup_elem(&start_times, &pid_tgid);

    if (!start_ts) {
        return 0; /* Пропустити, якщо початок операції не зафіксовано */
    }

    __u64 delta_ns = bpf_ktime_get_ns() - *start_ts;

    /* Обов'язкове очищення карти для запобігання витоку пам'яті */
    bpf_map_delete_elem(&start_times, &pid_tgid);

    /* Резервування пам'яті у Ring Buffer без навантаження на стек */
    struct event_t *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) {
        return 0; /* Буфер переповнено */
    }

    e->tgid = pid_tgid >> 32;
    e->pid = (__u32)pid_tgid;
    e->duration_ns = delta_ns;
    e->ret_code = (__s32)ret;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    /* Публікація події */
    bpf_ringbuf_submit(e, 0);
    return 0;
}
