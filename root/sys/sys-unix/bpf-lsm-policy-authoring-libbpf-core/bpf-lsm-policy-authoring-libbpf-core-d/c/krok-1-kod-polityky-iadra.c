#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

SEC("lsm/bprm_check_security")
int BPF_PROG(restrict_chmod_exec, struct linux_binprm *bprm)
{
    // 1. Отримуємо UID користувача, що викликає execve
    u64 uid_gid = bpf_get_current_uid_gid();
    u32 uid = (u32)uid_gid;

    // Якщо це root (UID 0), пропускаємо без перевірок
    if (uid == 0) {
        return 0;
    }

    // 2. Читаємо шлях бінарника, який ядро збирається запустити.
    //    comm тут ще зберігає назву процесу, що викликав execve (bash),
    //    тому рішення спирається саме на bprm->filename
    const char *fname = BPF_CORE_READ(bprm, filename);
    char path[32] = {};
    if (bpf_probe_read_kernel_str(path, sizeof(path), fname) < 0) {
        return 0;
    }

    // 3. Порівнюємо шлях із цільовим разом із завершальним нулем:
    //    цикл зі сталою межею верифікатор розгортає й пропускає
    const char target[] = "/usr/bin/chmod";
    bool match = true;
    for (unsigned i = 0; i < sizeof(target); i++) {
        if (path[i] != target[i]) {
            match = false;
        }
    }

    if (match) {

        bpf_printk("BPF-LSM: BLOCKED execution of chmod by UID %d\n", uid);
        
        // Повертаємо -EPERM (Operation not permitted) для блокування
        return -1;
    }

    return 0;
}
