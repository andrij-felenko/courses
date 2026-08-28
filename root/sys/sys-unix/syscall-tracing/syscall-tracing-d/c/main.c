/* Приклад модифікації аргументу системного виклику на точці sys_enter (C) */
#include <sys/ptrace.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>

void modify_syscall_arg(pid_t tracee_pid) {
    struct user_regs_struct regs;
    if (ptrace(PTRACE_GETREGS, tracee_pid, NULL, &regs) == 0) {
        /* Якщо виконується системний виклик write (NR 1 на x86_64) */
        if (regs.orig_rax == 1) {
            /* Змінюємо довжину буфера (третій аргумент rdx) на 0 */
            regs.rdx = 0;
            ptrace(PTRACE_SETREGS, tracee_pid, NULL, &regs);
        }
    }
}
