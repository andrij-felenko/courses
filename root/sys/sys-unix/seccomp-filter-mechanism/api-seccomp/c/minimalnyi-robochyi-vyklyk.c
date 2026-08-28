#define _GNU_SOURCE
#include <errno.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <stddef.h>
#include <stdio.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/utsname.h>
#include <unistd.h>

int main(void)
{
    struct sock_filter code[] = {
        /* 0 */ BPF_STMT(BPF_LD  | BPF_W   | BPF_ABS, offsetof(struct seccomp_data, arch)),
        /* 1 */ BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        /* 2 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        /* 3 */ BPF_STMT(BPF_LD  | BPF_W   | BPF_ABS, offsetof(struct seccomp_data, nr)),
        /* 4 */ BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_uname, 0, 1),
        /* 5 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),
        /* 6 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    struct sock_fprog prog = { .len = sizeof code / sizeof code[0], .filter = code };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0))
        return perror("no_new_privs"), 1;
    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog))
        return perror("seccomp"), 1;

    struct utsname u;
    if (uname(&u) == -1)
        perror("uname");        /* → uname: Operation not permitted */
    return 0;
}
