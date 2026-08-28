/* Приклад BPF-ітератора процесів (Kernel Space, C) */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

SEC("iter/task")
int count_high_memory_tasks(struct bpf_iter__task *ctx)
{
    struct seq_file *seq = ctx->meta->seq;
    struct task_struct *task = ctx->task;

    /* task == NULL означає завершення ітерації */
    if (!task)
        return 0;

    struct mm_struct *mm = task->mm;
    if (!mm)
        return 0;

    unsigned long total_vm = 0;
    bpf_probe_read_kernel(&total_vm, sizeof(total_vm), &mm->total_vm);

    /* Фільтрація в ядрі: пропускаємо процеси, що споживають менше 256 МБ */
    if (total_vm < 65536)
        return 0;

    /* Форматуємо лише відібрані об'єкти */
    bpf_seq_printf(seq, "TGID:%d PID:%d COMM:%s PAGES:%lu\n",
                   task->tgid, task->pid, task->comm, total_vm);

    return 0;
}

char _license[] SEC("license") = "GPL";
