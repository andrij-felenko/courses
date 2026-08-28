#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <time.h>
#include <errno.h>

#define MAX_CHILDREN 8
#define MAX_RESTARTS_BUDGET 16

typedef enum {
    STRATEGY_ONE_FOR_ONE,
    STRATEGY_REST_FOR_ONE
} Strategy;

typedef enum {
    RESTART_PERMANENT,
    RESTART_TRANSIENT,
    RESTART_TEMPORARY
} RestartType;

typedef struct {
    const char *name;
    void (*worker_fn)(void *arg);
    void *arg;
    RestartType restart_type;
    pid_t pid;
    bool is_alive;
} ChildSpec;

typedef struct {
    Strategy strategy;
    int max_restarts;
    int max_seconds;
    time_t crash_timestamps[MAX_RESTARTS_BUDGET];
    int crash_count;
    ChildSpec children[MAX_CHILDREN];
    int child_count;
} Supervisor;

static void record_crash_and_check_budget(Supervisor *sup) {
    time_t now = time(NULL);
    
    // Очищаємо старі таймстеми поза вікном max_seconds
    int valid = 0;
    for (int i = 0; i < sup->crash_count; i++) {
        if (now - sup->crash_timestamps[i] <= sup->max_seconds) {
            sup->crash_timestamps[valid++] = sup->crash_timestamps[i];
        }
    }
    sup->crash_count = valid;

    if (sup->crash_count < MAX_RESTARTS_BUDGET) {
        sup->crash_timestamps[sup->crash_count++] = now;
    }

    if (sup->crash_count > sup->max_restarts) {
        fprintf(stderr, "[SUPERVISOR] Перевищено ліміт збоїв (%d за %d с). Ескалація!\n",
                sup->max_restarts, sup->max_seconds);
        // Зупиняємо всіх живих дітей
        for (int i = 0; i < sup->child_count; i++) {
            if (sup->children[i].is_alive) {
                kill(sup->children[i].pid, SIGTERM);
                waitpid(sup->children[i].pid, NULL, 0);
                sup->children[i].is_alive = false;
            }
        }
        exit(EXIT_FAILURE);
    }
}

static bool start_child(Supervisor *sup, int index) {
    ChildSpec *spec = &sup->children[index];
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return false;
    }
    if (pid == 0) {
        // Дочірній процес: скидаємо обробники сигналів і запускаємо роботу
        signal(SIGINT, SIG_DFL);
        signal(SIGTERM, SIG_DFL);
        spec->worker_fn(spec->arg);
        exit(EXIT_SUCCESS);
    }
    spec->pid = pid;
    spec->is_alive = true;
    printf("[SUPERVISOR] Запущено дочірній процес '%s' (PID=%d)\n", spec->name, pid);
    return true;
}

static void stop_child(ChildSpec *spec) {
    if (!spec->is_alive) return;
    printf("[SUPERVISOR] Зупинка процесу '%s' (PID=%d)\n", spec->name, spec->pid);
    kill(spec->pid, SIGTERM);
    
    // Очікуємо завершення до 2 секунд, потім примусовий kill
    for (int t = 0; t < 20; t++) {
        int status;
        pid_t res = waitpid(spec->pid, &status, WNOHANG);
        if (res == spec->pid) {
            spec->is_alive = false;
            return;
        }
        usleep(100000); // 100 мс
    }
    kill(spec->pid, SIGKILL);
    waitpid(spec->pid, NULL, 0);
    spec->is_alive = false;
}

void supervisor_run(Supervisor *sup) {
    // 1. Початковий запуск усіх нащадків у порядку оголошення
    for (int i = 0; i < sup->child_count; i++) {
        if (!start_child(sup, i)) {
            fprintf(stderr, "[SUPERVISOR] Не вдалося запустити '%s'\n", sup->children[i].name);
            return;
        }
    }

    // 2. Головний цикл спостереження
    while (true) {
        int status;
        pid_t died_pid = waitpid(-1, &status, 0);
        if (died_pid < 0) {
            if (errno == EINTR) continue;
            break; // Немає живих нащадків
        }

        int child_idx = -1;
        for (int i = 0; i < sup->child_count; i++) {
            if (sup->children[i].pid == died_pid) {
                child_idx = i;
                break;
            }
        }
        if (child_idx < 0) continue;

        ChildSpec *spec = &sup->children[child_idx];
        spec->is_alive = false;

        bool is_normal = WIFEXITED(status) && (WEXITSTATUS(status) == 0);
        printf("[SUPERVISOR] Процес '%s' (PID=%d) завершився. Код=%d, Нормально=%d\n",
               spec->name, died_pid, WEXITSTATUS(status), is_normal);

        bool need_restart = false;
        if (spec->restart_type == RESTART_PERMANENT) {
            need_restart = true;
        } else if (spec->restart_type == RESTART_TRANSIENT && !is_normal) {
            need_restart = true;
        }

        if (!need_restart) {
            printf("[SUPERVISOR] Процес '%s' не потребує перезапуску.\n", spec->name);
            continue;
        }

        record_crash_and_check_budget(sup);

        if (sup->strategy == STRATEGY_ONE_FOR_ONE) {
            start_child(sup, child_idx);
        } else if (sup->strategy == STRATEGY_REST_FOR_ONE) {
            // Зупиняємо всіх наступних дітей у зворотному порядку
            for (int i = sup->child_count - 1; i > child_idx; i--) {
                stop_child(&sup->children[i]);
            }
            // Перезапускаємо збійного нащадка
            start_child(sup, child_idx);
            // Запускаємо наступних нащадків наново
            for (int i = child_idx + 1; i < sup->child_count; i++) {
                start_child(sup, i);
            }
        }
    }
}
