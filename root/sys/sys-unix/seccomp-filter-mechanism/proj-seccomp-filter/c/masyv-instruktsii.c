#define _GNU_SOURCE
#include <errno.h>
#include <stddef.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>

#define X32_BIT 0x40000000

#define ALLOW(name)                                             \
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_##name, 0, 1),     \
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)

static struct sock_filter filter[] = {
    /* 0 */ BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
                     offsetof(struct seccomp_data, arch)),
    /* 1 */ BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
    /* 2 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

    /* 3 */ BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
                     offsetof(struct seccomp_data, nr)),
    /* 4 */ BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, X32_BIT, 0, 1),
    /* 5 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

    ALLOW(read),    ALLOW(write),   ALLOW(close),  ALLOW(lseek),
    ALLOW(fstat),   ALLOW(mmap),    ALLOW(munmap), ALLOW(brk),
    ALLOW(rt_sigreturn), ALLOW(exit_group),

    BPF_STMT(BPF_RET | BPF_K,
             SECCOMP_RET_ERRNO | (ENOSYS & SECCOMP_RET_DATA)),
};

static int lock_down(void)
{
    struct sock_fprog prog = {
        .len    = (unsigned short)(sizeof filter / sizeof filter[0]),
        .filter = filter,
    };
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0)
        return -1;
    return syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog);
}
