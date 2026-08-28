s32 BPF_STRUCT_OPS(my_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    bool is_idle = false;
    s32 cpu;

    // Викликаємо стандартний хелпер ядра для пошуку вільного ядра
    cpu = scx_bpf_select_cpu_dfl(p, prev_cpu, wake_flags, &is_idle);

    if (is_idle) {
        // Якщо знайдено вільне ядро, відразу відправляємо завдання на нього
        scx_bpf_dispatch(p, SCX_DSQ_LOCAL, SCX_SLICE_DFL, 0);
    }

    return cpu;
}
