#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

// vmlinux.h не містить макросів errno — потрібні коди оголошуємо самі
#define EACCES 13

char _license[] SEC("license") = "GPL";

// Структура події аудиту для передачі в userspace
struct audit_event {
    u32 pid;
    u32 ppid;
    u32 uid;
    u32 action; // 0 = Allowed, 1 = Denied (Blocked)
    char comm[16];
    char filename[256];
};

// BPF Ring Buffer для аудиту
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256 KB
} audit_ringbuf SEC(".maps");

// Сховище для підрахунку кількості спроб запуску на рівні task_struct
struct {
    __uint(type, BPF_MAP_TYPE_TASK_STORAGE);
    __uint(map_flags, BPF_F_NO_PREALLOC);
    __type(key, int);
    __type(value, u64);
} task_exec_count SEC(".maps");

SEC("lsm/bprm_check_security")
int BPF_PROG(restrict_exec, struct linux_binprm *bprm)
{
    u64 uid_gid = bpf_get_current_uid_gid();
    u32 uid = (u32)uid_gid;
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = (u32)(pid_tgid >> 32);

    struct task_struct *current_task = (struct task_struct *)bpf_get_current_task_btf();
    
    // Інкремент лічильника в локальному сховищі процесу
    u64 *count = bpf_task_storage_get(&task_exec_count, current_task, 0, BPF_LOCAL_STORAGE_GET_F_CREATE);
    if (count) {
        __sync_fetch_and_add(count, 1);
    }

    // Буфер для зчитування шляху файлу
    char path_buf[256] = {};
    long ret = bpf_d_path(&bprm->file->f_path, path_buf, sizeof(path_buf));
    
    // Префікс каталогу /tmp для блокування
    const char tmp_prefix[] = "/tmp/";
    bool is_tmp = true;

    if (ret > 0) {
        #pragma unroll
        for (int i = 0; i < 5; i++) {
            if (path_buf[i] != tmp_prefix[i]) {
                is_tmp = false;
                break;
            }
        }
    } else {
        is_tmp = false;
    }

    // Виділення місця в Ring Buffer для події аудиту
    struct audit_event *event;
    event = bpf_ringbuf_reserve(&audit_ringbuf, sizeof(*event), 0);
    if (event) {
        event->pid = pid;
        event->ppid = BPF_CORE_READ(current_task, real_parent, tgid);
        event->uid = uid;
        bpf_get_current_comm(&event->comm, sizeof(event->comm));

        if (ret > 0) {
            bpf_probe_read_kernel_str(event->filename, sizeof(event->filename), path_buf);
        } else {
            event->filename[0] = '\0';
        }

        if (is_tmp) {
            event->action = 1; // Blocked
        } else {
            event->action = 0; // Allowed
        }

        bpf_ringbuf_submit(event, 0);
    }

    // Блокування виконання файлів із /tmp повернувши -EACCES
    if (is_tmp) {
        return -EACCES;
    }

    return 0; // Дозвіл для решти бінарних файлів
}
