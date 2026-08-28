// eBPF програма ядра (scx_simple.bpf.c)
#include <scx/common.bpf.h>

char _license[] SEC("license") = "GPL";

// Вибір CPU при пробудженні задачі
s32 BPF_STRUCT_OPS(simple_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    bool is_idle = false;
    s32 cpu;

    // Стандартна ядрова евристика; is_idle каже, чи обране ядро простоює
    cpu = scx_bpf_select_cpu_dfl(p, prev_cpu, wake_flags, &is_idle);

    // Ядро вільне — кладемо задачу просто в його локальну DSQ,
    // тоді ядро навіть не викличе enqueue для цієї задачі
    if (is_idle)
        scx_bpf_dispatch(p, SCX_DSQ_LOCAL, SCX_SLICE_DFL, 0);

    return cpu;
}

// Додавання задачі в чергу готовності
void BPF_STRUCT_OPS(simple_enqueue, struct task_struct *p, u64 enq_flags)
{
    // Відправляємо задачу в глобальну чергу SCX_DSQ_GLOBAL із дефолтним квантом часу
    scx_bpf_dispatch(p, SCX_DSQ_GLOBAL, SCX_SLICE_DFL, enq_flags);
}

// Диспетчеризація задачі на вільний CPU
void BPF_STRUCT_OPS(simple_dispatch, s32 cpu, struct task_struct *prev)
{
    // Автоматично витягуємо задачу з глобальної черги ядра
    scx_bpf_consume(SCX_DSQ_GLOBAL);
}

SEC(".struct_ops.link")
struct sched_ext_ops simple_ops = {
    .select_cpu = (void *)simple_select_cpu,
    .enqueue    = (void *)simple_enqueue,
    .dispatch   = (void *)simple_dispatch,
    .name       = "simple",
};
