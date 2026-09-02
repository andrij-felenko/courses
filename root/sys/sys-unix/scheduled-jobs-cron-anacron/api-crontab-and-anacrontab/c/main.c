/* minicron — навчальний планувальник: читає таблицю crontab, прокидається на
   нульовій секунді кожної хвилини й запускає завдання, чий розклад збігся.
   Перечитує таблицю за подією inotify (де його немає — за st_mtime).
   Використання: minicron [-s] <файл таблиці>
   -s — системна таблиця (шосте поле — ім'я користувача). */
#define _GNU_SOURCE

#include <ctype.h>
#include <errno.h>
#include <libgen.h>
#include <pwd.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#include "joblock.h"
#include "runjob.h"
#include "schedule.h"
#include "timerloop.h"

#define MAX_ENTRIES     64
#define MAX_ENV         32
#define CATCHUP_SECONDS 3600   /* скільки пропущеного наздоганяємо після стрибка */
#define SLACK_NS        200000000UL /* 200 мс вікна коалесценції пробуджень */
#define LOCK_DIR        "/tmp"      /* у справжньому демоні — /var/lock/cron */

typedef struct {
    cron_schedule_t schedule;
    char *user;
    char *command;
    char *stdin_data;
    char *tz;      /* CRON_TZ рядка, якщо був */
    char *mailto;
    char *shell;
    char **envp;   /* знімок середовища на момент рядка */
    char *lock_path;
} entry_t;

typedef struct {
    entry_t items[MAX_ENTRIES];
    size_t count;
} crontab_t;

typedef struct {
    char *names[MAX_ENV];
    char *values[MAX_ENV];
    size_t count;
} env_map_t;

typedef struct {
    crontab_t tab;
    const char *path;
    bool system_table;
    cron_watch_t *watch;
} app_t;

static timer_loop_t *g_loop = NULL;
static time_t g_last_minute = 0;

static void *xmalloc(size_t size)
{
    void *p = malloc(size);
    if (p == NULL) {
        fprintf(stderr, "minicron: бракує пам'яті\n");
        exit(1);
    }
    return p;
}

static char *xstrdup(const char *s)
{
    size_t len = strlen(s) + 1;
    char *copy = xmalloc(len);
    memcpy(copy, s, len);
    return copy;
}

static void env_set(env_map_t *env, const char *name, const char *value)
{
    for (size_t i = 0; i < env->count; i++) {
        if (strcmp(env->names[i], name) == 0) {
            free(env->values[i]);
            env->values[i] = xstrdup(value);
            return;
        }
    }
    if (env->count == MAX_ENV) {
        fprintf(stderr, "minicron: забагато змінних середовища, «%s» пропущено\n", name);
        return;
    }
    env->names[env->count] = xstrdup(name);
    env->values[env->count] = xstrdup(value);
    env->count++;
}

static const char *env_get(const env_map_t *env, const char *name)
{
    for (size_t i = 0; i < env->count; i++) {
        if (strcmp(env->names[i], name) == 0) {
            return env->values[i];
        }
    }
    return NULL;
}

static void env_clear(env_map_t *env)
{
    for (size_t i = 0; i < env->count; i++) {
        free(env->names[i]);
        free(env->values[i]);
    }
    env->count = 0;
}

/* Знімок середовища для завдання: NULL-завершений масив "NAME=value".
   extra — одна необов'язкова пара понад таблицю (нею їде TZ із CRON_TZ). */
static char **env_snapshot(const env_map_t *env, const char *extra_name,
                           const char *extra_value)
{
    const size_t extra = (extra_name != NULL) ? 1 : 0;
    char **envp = xmalloc((env->count + extra + 1) * sizeof(char *));
    size_t out = 0;
    for (size_t i = 0; i < env->count; i++) {
        size_t len = strlen(env->names[i]) + strlen(env->values[i]) + 2;
        char *item = xmalloc(len);
        snprintf(item, len, "%s=%s", env->names[i], env->values[i]);
        envp[out++] = item;
    }
    if (extra != 0) {
        size_t len = strlen(extra_name) + strlen(extra_value) + 2;
        char *item = xmalloc(len);
        snprintf(item, len, "%s=%s", extra_name, extra_value);
        envp[out++] = item;
    }
    envp[out] = NULL;
    return envp;
}

