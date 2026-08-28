#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>

#define MAX_JOBS 32
#define MAX_ARGS 16

typedef enum {
    JOB_RUNNING,
    JOB_STOPPED,
    JOB_COMPLETED
} JobState;

typedef struct {
    int id;
    pid_t pgid;
    char command[128];
    JobState state;
    struct termios tmodes;
} Job;

static Job job_table[MAX_JOBS];
static int job_count = 0;
static pid_t shell_pgid;
static int shell_terminal = STDIN_FILENO;
static struct termios shell_tmodes;

static void init_shell(void) {
    /* Перевіряємо, чи працюємо ми в інтерактивному терміналі */
    if (!isatty(shell_terminal)) {
        fprintf(stderr, "Помилка: Оболонка повинна запускатися в TTY\n");
        exit(EXIT_FAILURE);
    }

    /* Чекаємо, поки оболонка не опиниться на передньому плані */
    while (tcgetpgrp(shell_terminal) != (shell_pgid = getpgrp())) {
        kill(-shell_pgid, SIGTTIN);
    }

    /* Ігноруємо термінальні сигнали у самому процесі оболонки */
    signal(SIGINT, SIG_IGN);
    signal(SIGQUIT, SIG_IGN);
    signal(SIGTSTP, SIG_IGN);
    signal(SIGTTIN, SIG_IGN);
    signal(SIGTTOU, SIG_IGN);
    signal(SIGCHLD, SIG_DFL);

    /* Створюємо власну групу процесів для оболонки */
    shell_pgid = getpid();
    if (setpgid(shell_pgid, shell_pgid) < 0) {
        perror("setpgid для оболонки");
        exit(EXIT_FAILURE);
    }

    /* Забираємо фокус термінала собі */
    tcsetpgrp(shell_terminal, shell_pgid);
    tcgetattr(shell_terminal, &shell_tmodes);
}

static Job* add_job(pid_t pgid, const char* cmd, JobState state) {
    if (job_count >= MAX_JOBS) return NULL;
    Job* j = &job_table[job_count++];
    j->id = job_count;
    j->pgid = pgid;
    snprintf(j->command, sizeof(j->command), "%s", cmd);
    j->state = state;
    tcgetattr(shell_terminal, &j->tmodes);
    return j;
}

static void wait_for_job(Job* j) {
    int status;
    pid_t pid;

    /* Чекаємо зміни стану будь-якого процесу з даної групи */
    while ((pid = waitpid(-j->pgid, &status, WUNTRACED)) > 0) {
        if (WIFSTOPPED(status)) {
            j->state = JOB_STOPPED;
            tcgetattr(shell_terminal, &j->tmodes);
            printf("\n[%d]+ Зупинено (SIGTSTP)   %s\n", j->id, j->command);
            break;
        } else if (WIFEXITED(status) || WIFSIGNALED(status)) {
            j->state = JOB_COMPLETED;
            break;
        }
    }

    /* Повертаємо термінал оболонці */
    tcsetpgrp(shell_terminal, shell_pgid);
    tcsetattr(shell_terminal, TCSADRAIN, &shell_tmodes);
}

static void put_job_in_foreground(Job* j, int cont) {
    /* Відновлюємо налаштування термінала завдання */
    tcsetattr(shell_terminal, TCSADRAIN, &j->tmodes);
    
    /* Передаємо термінал групі завдання */
    tcsetpgrp(shell_terminal, j->pgid);

    if (cont) {
        if (kill(-j->pgid, SIGCONT) < 0) {
            perror("kill (SIGCONT)");
        }
    }

    j->state = JOB_RUNNING;
    wait_for_job(j);
}

static void put_job_in_background(Job* j, int cont) {
    if (cont) {
        if (kill(-j->pgid, SIGCONT) < 0) {
            perror("kill (SIGCONT)");
        }
    }
    j->state = JOB_RUNNING;
    printf("[%d] %d\n", j->id, (int)j->pgid);
}

static void execute_cmd(char** args, int in_bg, const char* full_cmd) {
    pid_t pid = fork();

    if (pid == 0) {
        /* Код нащадка */
        pid_t child_pid = getpid();
        setpgid(child_pid, child_pid);

        if (!in_bg) {
            tcsetpgrp(shell_terminal, child_pid);
        }

        /* Відновлюємо дефолтні обробники сигналів у нащадку */
        signal(SIGINT, SIG_DFL);
        signal(SIGQUIT, SIG_DFL);
        signal(SIGTSTP, SIG_DFL);
        signal(SIGTTIN, SIG_DFL);
        signal(SIGTTOU, SIG_DFL);
        signal(SIGCHLD, SIG_DFL);

        execvp(args[0], args);
        perror("execvp");
        _exit(EXIT_FAILURE);
    } else if (pid > 0) {
        /* Код батька (оболонки) */
        setpgid(pid, pid); /* Взаємне усунення race condition */

        Job* j = add_job(pid, full_cmd, in_bg ? JOB_RUNNING : JOB_STOPPED);
        if (!in_bg) {
            put_job_in_foreground(j, 0);
        } else {
            put_job_in_background(j, 0);
        }
    } else {
        perror("fork");
    }
}

int main(void) {
    char line[256];
    init_shell();

    while (1) {
        printf("job-shell> ");
        fflush(stdout);

        if (!fgets(line, sizeof(line), stdin)) break;

        line[strcspn(line, "\n")] = 0;
        if (strlen(line) == 0) continue;

        char* args[MAX_ARGS];
        int arg_idx = 0;
        char* token = strtok(line, " ");
        while (token && arg_idx < MAX_ARGS - 1) {
            args[arg_idx++] = token;
            token = strtok(NULL, " ");
        }
        args[arg_idx] = NULL;

        int in_bg = 0;
        if (arg_idx > 0 && strcmp(args[arg_idx - 1], "&") == 0) {
            in_bg = 1;
            args[--arg_idx] = NULL;
        }

        if (args[0] == NULL) continue;

        if (strcmp(args[0], "jobs") == 0) {
            for (int i = 0; i < job_count; i++) {
                if (job_table[i].state != JOB_COMPLETED) {
                    printf("[%d] %s   %s\n", job_table[i].id,
                           job_table[i].state == JOB_STOPPED ? "Зупинено" : "Працює",
                           job_table[i].command);
                }
            }
        } else if (strcmp(args[0], "fg") == 0) {
            if (job_count > 0) {
                Job* j = &job_table[job_count - 1];
                printf("%s\n", j->command);
                put_job_in_foreground(j, 1);
            }
        } else if (strcmp(args[0], "bg") == 0) {
            if (job_count > 0) {
                Job* j = &job_table[job_count - 1];
                put_job_in_background(j, 1);
            }
        } else if (strcmp(args[0], "exit") == 0) {
            break;
        } else {
            execute_cmd(args, in_bg, line);
        }
    }

    return 0;
}
