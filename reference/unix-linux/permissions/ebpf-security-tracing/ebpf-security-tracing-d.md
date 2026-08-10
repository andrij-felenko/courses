# eBPF у безпеці та трасуванні

<preknowlist>
- [Що таке eBPF (Extended Berkeley Packet Filter)](book:observability/ebpf-extended-berkeley-packet-filter)
- [LSM (Linux Security Modules) фреймворк](book:permissions/lsm-framework)
- [Процеси, credentials, UIDs](book:permissions/process-credentials-uids-gids)
</preknowlist>

Традиційні системи безпеки Linux, такі як SELinux чи AppArmor, покладаються на статичні правила. З розвитком хмарних середовищ та мікросервісів з'явилася потреба в динамічному, програмованому контролі доступу та моніторингу. **eBPF (Extended Berkeley Packet Filter)** дозволяє безпечно виконувати користувацький код всередині ядра Linux, не змінюючи його вихідний код і не завантажуючи модулі ядра (LKM).

У контексті безпеки eBPF дозволяє не лише спостерігати за поведінкою системи (трасування), а й активно втручатися (LSM BPF). Це дає змогу створювати інструменти на кшталт **Tetragon** та **Falco**, які відстежують виконання процесів, мережеву активність та зміну привілеїв у реальному часі.

## Механізми eBPF для безпеки

### 1. Kprobes та Tracepoints для моніторингу
Перші інструменти безпеки на базі eBPF використовували `kprobes` (kernel probes) та `tracepoints` для перехоплення системних викликів. Наприклад, коли процес викликає `execve`, eBPF-програма може зчитати аргументи виклику і передати їх у простір користувача для аналізу.

### 2. LSM BPF Hooks (активний контроль)
Починаючи з Linux 5.7, з'явився механізм **BPF LSM**. На відміну від `kprobes`, які створені для спостереження, BPF LSM інтегрується безпосередньо у фреймворк Linux Security Modules. Це дозволяє eBPF-програмам повертати код помилки (наприклад, `-EPERM`), активно блокуючи дію до її виконання.

## Відстеження виконання процесів

Відстеження запуску нових процесів — базова задача безпеки. Інструменти перехоплюють виклики `execve` або хуки `bprm_check_security`.

:::tabs
@tab C (eBPF код)
```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

SEC("lsm/bprm_check_security")
int BPF_PROG(restrict_exec, struct linux_binprm *bprm)
{
    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));
    
    // Блокування виконання для певних процесів
    if (comm[0] == 'b' && comm[1] == 'a' && comm[2] == 'd') {
        return -EPERM;
    }
    
    return 0;
}

char _license[] SEC("license") = "GPL";
```
@tab Python (BCC Space)
```python
from bcc import BPF

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

int trace_exec(struct pt_regs *ctx) {
    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));
    bpf_trace_printk("Executed: %s\\n", comm);
    return 0;
}
"""
b = BPF(text=bpf_text)
b.attach_kprobe(event=b.get_syscall_fnname("execve"), fn_name="trace_exec")
print("Tracing execve... Ctrl-C to exit.")
b.trace_print()
```
@tab Go (Cilium ebpf)
```go
package main

import (
	"log"
	"github.com/cilium/ebpf/link"
)

//go:generate go run github.com/cilium/ebpf/cmd/bpf2go bpf restrict_exec.c

func main() {
	objs := bpfObjects{}
	loadBpfObjects(&objs, nil)
	defer objs.Close()

	l, err := link.AttachLSM(link.LSMOptions{
		Program: objs.RestrictExec,
	})
	if err != nil {
		log.Fatal(err)
	}
	defer l.Close()
	// ... loop
}
```
:::

## Відстеження змін привілеїв (Credential Tracking)

Атаки з підвищенням привілеїв часто включають зміну UID/GID процесу (наприклад, експлуатація вразливості для отримання root). eBPF може відстежувати хуки на кшталт `commit_creds` або перехоплювати системні виклики `setuid`.

## Інструменти екосистеми

- **Falco:** Стандарт де-факто для виявлення загроз у Kubernetes. Використовує eBPF kprobes для аналізу системних викликів, порівнюючи їх із правилами (наприклад, "запуск shell у контейнері").
- **Tetragon (від Cilium):** Забезпечує безпеку на рівні виконання, використовуючи глибоку інтеграцію з BPF LSM. На відміну від інструментів на базі kprobes, Tetragon може синхронно блокувати підозрілі події.
