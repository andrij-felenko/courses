#include <scx/common.bpf.h>

char _license[] SEC("license") = "GPL";

// Структура події, що передається через Ring Buffer у User Space
struct task_queued_event {
    s32 pid;
    s32 cpu;
    u64 flags;
};

// BPF Ring Buffer для передачі подій у простір користувача
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} event_ringbuf SEC(".maps");

// BPF Array для збереження обраного PID для кожного виконуючого CPU
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1024); // Підтримка до 1024 ядер CPU
    __type(key, u32);
    __type(value, s32);
} cpu_decision_map SEC(".maps");

s32 BPF_STRUCT_OPS(rustland_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    // Зауваження: Повертаємо попередній CPU як підказку ядра
    return prev_cpu;
}

void BPF_STRUCT_OPS(rustland_enqueue, struct task_struct *p, u64 enq_flags)
{
    struct task_queued_event *ev;

    // Резервуємо слот у кільцевому буфері подій
    ev = bpf_ringbuf_reserve(&event_ringbuf, sizeof(*ev), 0);
    if (!ev) {
        // Якщо буфер переповнено, аварійно відправляємо задачу в глобальну чергу ядра
        scx_bpf_dispatch(p, SCX_DSQ_GLOBAL, SCX_SLICE_DFL, enq_flags);
        return;
    }

    ev->pid = p->pid;
    ev->cpu = scx_bpf_task_cpu(p);
    ev->flags = enq_flags;

    // Публікуємо подію для демона у просторі користувача
    bpf_ringbuf_submit(ev, 0);
}

void BPF_STRUCT_OPS(rustland_dispatch, s32 cpu, struct task_struct *prev)
{
    u32 key = cpu;
    s32 *target_pid;
    struct task_struct *p;

    // Вичитати рішення демона Rust для поточного процесора
    target_pid = bpf_map_lookup_elem(&cpu_decision_map, &key);
    if (target_pid && *target_pid > 0) {
        p = bpf_task_from_pid(*target_pid);
        if (p) {
            // Рішення є: кладемо саме цю задачу в локальну DSQ цього CPU
            scx_bpf_dispatch(p, SCX_DSQ_LOCAL, SCX_SLICE_DFL, 0);
            bpf_task_release(p);
        }
        // Комірку звільняємо лише після спроби диспетчеризації
        *target_pid = 0;
    }

    // Вичитуємо чергу ядра для забезпечення постійного просування задач
    scx_bpf_consume(SCX_DSQ_GLOBAL);
}

SEC(".struct_ops.link")
struct sched_ext_ops rustland_ops = {
    .select_cpu = (void *)rustland_select_cpu,
    .enqueue    = (void *)rustland_enqueue,
    .dispatch   = (void *)rustland_dispatch,
    .name       = "rustland",
};
