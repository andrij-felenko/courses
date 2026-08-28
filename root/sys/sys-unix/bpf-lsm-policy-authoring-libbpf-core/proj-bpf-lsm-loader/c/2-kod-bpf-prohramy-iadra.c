#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

// Структура події аудиту, що передається у User Space
struct audit_event {
    u32 pid;
    u32 ppid;
    u32 uid;
    u32 gid;
    char comm[16];
    char filename[64];
    bool blocked;
};

// Оголошення глобального BPF Ring Buffer на 256 КБ
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256 KB
} audit_ringbuf SEC(".maps");

SEC("lsm/bprm_check_security")
int BPF_PROG(enforce_exec_policy, struct linux_binprm *bprm)
{
    // 1. Отримуємо ідентифікатори поточного процесу та користувача
    u64 uid_gid = bpf_get_current_uid_gid();
    u32 uid = (u32)uid_gid;
    u32 gid = (u32)(uid_gid >> 32);

    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = (u32)(pid_tgid >> 32);

    // 2. Читаємо ім'я файлу виконуваного об'єкта через CO-RE
    const char *fname = BPF_CORE_READ(bprm, filename);
    if (!fname) {
        return 0;
    }

    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));

    // 3. Логіка політики: блокуємо запуск chmod та netcat не-root користувачами (UID != 0)
    bool is_restricted = false;
    
    // Рішення спирається на bprm->filename, а не на comm: у точці виклику хука
    // comm ще містить назву процесу, який викликав execve (наприклад, bash),
    // а на назву нового бінарника ядро змінить її вже після дозволу на запуск.
    char path[64] = {};
    bpf_probe_read_kernel_str(path, sizeof(path), fname);

    if (__builtin_memcmp(path, "/usr/bin/chmod", sizeof("/usr/bin/chmod")) == 0 ||
        __builtin_memcmp(path, "/usr/bin/nc", sizeof("/usr/bin/nc")) == 0 ||
        __builtin_memcmp(path, "/usr/bin/ncat", sizeof("/usr/bin/ncat")) == 0) {
        is_restricted = true;
    }

    bool should_block = (uid != 0) && is_restricted;

    // 4. Формуємо та відправляємо подію у Ring Buffer
    struct audit_event *evt;
    evt = bpf_ringbuf_reserve(&audit_ringbuf, sizeof(*evt), 0);
    if (evt) {
        evt->pid = pid;
        evt->uid = uid;
        evt->gid = gid;
        evt->blocked = should_block;

        // Копіюємо батьківський PID через структуру task_struct
        struct task_struct *task = (struct task_struct *)bpf_get_current_task();
        evt->ppid = BPF_CORE_READ(task, real_parent, tgid);

        // Безпечно зчитуємо рядки з пам'яті ядра
        bpf_probe_read_kernel_str(evt->comm, sizeof(evt->comm), comm);
        bpf_probe_read_kernel_str(evt->filename, sizeof(evt->filename), fname);

        // Публікуємо подію для споживачів у User Space
        bpf_ringbuf_submit(evt, 0);
    }

    // 5. Приймаємо рішення про допуск операції
    if (should_block) {
        bpf_printk("BPF-LSM: DENIED exec '%s' (PID %d, UID %d)\n", comm, pid, uid);
        return -1; // -EPERM (Operation not permitted)
    }

    return 0; // Allow
}
