#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <errno.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

/* =========================================================================
 * ШАР 1: ПОЛІТИКА (Policy) — правила життя процесу
 * ========================================================================= */
typedef struct {
    int max_retries;           /* скільки спроб дозволено */
    int base_delay_ms;         /* початкова затримка перед рестартом (мс) */
    int max_delay_ms;          /* максимальна затримка експоненційного бекофу */
    bool restart_on_clean_exit;/* чи перезапускати при коді виходу 0 */
} SupervisorPolicy;

typedef struct {
    int attempts_made;
    int current_delay_ms;
} SupervisorState;

static void policy_init(SupervisorState *state, const SupervisorPolicy *policy) {
    state->attempts_made = 0;
    state->current_delay_ms = policy->base_delay_ms;
}

static bool policy_should_restart(SupervisorState *state, const SupervisorPolicy *policy, int status) {
    /* Якщо процес вийшов сам із кодом 0 і політика не вимагає рестарту — зупиняємось */
    if (WIFEXITED(status) && WEXITSTATUS(status) == 0 && !policy->restart_on_clean_exit) {
        printf("[ПОЛІТИКА] Процес успішно завершив роботу (exit code 0). Рестарт не потрібен.\n");
        return false;
    }

    state->attempts_made++;
    if (state->attempts_made > policy->max_retries) {
        printf("[ПОЛІТИКА] Вичерпано ліміт спроб (%d). Зупинка.\n", policy->max_retries);
        return false;
    }

    printf("[ПОЛІТИКА] Спроба %d/%d. Очікування %d мс перед рестартом...\n",
           state->attempts_made, policy->max_retries, state->current_delay_ms);

    struct timespec ts = {
        .tv_sec = state->current_delay_ms / 1000,
        .tv_nsec = (state->current_delay_ms % 1000) * 1000000L
    };
    nanosleep(&ts, NULL);

    /* Експоненційний бекоф: подвоюємо затримку до досягнення max_delay_ms */
    state->current_delay_ms *= 2;
    if (state->current_delay_ms > policy->max_delay_ms) {
        state->current_delay_ms = policy->max_delay_ms;
    }

    return true;
}

/* =========================================================================
 * ШАР 2: МЕХАНІЗМ (Mechanism) — запуск, комутація каналів, збір логів
 * ========================================================================= */
typedef struct {
    pid_t pid;
    int log_pipe_fd;
} ChildProcess;

/* Чистий механізм: створення нащадка з перехопленням stdout/stderr у канал */
static bool spawn_child(char *const argv[], ChildProcess *out_child) {
    int pipefd[2];
    /* O_CLOEXEC гарантує, що дескриптори каналу не витечуть у сторонні виклики exec */
    if (pipe2(pipefd, O_CLOEXEC) == -1) {
        perror("[МЕХАНІЗМ] pipe2 failed");
        return false;
    }

    pid_t pid = fork();
    if (pid == -1) {
        perror("[МЕХАНІЗМ] fork failed");
        close(pipefd[0]);
        close(pipefd[1]);
        return false;
    }

    if (pid == 0) {
        /* ДОЧІРНІЙ ПРОЦЕС:
         * Створюємо окрему групу процесів, щоб сигнали не вбивали наглядача */
        setpgid(0, 0);

        /* Перенаправляємо stdout і stderr у кінець запису каналу */
        if (dup2(pipefd[1], STDOUT_FILENO) == -1 || dup2(pipefd[1], STDERR_FILENO) == -1) {
            perror("[ДОЧІРНІЙ] dup2 failed");
            _exit(127);
        }

        /* Зачиняємо оригінальні дескриптори після дублювання */
        close(pipefd[0]);
        close(pipefd[1]);

        execvp(argv[0], argv);
        /* Якщо execvp повернув керування — сталася помилка */
        perror("[ДОЧІРНІЙ] execvp failed");
        _exit(127);
    }

    /* БАТЬКІВСЬКИЙ ПРОЦЕС:
     * Закриваємо кінець запису, залишаємо кінець читання */
    close(pipefd[1]);
    out_child->pid = pid;
    out_child->log_pipe_fd = pipefd[0];
    return true;
}

/* Механізм зливу логів з каналу та очікування виходу */
static int collect_and_wait(ChildProcess *child) {
    char buf[256];
    ssize_t bytes_read;

    /* Вичитуємо всі логи, доки дочірній процес не закриє свій кінець запису */
    while ((bytes_read = read(child->log_pipe_fd, buf, sizeof(buf) - 1)) > 0) {
        buf[bytes_read] = '\0';
        printf("[ЛОГ НАЩАДКА %d] %s", child->pid, buf);
        if (buf[bytes_read - 1] != '\n') {
            printf("\n");
        }
    }

    close(child->log_pipe_fd);

    int status = 0;
    while (waitpid(child->pid, &status, 0) == -1) {
        if (errno == EINTR) continue; /* перервано сигналом — повторюємо */
        perror("[МЕХАНІЗМ] waitpid failed");
        return -1;
    }

    return status;
}

/* =========================================================================
 * ТОЧКА ВХОДУ: зв'язування механізму й політики
 * ========================================================================= */
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    /* Налаштовуємо політику */
    SupervisorPolicy policy = {
        .max_retries = 3,
        .base_delay_ms = 200,
        .max_delay_ms = 2000,
        .restart_on_clean_exit = false
    };

    SupervisorState state;
    policy_init(&state, &policy);

    char *const *target_args = &argv[1];

    while (true) {
        printf("\n[НАГЛЯДАЧ] Запуск програми: %s\n", target_args[0]);
        ChildProcess child;
        if (!spawn_child(target_args, &child)) {
            fprintf(stderr, "[НАГЛЯДАЧ] Не вдалося породити процес.\n");
            break;
        }

        int status = collect_and_wait(&child);
        if (status == -1) {
            break;
        }

        if (WIFEXITED(status)) {
            printf("[МЕХАНІЗМ] Процес завершився з кодом: %d\n", WEXITSTATUS(status));
        } else if (WIFSIGNALED(status)) {
            printf("[МЕХАНІЗМ] Процес загинув від сигналу: %d (%s)\n",
                   WTERMSIG(status), strsignal(WTERMSIG(status)));
        }

        if (!policy_should_restart(&state, &policy, status)) {
            break;
        }
    }

    printf("[НАГЛЯДАЧ] Роботу наглядача завершено.\n");
    return 0;
}
