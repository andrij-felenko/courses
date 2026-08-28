#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

/* Виконання цільової програми у дочірньому процесі */
static void run_target_program(char **argv) {
    /* Дозволяємо батьківському процесу трасувати поточний процес */
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
        perror("ptrace PTRACE_TRACEME");
        exit(EXIT_FAILURE);
    }
    
    /* Зупиняємо процес перед заміною образу */
    raise(SIGSTOP);
    
    /* Замінюємо образ процесу на обрану програму */
    execvp(argv[0], argv);
    perror("execvp");
    exit(EXIT_FAILURE);
}

/* Цикл обробки подій трасування у батьківському процесі */
static void run_tracer_loop(pid_t child_pid) {
    int status = 0;
    int is_sys_enter = 1;

    /* Чекаємо початкової зупинки дочірнього процесу після SIGSTOP */
    if (waitpid(child_pid, &status, 0) < 0) {
        perror("waitpid initial");
        return;
    }

    /* Встановлюємо прапорці ptrace */
    if (ptrace(PTRACE_SETOPTIONS, child_pid, 0, PTRACE_O_TRACESYSGOOD | PTRACE_O_EXITKILL) < 0) {
        perror("ptrace PTRACE_SETOPTIONS");
        return;
    }

    printf("[Tracer C] Трасування розпочато для PID: %d\n", child_pid);

    while (1) {
        /* Запускаємо процес до наступної точки системного виклику */
        if (ptrace(PTRACE_SYSCALL, child_pid, 0, 0) < 0) {
            perror("ptrace PTRACE_SYSCALL");
            break;
        }

        /* Чекаємо на зміну стану цільового процесу */
        if (waitpid(child_pid, &status, 0) < 0) {
            perror("waitpid loop");
            break;
        }

        /* Перевірка на нормальне або аварійне завершення */
        if (WIFEXITED(status)) {
            printf("[Tracer C] Процес нормалізовано завершився з кодом: %d\n", WEXITSTATUS(status));
            break;
        }
        if (WIFSIGNALED(status)) {
            printf("[Tracer C] Процес вбито сигналом: %d\n", WTERMSIG(status));
            break;
        }

        /* Ідентифікація точки системного виклику через TRACESYSGOOD (SIGTRAP | 0x80) */
        if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
            struct user_regs_struct regs;
            if (ptrace(PTRACE_GETREGS, child_pid, 0, &regs) < 0) {
                perror("ptrace PTRACE_GETREGS");
                break;
            }

            if (is_sys_enter) {
                /* sys_enter: orig_rax = номер виклику, rdi, rsi, rdx = аргументи 1..3 */
                printf("[sys_enter] Syscall NR: %llu (Arg1: 0x%llx, Arg2: 0x%llx, Arg3: 0x%llx)\n",
                       (unsigned long long)regs.orig_rax,
                       (unsigned long long)regs.rdi,
                       (unsigned long long)regs.rsi,
                       (unsigned long long)regs.rdx);
                is_sys_enter = 0;
            } else {
                /* sys_exit: rax = код повернення ядра */
                printf("[sys_exit ] Syscall NR: %llu -> Return Code: %lld\n",
                       (unsigned long long)regs.orig_rax,
                       (long long)regs.rax);
                is_sys_enter = 1;
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <програма> [аргументи...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    if (child == 0) {
        run_target_program(&argv[1]);
    } else {
        run_tracer_loop(child);
    }

    return EXIT_SUCCESS;
}