/* Рядок виду NAME=value / NAME="value" / NAME = 'value'. Значення НЕ підлягає
   розгортанню змінних оболонки: «$PATH» лишається текстом. */
static bool parse_env_line(const char *line, char *name, size_t name_size,
                           char *value, size_t value_size)
{
    const char *p = line;
    while (*p == ' ' || *p == '\t') {
        p++;
    }
    if (!isalpha((unsigned char)*p) && *p != '_') {
        return false;
    }
    size_t n = 0;
    while (isalnum((unsigned char)*p) || *p == '_') {
        if (n + 1 >= name_size) {
            return false;
        }
        name[n++] = *p++;
    }
    name[n] = '\0';

    while (*p == ' ' || *p == '\t') {
        p++;
    }
    if (*p != '=') {
        return false;
    }
    p++;
    while (*p == ' ' || *p == '\t') {
        p++;
    }

    size_t len = strlen(p);
    while (len > 0 && (p[len - 1] == ' ' || p[len - 1] == '\t' || p[len - 1] == '\r')) {
        len--;
    }
    if (len >= 2 && ((p[0] == '"' && p[len - 1] == '"') ||
                     (p[0] == '\'' && p[len - 1] == '\''))) {
        p++;
        len -= 2;
    }
    if (len >= value_size) {
        return false;
    }
    memcpy(value, p, len);
    value[len] = '\0';
    return true;
}

/* Перший незахищений '%' відрізає stdin, наступні стають переводами рядка,
   «\%» лишається звичайним відсотком. */
static void split_percent(const char *raw, char **command_out, char **stdin_out)
{
    size_t len = strlen(raw);
    char *cmd = xmalloc(len + 1);
    char *data = xmalloc(len + 2);
    size_t ci = 0;
    size_t di = 0;
    bool in_stdin = false;

    for (size_t i = 0; i < len; i++) {
        char c = raw[i];
        if (c == '\\' && raw[i + 1] == '%') {
            if (in_stdin) {
                data[di++] = '%';
            } else {
                cmd[ci++] = '%';
            }
            i++;
            continue;
        }
        if (c == '%') {
            if (!in_stdin) {
                in_stdin = true;
            } else {
                data[di++] = '\n';
            }
            continue;
        }
        if (in_stdin) {
            data[di++] = c;
        } else {
            cmd[ci++] = c;
        }
    }
    while (ci > 0 && (cmd[ci - 1] == ' ' || cmd[ci - 1] == '\t')) {
        ci--;
    }
    cmd[ci] = '\0';
    /* Тіло stdin завжди завершується переводом рядка. */
    if (di > 0 && data[di - 1] != '\n') {
        data[di++] = '\n';
    }
    data[di] = '\0';

    *command_out = cmd;
    if (di > 0) {
        *stdin_out = data;
    } else {
        *stdin_out = NULL;
        free(data);
    }
}

static char *read_file(const char *path, size_t *out_len)
{
    FILE *f = fopen(path, "rb");
    if (f == NULL) {
        fprintf(stderr, "minicron: %s: %s\n", path, strerror(errno));
        return NULL;
    }
    size_t capacity = 8192;
    size_t len = 0;
    char *buf = xmalloc(capacity);
    for (;;) {
        if (len == capacity) {
            capacity *= 2;
            char *grown = realloc(buf, capacity);
            if (grown == NULL) {
                free(buf);
                fclose(f);
                fprintf(stderr, "minicron: бракує пам'яті\n");
                return NULL;
            }
            buf = grown;
        }
        size_t n = fread(buf + len, 1, capacity - len, f);
        len += n;
        if (n == 0) {
            break;
        }
    }
    if (ferror(f)) {
        fprintf(stderr, "minicron: читання %s: %s\n", path, strerror(errno));
        free(buf);
        fclose(f);
        return NULL;
    }
    fclose(f);
    *out_len = len;
    return buf;
}

/* Ім'я файлу замка не залежить від номера рядка: після перечитування таблиці
   те саме завдання мусить упізнати свій власний замок. */
static uint64_t fnv1a(uint64_t hash, const char *s)
{
    while (*s != '\0') {
        hash ^= (unsigned char)*s++;
        hash *= 1099511628211ULL;
    }
    return hash;
}

