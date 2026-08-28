#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

/* Вхідна структура команди від користувацького простору */
struct policy_command {
    __u32 target_pid;
    __u8  block_action; /* 1 = Block, 0 = Allow */
};

/* Мапа User Ring Buffer для передачі команд у ядро БЕЗ SYSCALL */
struct {
    __uint(type, BPF_MAP_TYPE_USER_RINGBUF);
    __uint(max_entries, 256 * 1024);
} cmd_ringbuf SEC(".maps");

/* Хеш-мапа заблокованих PID */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);
    __type(value, __u8);
} blocked_pids SEC(".maps");

/* 1. BPF Iterator: обхід усіх процесів у ядрі */
SEC("iter/task")
int inspect_tasks(struct bpf_iter__task *ctx)
{
    struct seq_file *seq = ctx->meta->seq;
    struct task_struct *task = ctx->task;

    if (!task)
        return 0;

    /* Читаємо розмір віртуальної пам'яті процесу */
    struct mm_struct *mm = task->mm;
    if (!mm)
        return 0;

    unsigned long total_vm = 0;
    bpf_probe_read_kernel(&total_vm, sizeof(total_vm), &mm->total_vm);

    /* Відбираємо лише процеси, що споживають більше 100 000 сторінок (~400 МБ) */
    if (total_vm > 100000) {
        bpf_seq_printf(seq, "PID:%d COMM:%s PAGES:%lu\n", 
                       task->pid, task->comm, total_vm);
    }

    return 0;
}

/* Callback для обробки кожної команди з User Ring Buffer */
static long process_policy_cmd(struct bpf_dynptr *dynptr, void *context)
{
    struct policy_command cmd;

    /* Безпечне копіювання команди з dynptr з перевіркою меж */
    if (bpf_dynptr_read(&cmd, sizeof(cmd), dynptr, 0, 0) < 0)
        return 0;

    if (cmd.block_action == 1) {
        __u8 flag = 1;
        bpf_map_update_elem(&blocked_pids, &cmd.target_pid, &flag, BPF_ANY);
    } else {
        bpf_map_delete_elem(&blocked_pids, &cmd.target_pid);
    }

    return 0;
}

/* 2. Двигун застосування команд з User Ringbuf */
SEC("tp/syscalls/sys_enter_write")
int apply_user_policies(void *ctx)
{
    /* Вичищаємо та застосовуємо всі накопичені команди з кольца */
    bpf_user_ringbuf_drain(&cmd_ringbuf, process_policy_cmd, NULL, BPF_RB_NO_WAKEUP);
    return 0;
}

char _license[] SEC("license") = "GPL";
