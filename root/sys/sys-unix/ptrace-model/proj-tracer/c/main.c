#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/types.h>
#include <errno.h>

/* Таблиця імен системних викликів x86_64 для форматованого виводу */
static const char *get_syscall_name(long syscall_nr) {
    switch (syscall_nr) {
        case 0:   return "read";
        case 1:   return "write";
        case 2:   return "open";
        case 3:   return "close";
        case 9:   return "mmap";
        case 10:  return "mprotect";
        case 11:  return "munmap";
        case 12:  return "brk";
        case 59:  return "execve";
        case 231: return "exit_group";
        default:  return "unknown_syscall";
    }
}

/* Функція для безпечного читання рядка з пам'яті tracee по 8 байт (слово) */
static void read_remote_string(pid_t child, unsigned long addr, char *buffer, size_t max_len) {
    size_t bytes_read = 0;
    while (bytes_read < max_len - 1) {
        errno = 0;
        long val = ptrace(PTRACE_PEEKDATA, child, (void*)(addr + bytes_read), NULL);
        if (val == -1 && errno != 0) {
            break;
        }
        char *p = (char *)&val;
        for (int i = 0; i < sizeof(long); ++i) {
            if (p[i] == '\0' || bytes_read >= max_len - 1) {
                buffer[bytes_read] = '\0';
                return;
            }
            buffer[bytes_read++] = p[i];
        }
    }
    buffer[bytes_read] = '\0';
}

static void run_target(char **argv) {
    /* Дозволяємо батьківському процесу трасувати поточний процес */
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
        perror("ptrace(TRACEME) failed");
        exit(EXIT_FAILURE);
    }
    
    /* Призупиняємо виконання для налаштування опцій трасувальником */
    raise(SIGSTOP);
    
    /* Замінюємо простір пам'яті кодом цільової програми */
    execvp(argv[0], argv);
    perror("execvp failed");
    exit(EXIT_FAILURE);
}

static void run_tracer(pid_t child_pid) {
    int status;

    /* Чекаємо першої зупинки SIGSTOP від дочірнього процесу */
    if (waitpid(child_pid, &status, 0) < 0) {
        perror("waitpid initial failed");
        return;
    }

    if (!WIFSTOPPED(status)) {
        fprintf(stderr, "Tracee didn't stop properly\n");
        return;
    }

    /* Встановлюємо прапор PTRACE_O_TRACESYSGOOD для маркування syscalls */
    if (ptrace(PTRACE_SETOPTIONS, child_pid, 0, (void*)PTRACE_O_TRACESYSGOOD) < 0) {
        perror("ptrace(PTRACE_SETOPTIONS) failed");
        return;
    }

    int in_syscall = 0;
    long syscall_nr = -1;

    while (1) {
        /* Відновлюємо виконання до наступного системного виклику */
        if (ptrace(PTRACE_SYSCALL, child_pid, 0, 0) < 0) {
            perror("ptrace(SYSCALL) failed");
            break;
        }

        if (waitpid(child_pid, &status, 0) < 0) {
            perror("waitpid loop failed");
            break;
        }

        /* Перевіряємо, чи цільовий процес завершився нормально */
        if (WIFEXITED(status)) {
            printf("\n[Tracer] Tracee exited with code %d\n", WEXITSTATUS(status));
            break;
        }

        /* Перевіряємо, чи цільовий процес було вбито сигналом */
        if (WIFSIGNALED(status)) {
            printf("\n[Tracer] Tracee killed by signal %d\n", WTERMSIG(status));
            break;
        }

        /* Обробка стану ptrace-stop */
        if (WIFSTOPPED(status)) {
            int sig = WSTOPSIG(status);

            /* Перевіряємо, чи це зупинка на системному виклику (SIGTRAP | 0x80 = 0x85) */
            if (sig == (SIGTRAP | 0x80)) {
                struct user_regs_struct regs;
                if (ptrace(PTRACE_GETREGS, child_pid, 0, &regs) < 0) {
                    perror("ptrace(GETREGS) failed");
                    break;
                }

                if (!in_syscall) {
                    /* Точка входу в системний виклик (Syscall Enter Stop) */
                    in_syscall = 1;
                    syscall_nr = (long)regs.orig_rax;
                    
                    printf("[SYS_ENTER] %-12s (arg1=0x%-8llx, arg2=0x%-8llx, arg3=0x%-8llx)",
                           get_syscall_name(syscall_nr),
                           regs.rdi, regs.rsi, regs.rdx);

                    /* Якщо це системний виклик write(), читаємо переданий рядок */
                    if (syscall_nr == 1 && regs.rsi != 0) {
                        char str_buf[64];
                        read_remote_string(child_pid, regs.rsi, str_buf, sizeof(str_buf));
                        printf(" [buf=\"%s\"]", str_buf);
                    }
                    fflush(stdout);
                } else {
                    /* Точка виходу з системного виклику (Syscall Exit Stop) */
                    in_syscall = 0;
                    long res = (long)regs.rax;
                    printf(" = %ld\n", res);
                }
            } else {
                /* Якщо процес зупинився через звичайний апаратний сигнал */
                printf("\n[Tracer] Tracee received signal: %d\n", sig);
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <program> [args...]\n", argv[0]);
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