static void add_entry(crontab_t *tab, const cron_schedule_t *sched, const char *user,
                      const char *rest, const env_map_t *env)
{
    if (tab->count == MAX_ENTRIES) {
        fprintf(stderr, "minicron: більше за %d завдань не тримаємо\n", MAX_ENTRIES);
        return;
    }
    entry_t *e = &tab->items[tab->count];
    memset(e, 0, sizeof(*e));
    e->schedule = *sched;
    e->user = xstrdup(user);
    split_percent(rest, &e->command, &e->stdin_data);

    const char *tz = env_get(env, "CRON_TZ");
    e->tz = (tz != NULL) ? xstrdup(tz) : NULL;
    const char *mailto = env_get(env, "MAILTO");
    e->mailto = xstrdup((mailto != NULL) ? mailto : user);
    const char *shell = env_get(env, "SHELL");
    e->shell = xstrdup((shell != NULL) ? shell : "/bin/sh");

    /* CRON_TZ задає пояс і самому завданню, якщо TZ не оголошено явно. */
    const bool inherit_tz = (e->tz != NULL && env_get(env, "TZ") == NULL);
    e->envp = env_snapshot(env, inherit_tz ? "TZ" : NULL, inherit_tz ? e->tz : NULL);

    uint64_t hash = fnv1a(1469598103934665603ULL, user);
    hash = fnv1a(hash, e->command);
    size_t path_len = strlen(LOCK_DIR) + 40;
    e->lock_path = xmalloc(path_len);
    snprintf(e->lock_path, path_len, "%s/minicron-%016llx.lock",
             LOCK_DIR, (unsigned long long)hash);

    tab->count++;
}

static void entry_clear(entry_t *e)
{
    free(e->user);
    free(e->command);
    free(e->stdin_data);
    free(e->tz);
    free(e->mailto);
    free(e->shell);
    for (char **p = e->envp; p != NULL && *p != NULL; p++) {
        free(*p);
    }
    free(e->envp);
    free(e->lock_path);
    memset(e, 0, sizeof(*e));
}

static void crontab_clear(crontab_t *tab)
{
    for (size_t i = 0; i < tab->count; i++) {
        entry_clear(&tab->items[i]);
    }
    tab->count = 0;
}

static bool load_crontab(const char *path, bool system_table, crontab_t *tab)
{
    size_t file_len = 0;
    char *text = read_file(path, &file_len);
    if (text == NULL) {
        return false;
    }

    env_map_t env;
    memset(&env, 0, sizeof env);

    /* Дефолти демона; далі їх перекривають оголошення з таблиці зверху вниз. */
    struct passwd *self = getpwuid(getuid());
    const char *owner = (self != NULL) ? self->pw_name : "root";
    env_set(&env, "SHELL", "/bin/sh");
    env_set(&env, "PATH", "/usr/bin:/bin");
    env_set(&env, "HOME", (self != NULL) ? self->pw_dir : "/");
    env_set(&env, "LOGNAME", owner);
    env_set(&env, "USER", owner);

    size_t pos = 0;
    while (pos < file_len) {
        char *nl = memchr(text + pos, '\n', file_len - pos);
        if (nl == NULL) {
            /* Останній рядок без завершального '\n' Vixie мовчки ігнорує. */
            break;
        }
        size_t line_len = (size_t)(nl - (text + pos));
        char line[1024];
        if (line_len >= sizeof line) {
            fprintf(stderr, "minicron: рядок задовгий, пропущено\n");
            pos += line_len + 1;
            continue;
        }
        memcpy(line, text + pos, line_len);
        line[line_len] = '\0';
        pos += line_len + 1;

        const char *p = line;
        while (*p == ' ' || *p == '\t') {
            p++;
        }
        if (*p == '\0' || *p == '#') {
            continue;
        }

        char name[64];
        char value[512];
        if (parse_env_line(p, name, sizeof name, value, sizeof value)) {
            env_set(&env, name, value);
            continue;
        }

        cron_schedule_t sched;
        const char *rest = NULL;
        char err[192] = "";
        if (!cron_schedule_parse(p, &sched, &rest, err, sizeof err)) {
            fprintf(stderr, "minicron: %s: %s\n", path, err);
            continue;
        }

        char user[64];
        snprintf(user, sizeof user, "%s", owner);
        if (system_table) {
            while (*rest == ' ' || *rest == '\t') {
                rest++;
            }
            const char *start = rest;
            while (*rest != '\0' && !isspace((unsigned char)*rest)) {
                rest++;
            }
            size_t user_len = (size_t)(rest - start);
            if (user_len == 0 || user_len >= sizeof user) {
                fprintf(stderr, "minicron: %s: бракує поля користувача\n", path);
                continue;
            }
            memcpy(user, start, user_len);
            user[user_len] = '\0';
        }
        while (*rest == ' ' || *rest == '\t') {
            rest++;
        }
        if (*rest == '\0') {
            fprintf(stderr, "minicron: %s: рядок розкладу без команди\n", path);
            continue;
        }
        add_entry(tab, &sched, user, rest, &env);
    }

    env_clear(&env);
    free(text);
    return true;
}

