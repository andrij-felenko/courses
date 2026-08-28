#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define MAX_FILENAME_LEN 256
#define TASK_COMM_LEN 16

// Структура події аудиту, що передається у простір користувача.
// Те саме оголошення винесено у спільний заголовок exec_event.h, який включає завантажувач.
struct exec_event {
    u32 pid;
    u32 ppid;
    u32 uid;
    u32 gid;
    char comm[TASK_COMM_LEN];
    char filename[MAX_FILENAME_LEN];
};

// Оголошення мапи Ring Buffer на 256 КБ
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

// Tracepoint перехоплення входження у sys_enter_execve
SEC("tp/syscalls/sys_enter_execve")
int trace_execve(struct trace_event_raw_sys_enter *ctx)
{
    struct exec_event *event;
    struct task_struct *task;
    const char *filename_ptr;

    // 1. Зарезервувати ділянку пам'яті у Ring Buffer
    event = bpf_ringbuf_reserve(&rb, sizeof(*event), 0);
    if (!event) {
        // Якщо кільцевий буфер переповнений, відкидаємо подію
        return 0;
    }

    // 2. Зчитати ідентифікатори PID (tgid) та TID (pid)
    u64 pid_tgid = bpf_get_current_pid_tgid();
    event->pid = pid_tgid >> 32;

    // 3. Зчитати ідентифікатори UID та GID
    u64 uid_gid = bpf_get_current_uid_gid();
    event->uid = (u32)uid_gid;
    event->gid = uid_gid >> 32;

    // 4. Отримати вказівник на структуру task_struct поточного процесу
    task = (struct task_struct *)bpf_get_current_task();

    // 5. Витягти PPID батьківського процесу через CO-RE читання task->real_parent->tgid
    // Використання real_parent ізолює від тимчасової зміни батька при ptrace-налагодженні
    event->ppid = BPF_CORE_READ(task, real_parent, tgid);

    // 6. Зчитати коротку назву виконуваного файла (comm)
    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    // 7. Зчитати шлях до виконуваного файла з аргументів системного виклику (args[0])
    filename_ptr = (const char *)ctx->args[0];
    bpf_probe_read_user_str(&event->filename, sizeof(event->filename), filename_ptr);

    // 8. Зафіксувати та відправити подію у Ring Buffer
    bpf_ringbuf_submit(event, 0);
    return 0;
}

char _license[] SEC("license") = "GPL";
