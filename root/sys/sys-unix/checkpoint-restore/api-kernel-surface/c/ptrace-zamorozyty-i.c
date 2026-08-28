#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <elf.h>
#include <stdio.h>

int freeze_and_peek(pid_t pid, struct user_regs_struct *out)
{
    int status;

    /* приєднання, яке НЕ видно ззовні: стан зупинки не змінюється */
    if (ptrace(PTRACE_SEIZE, pid, 0, 0) < 0)
        return -1;

    /* зупинка без сигналу */
    if (ptrace(PTRACE_INTERRUPT, pid, 0, 0) < 0)
        return -1;
    waitpid(pid, &status, __WALL);

    struct iovec iov = { .iov_base = out, .iov_len = sizeof *out };
    if (ptrace(PTRACE_GETREGSET, pid, (void *) NT_PRSTATUS, &iov) < 0)
        return -1;

    ptrace(PTRACE_DETACH, pid, 0, 0);   /* задача біжить далі, ніби нічого не було */
    return 0;
}