/* CRON_TZ діє на обчислення розкладу саме цього рядка. */
static void entry_localtime(const entry_t *e, time_t t, struct tm *out)
{
    if (e->tz == NULL) {
        localtime_r(&t, out);
        return;
    }
    char saved[64] = "";
    const char *current = getenv("TZ");
    const bool had_tz = (current != NULL);
    if (had_tz) {
        snprintf(saved, sizeof saved, "%s", current);
    }
    setenv("TZ", e->tz, 1);
    tzset();
    localtime_r(&t, out);
    if (had_tz) {
        setenv("TZ", saved, 1);
    } else {
        unsetenv("TZ");
    }
    tzset();
}

/* Другий рівень розгалуження: замок і саме завдання живуть у власному процесі,
   тож головний цикл планування нічого не чекає. */
static void launch(entry_t *e)
{
    pid_t pid = fork();
    if (pid < 0) {
        perror("minicron: fork");
        return;
    }
    if (pid > 0) {
        return;
    }

    int lock_fd = -1;
    switch (job_lock_acquire(e->lock_path, &lock_fd)) {
    case JOB_LOCK_BUSY:
        fprintf(stderr, "minicron: «%s» ще виконується, запуск пропущено\n", e->command);
        _exit(0);
    case JOB_LOCK_ERROR:
        _exit(1);
    case JOB_LOCK_HELD:
        break;
    }

    cron_job_t job;
    job.user = e->user;
    job.command = e->command;
    job.stdin_data = e->stdin_data;
    job.mailto = e->mailto;
    job.shell = e->shell;
    job.envp = e->envp;

    int rc = cron_job_run(&job);
    job_lock_release(lock_fd);
    _exit((rc < 0) ? 1 : 0);
}

/* Проміжні процеси живуть недовго; прибираємо їх на кожному тіку, щоб не
   лишати зомбі до кінця роботи демона. */
static void reap_children(void)
{
    while (waitpid(-1, NULL, WNOHANG) > 0) {
        continue;
    }
}

static void run_minute(crontab_t *tab, time_t minute)
{
    for (size_t i = 0; i < tab->count; i++) {
        entry_t *e = &tab->items[i];
        struct tm tm_local;
        entry_localtime(e, minute, &tm_local);
        if (cron_schedule_matches(&e->schedule, &tm_local)) {
            launch(e);
        }
    }
}

static void reload(app_t *app)
{
    crontab_t fresh;
    memset(&fresh, 0, sizeof fresh);
    if (!load_crontab(app->path, app->system_table, &fresh)) {
        fprintf(stderr, "minicron: таблицю не перечитано, лишаю попередню\n");
        crontab_clear(&fresh);
        return;
    }
    crontab_clear(&app->tab);
    app->tab = fresh;
    /* @reboot повторно НЕ запускаємо: фазу завантаження вже пройдено — саме
       тому «crontab -e» не перезапускає таких завдань. */
    fprintf(stderr, "minicron: таблицю перечитано, завдань: %zu\n", app->tab.count);
}

static void on_config_change(int fd, void *user_data)
{
    (void)fd;
    app_t *app = user_data;
    if (cron_watch_changed(app->watch)) {
        reload(app);
    }
}

