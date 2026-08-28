#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>

static void run_target(char *const argv[]) {
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
        perror("ptrace TRACEME failed");
        exit(EXIT_FAILURE);
    }
    execvp(argv[0], argv);
    perror("execvp failed");
    exit(EXIT_FAILURE);
}

static void run_tracer(pid_t child_pid) {
    int status;
    int is_syscall_entry = 1;

    waitpid(child_pid, &status, 0);

    /* Встановлюємо прапорець PTRACE_O_TRACESYSGOOD */
    if (ptrace(PTRACE_SETOPTIONS, child_pid, 0, PTRACE_O_TRACESYSGOOD) < 0) {
        perror("ptrace SETOPTIONS failed");
        exit(EXIT_FAILURE);
    }

    while (1) {
        if (ptrace(PTRACE_SYSCALL, child_pid, 0, 0) < 0) {
            perror("ptrace SYSCALL failed");
            break;
        }

        waitpid(child_pid, &status, 0);

        if (WIFEXITED(status) || WIFSIGNALED(status)) {
            printf("[Процес %d завершився]\n", child_pid);
            break;
        }

        if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
            struct user_regs_struct regs;
            if (ptrace(PTRACE_GETREGS, child_pid, 0, &regs) < 0) {
                perror("ptrace GETREGS failed");
                break;
            }

            if (is_syscall_entry) {
                printf("[SYSCALL Entry] № %llu (arg1: 0x%llx, arg2: 0x%llx, arg3: 0x%llx)\n",
                       regs.orig_rax, regs.rdi, regs.rsi, regs.rdx);
                is_syscall_entry = 0;
            } else {
                printf("[SYSCALL Exit ] № %llu -> Result: %lld\n",
                       regs.orig_rax, (long long)regs.rax);
                is_syscall_entry = 1;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <програма_для_запуску> [аргументи...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        run_target(&argv[1]);
    } else {
        run_tracer(pid);
    }

    return EXIT_SUCCESS;
}
