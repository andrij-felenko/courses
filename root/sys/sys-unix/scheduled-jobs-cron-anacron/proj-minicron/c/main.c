#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <errno.h>

#define MAX_JOBS 32
#define MAX_CMD_LEN 256

/* Бітова маска для кожного поля розкладу.
 * 64 біти вистачає для покриття діапазону хвилин (0..59) та решти полів. */
typedef struct {
    unsigned long long minute_mask;   /* 0-59 */
    unsigned int hour_mask;           /* 0-23 */
    unsigned int dom_mask;            /* 1-31 (біти 1..31) */
    unsigned int month_mask;          /* 1-12 (біти 1..12) */
    unsigned int dow_mask;            /* 0-7 (0 і 7 - неділя) */
    int dom_is_wildcard;              /* чи було поле дня місяця задано як '*' */
    int dow_is_wildcard;              /* чи було поле дня тижня задано як '*' */
    char command[MAX_CMD_LEN];
} cron_job_t;

static cron_job_t g_jobs[MAX_JOBS];
static size_t g_num_jobs = 0;

/* Обробник сигналу SIGCHLD для асинхронного очищення зомбі-процесів */
static void sigchld_handler(int sig) {
    (void)sig;
    int saved_errno = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0) {
        /* Очищаємо всіх нащадків, що завершили роботу */
    }
    errno = saved_errno;
}

/* Парсинг одного поля crontab у бітову маску (підтримка '*', чисел, діапазонів 'a-b' та кроків */
static int parse_field(const char *str, int min_val, int max_val,
                       unsigned long long *mask_out, int *is_wildcard) {
    *mask_out = 0;
    *is_wildcard = 0;

    if (strcmp(str, "*") == 0) {
        *is_wildcard = 1;
        for (int i = min_val; i <= max_val; ++i) {
            *mask_out |= (1ULL << i);
        }
        return 0;
    }

    if (strncmp(str, "*/", 2) == 0) {
        int step = atoi(str + 2);
        if (step <= 0) return -1;
        for (int i = min_val; i <= max_val; i += step) {
            *mask_out |= (1ULL << i);
        }
        return 0;
    }

    char *dash = strchr(str, '-');
    if (dash) {
        int start = atoi(str);
        int end = atoi(dash + 1);
        if (start < min_val || end > max_val || start > end) return -1;
        for (int i = start; i <= end; ++i) {
            *mask_out |= (1ULL << i);
        }
        return 0;
    }

    /* Простий список через кому або одне число */
    char buf[64];
    strncpy(buf, str, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
    char *token = strtok(buf, ",");
    while (token) {
        int val = atoi(token);
        if (val < min_val || val > max_val) return -1;
        *mask_out |= (1ULL << val);
        token = strtok(NULL, ",");
    }
    return 0;
}

/* Додавання завдання до таблиці */
static int add_job(const char *min_s, const char *hour_s, const char *dom_s,
                   const char *mon_s, const char *dow_s, const char *cmd) {
    if (g_num_jobs >= MAX_JOBS) return -1;
    cron_job_t *j = &g_jobs[g_num_jobs];

    unsigned long long m_mask, h_mask, dom_m, mon_m, dow_m;
    int dom_w, dow_w, dummy;

    if (parse_field(min_s, 0, 59, &m_mask, &dummy) != 0) return -1;
    if (parse_field(hour_s, 0, 23, &h_mask, &dummy) != 0) return -1;
    if (parse_field(dom_s, 1, 31, &dom_m, &dom_w) != 0) return -1;
    if (parse_field(mon_s, 1, 12, &mon_m, &dummy) != 0) return -1;
    if (parse_field(dow_s, 0, 7, &dow_m, &dow_w) != 0) return -1;

    /* Уніфікація неділі: 0 і 7 відповідають неділі */
    if (dow_m & (1ULL << 7)) {
        dow_m |= (1ULL << 0);
    }
    if (dow_m & (1ULL << 0)) {
        dow_m |= (1ULL << 7);
    }

    j->minute_mask = m_mask;
    j->hour_mask = (unsigned int)h_mask;
    j->dom_mask = (unsigned int)dom_m;
    j->month_mask = (unsigned int)mon_m;
    j->dow_mask = (unsigned int)dow_m;
    j->dom_is_wildcard = dom_w;
    j->dow_is_wildcard = dow_w;
    strncpy(j->command, cmd, sizeof(j->command) - 1);
    j->command[sizeof(j->command) - 1] = '\0';

    g_num_jobs++;
    return 0;
}

/* Перевірка збігу завдання з поточним астрономічним часом */
static int job_matches(const cron_job_t *j, const struct tm *t) {
    /* 1. Хвилини, години, місяці перевіряються через кон'юнкцію */
    if (!(j->minute_mask & (1ULL << t->tm_min))) return 0;
    if (!(j->hour_mask & (1ULL << t->tm_hour))) return 0;
    if (!(j->month_mask & (1ULL << (t->tm_mon + 1)))) return 0;

    int dom_match = (j->dom_mask & (1ULL << t->tm_mday)) ? 1 : 0;
    int dow_match = (j->dow_mask & (1ULL << t->tm_wday)) ? 1 : 0;

    /* 2. Особливе правило POSIX: якщо обидва поля обмежені, використовується OR */
    if (!j->dom_is_wildcard && !j->dow_is_wildcard) {
        return dom_match || dow_match;
    }
    /* Якщо хоча б одне поле є '*', використовується звичайна кон'юнкція */
    return dom_match && dow_match;
}

/* Запуск завдання у дочірньому процесі */
static void spawn_job(const char *cmd) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return;
    }
    if (pid == 0) {
        /* Дочірній процес: ізоляція стандартних дескрипторів */
        int devnull = open("/dev/null", O_RDWR);
        if (devnull >= 0) {
            dup2(devnull, STDIN_FILENO);
            close(devnull);
        }
        /* Виконання команди через стандартний командний інтерпретатор */
        execl("/bin/sh", "sh", "-c", cmd, (char *)NULL);
        _exit(127);
    }
}

int main(void) {
    /* Встановлюємо обробник SIGCHLD */
    struct sigaction sa;
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    sigaction(SIGCHLD, &sa, NULL);

    /* Додаємо тестові розклади:
     * 1. Кожну хвилину: друк поточної мітки часу
     * 2. Кожні 5 хвилин: системний звіт
     * 3. Щоп'ятниці та 13-го числа: перевірка правила DOM || DOW */
    add_job("*", "*", "*", "*", "*", "echo minicron tick $(date) >> /tmp/minicron.log");
    add_job("*/5", "*", "*", "*", "*", "uptime >> /tmp/minicron-uptime.log");
    add_job("0", "12", "13", "*", "5", "echo Friday the 13th alert >> /tmp/minicron.log");

    printf("minicron запущено. Зареєстровано завдань: %zu\n", g_num_jobs);

    while (1) {
        time_t now = time(NULL);
        struct tm tm_now;
        localtime_r(&now, &tm_now);

        /* Засинаємо до початку наступної хвилини */
        int seconds_to_next_minute = 60 - tm_now.tm_sec;
        if (seconds_to_next_minute > 0) {
            sleep((unsigned int)seconds_to_next_minute);
        }

        /* Оновлюємо час після пробудження */
        now = time(NULL);
        localtime_r(&now, &tm_now);

        /* Перевіряємо всі зареєстровані завдання */
        for (size_t i = 0; i < g_num_jobs; ++i) {
            if (job_matches(&g_jobs[i], &tm_now)) {
                spawn_job(g_jobs[i].command);
            }
        }
    }

    return 0;
}
