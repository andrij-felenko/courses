# Գ�������� ��������� ������� (seccomp)

<preknowlist>
- [��������� ���� Linux](book:unix-linux/kernel-and-userspace) � ����� ������� ��������� ������� �� VFS.
- [������: �� �� ��������](book:unix-linux/process-model) � ������ ���� ������� �������� ������, ����������� � ������ ����, � ���� �� � ��������, �� ��� �������� ���������.
- [���� ���� � �� �� ����������](book:unix-linux/permission-bits) � ������ �� ����� ����� ����� ��� �� ���������� �������� / ����� / �����.
- [��������� (capabilities) ������ ����������� root](book:unix-linux/capabilities) � �������� root ������� �� ����� ������������, � `CAP_SYS_ADMIN` � ���� � ���.
- [������: ���������� ���������](book:unix-linux/signal-model) � ���� �쳺 ��������� ���� ��������� � ������� ���� ����� � �������� ��� �������.
</preknowlist>

������� ���������� ������� �� ��� ���� Linux ���������� �������� ��������� ������� ��� ��������� ������� �� �������� �������. ����� �� ������������ ��������� � **seccomp** (Secure Computing Mode).

����� ������ ����������� �������� � ������ �� ��� ��������. ³� ������ �� ������� ������������, �� �� ������ ��������� �����������, ����䳺 ���� ������� ���������� �����. ����� ������� ���� �������� ��������� JPEG, ������� ����������� �� ������������ ������ � � ���������� ������ ������� ��� ��������� ����� �������. �� ���� ��������? �� ��������� ������� �� ����� � ����� ������. ��� �� ����� �� ����. ���� � �� ��������, �� ���������� � ���� ������ ������, �� ���� ���������� �����. � ��������� Linux �� x86-64 ����� 300 ����� ����� � ����. ��� ������ ����������� �������. ����� � �� ���, ���� ��� ������ �� ����� ���������, ��� ������ �� �������. ���� ��� ������� seccomp.

## ������ ������: SECCOMP_MODE_STRICT �� SECCOMP_MODE_FILTER

Seccomp ������ � ���� �������� �������, �� ����������� ��������� �������� `prctl` ��� `seccomp`.

### SECCOMP_MODE_STRICT

������������� � ��� Linux 2.6.12 (2005 ��), ��� ����� �������� ���� ������ �������: `read`, `write`, `_exit` �� `rt_sigreturn`. ����-���� ����� � �������� `SIGKILL`.


```c
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <unistd.h>
#include <stdio.h>

int main() {
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT) == -1) {
        perror("prctl");
        return 1;
    }
    write(1, "Strict mode activated!\n", 23);
    getpid(); // SIGKILL
    return 0;
}
```


### SECCOMP_MODE_FILTER (seccomp-bpf)

�'������ � Linux 3.5 (2012). �������� ����������� �������� BPF, ��� �������� �� �������� �������. ��� ������������ ������� ������� `CAP_SYS_ADMIN` ��� ��������� `PR_SET_NO_NEW_PRIVS`. 

## ��������� seccomp_data

���� ������ ������ ������, ���� ����� ��������� `seccomp_data` �� ������ �� BPF-�������:

```c
struct seccomp_data {
    int   nr;                   /* ����� ������� */
    __u32 arch;                 /* ����������� ��������� */
    __u64 instruction_pointer;  /* �������� �� ���������� */
    __u64 args[6];              /* ��������� (�������� 6) */
};
```

Գ���� ���������� **��** ��������� �������. ���'��� ������� ������� � seccomp BPF �� ���� ����������� ���������. �� ������� ����� ������� ���� *TOCTOU (Time-Of-Check to Time-Of-Use)*.

## ĳ� ��� ��������� (Return Values)

BPF-������ ������� 32-���� ��������. ��������� 16 �� ���������� ��:
1. **`SECCOMP_RET_KILL_PROCESS`**: ����� ���� ������.
2. **`SECCOMP_RET_KILL_THREAD`**: ����� ���� ����, �� ������ ������.
3. **`SECCOMP_RET_TRAP`**: ������� `SIGSYS`.
4. **`SECCOMP_RET_ERRNO`**: ������ �� ����������, ������� ������� `errno`.
5. **`SECCOMP_RET_TRACE`**: ������� ��� `ptrace`.
6. **`SECCOMP_RET_LOG`**: �������� ������, ��� ������ � �����.
7. **`SECCOMP_RET_ALLOW`**: ������ �����.

## ������������ libseccomp

��������� ����� BPF ���������� �������� �� �������. ��������� `libseccomp` �������� �� ����������.

```c
#include <seccomp.h>
#include <stdio.h>
#include <unistd.h>

int main() {
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
    if (!ctx) return 1;

    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
    
    if (seccomp_load(ctx) < 0) {
        seccomp_release(ctx);
        return 1;
    }
    seccomp_release(ctx);

    printf("Seccomp �����������!\n");
    getpid(); // SIGSYS
    return 0;
}
```

## ������������ � �����������

Docker �� ������������� ��������� seccomp-�������, �������� ���������� �������: `mount`, `kexec_load`, `bpf`, `ptrace`, `userfaultfd`, `clone` (� `CLONE_NEWUSER`).

Seccomp-BPF � �� ������� ���'�� ����� ������������ ������������, �� ��������� ���������� �������� �������.
