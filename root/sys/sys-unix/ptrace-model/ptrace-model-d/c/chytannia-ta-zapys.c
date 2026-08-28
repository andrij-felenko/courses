#include <stdio.h>
#include <sys/ptrace.h>
#include <sys/user.h>

void inspect_registers(pid_t pid) {
    struct user_regs_struct regs;
    if (ptrace(PTRACE_GETREGS, pid, NULL, &regs) == 0) {
        printf("RIP (Instruction Pointer): 0x%llx\n", regs.rip);
        printf("RSP (Stack Pointer):       0x%llx\n", regs.rsp);
        printf("RAX (Syscall/Return):      0x%llx\n", regs.rax);
    }
}