static void on_minute(uint64_t expirations, void *user_data)
{
    (void)expirations;
    app_t *app = user_data;

    /* Там, де inotify недоступний, зміни ловимо звичайним stat() — рівно раз
       на хвилину, як це робить класичний Vixie cron. */
    if (cron_watch_fd(app->watch) < 0 && cron_watch_changed(app->watch)) {
        reload(app);
    }

    time_t now = time(NULL);
    time_t minute = now - (now % 60);

    if (minute <= g_last_minute) {
        /* Годинник стрибнув назад (осінній перехід, корекція NTP): хвилину,
           яку вже відпрацювали, вдруге не запускаємо. */
        reap_children();
        return;
    }

    /* Стрибок уперед (весняний перехід, вихід зі сну): проходимо пропущені
       хвилини, але не глибше за годину — інакше черга вибухне. */
    time_t start = g_last_minute + 60;
    if (minute - start > CATCHUP_SECONDS) {
        start = minute - CATCHUP_SECONDS;
    }
    for (time_t t = start; t <= minute; t += 60) {
        run_minute(&app->tab, t);
    }
    g_last_minute = minute;
    reap_children();
}

static void on_signal(int signo)
{
    (void)signo;
    timer_loop_stop(g_loop);
}

int main(int argc, char **argv)
{
    static app_t app;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-s") == 0) {
            app.system_table = true;
        } else if (app.path == NULL) {
            app.path = argv[i];
        } else {
            fprintf(stderr, "Використання: %s [-s] <файл crontab>\n", argv[0]);
            return 2;
        }
    }
    if (app.path == NULL) {
        fprintf(stderr, "Використання: %s [-s] <файл crontab>\n", argv[0]);
        return 2;
    }

    if (!load_crontab(app.path, app.system_table, &app.tab)) {
        return 1;
    }
    if (app.tab.count == 0) {
        fprintf(stderr, "minicron: у таблиці немає жодного завдання\n");
        return 1;
    }

    /* Стежимо і за файлом, і за його каталогом: редактор зберігає таблицю
       через тимчасовий файл і rename(), після якого стеження за самим
       файлом уже вказує в нікуди. */
    char dir_buf[512];
    snprintf(dir_buf, sizeof dir_buf, "%s", app.path);
    const char *watched[2] = {app.path, dirname(dir_buf)};
    app.watch = cron_watch_open(watched, 2);
    if (app.watch == NULL) {
        perror("minicron: cron_watch_open");
        crontab_clear(&app.tab);
        return 1;
    }

    /* @reboot — рівно один запуск під час ініціалізації демона. */
    for (size_t i = 0; i < app.tab.count; i++) {
        if ((app.tab.items[i].schedule.flags & CRON_AT_REBOOT) != 0u) {
            launch(&app.tab.items[i]);
        }
    }

    g_loop = timer_loop_create();
    if (g_loop == NULL) {
        cron_watch_close(app.watch);
        crontab_clear(&app.tab);
        return 1;
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    /* Хвилинна сітка й так груба, тож дозволяємо ядру звести наше пробудження
       з чужим у межах 200 мс — процесор вийде зі сну один раз замість двох. */
    timer_loop_set_slack_ns(SLACK_NS);
    fprintf(stderr, "minicron: вікно коалесценції — %ld нс\n",
            timer_loop_read_slack_ns());

    time_t now = time(NULL);
    g_last_minute = now - (now % 60);

    /* Прокидаємось не «через 60 с», а точно на нульовій секунді наступної
       хвилини — інакше розклад повільно дрейфував би вперед. */
    struct itimerspec spec;
    memset(&spec, 0, sizeof spec);
    spec.it_value.tv_sec = cron_seconds_to_next_minute(now);
    spec.it_interval.tv_sec = 60;

    int rc = 1;
    if (timer_loop_add_timer(g_loop, CLOCK_REALTIME, &spec, 0, on_minute, &app) == 0) {
        /* inotify — звичайний дескриптор, тож живе в тому самому epoll, що й
           таймер: окремого потоку чи сигналу для нього не потрібно. */
        const int watch_fd = cron_watch_fd(app.watch);
        if (watch_fd < 0 ||
            timer_loop_add_fd(g_loop, watch_fd, on_config_change, &app) == 0) {
            fprintf(stderr, "minicron: %zu завдань, чекаю на хвилинний тік\n",
                    app.tab.count);
            rc = (timer_loop_run(g_loop) == 0) ? 0 : 1;
        }
    }

    timer_loop_destroy(g_loop);
    cron_watch_close(app.watch);
    crontab_clear(&app.tab);
    reap_children();
    return rc;
}
