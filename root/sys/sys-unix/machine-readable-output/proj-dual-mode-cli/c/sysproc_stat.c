/* sysproc_stat.c — Реалізація дуального CLI мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <sys/ioctl.h>

#define ANSI_RESET   "\033[0m"
#define ANSI_BOLD    "\033[1m"
#define ANSI_GREEN   "\033[32m"
#define ANSI_YELLOW  "\033[33m"
#define ANSI_CYAN    "\033[36m"
#define ANSI_RED     "\033[31m"

typedef enum {
    OUT_AUTO,
    OUT_HUMAN,
    OUT_JSON,
    OUT_TSV
} OutputMode;

typedef struct {
    pid_t pid;
    char name[64];
    char state;
    uint64_t rss_bytes;
    uint64_t vsz_bytes;
} ProcessMetric;

typedef struct {
    OutputMode mode;
    bool enable_color;
    bool null_delimited;
    bool no_heading;
} Config;

/* Перевірка стандартів NO_COLOR, CLICOLOR та стану TTY */
static bool detect_color_support(int fd) {
    const char *no_color = getenv("NO_COLOR");
    if (no_color && no_color[0] != '\0') {
        return false;
    }
    const char *clicolor_force = getenv("CLICOLOR_FORCE");
    if (clicolor_force && strcmp(clicolor_force, "0") != 0) {
        return true;
    }
    const char *term = getenv("TERM");
    if (term && strcmp(term, "dumb") == 0) {
        return false;
    }
    const char *clicolor = getenv("CLICOLOR");
    if (clicolor && strcmp(clicolor, "0") == 0) {
        return false;
    }
    return isatty(fd) == 1;
}

/* Форматування байтів у двійкові одиниці IEC (KiB, MiB, GiB) */
static void format_human_bytes(uint64_t bytes, char *buf, size_t buflen) {
    const char *units[] = {"B", "KiB", "MiB", "GiB", "TiB"};
    double size = (double)bytes;
    int unit_idx = 0;
    while (size >= 1024.0 && unit_idx < 4) {
        size /= 1024.0;
        unit_idx++;
    }
    if (unit_idx == 0) {
        snprintf(buf, buflen, "%" PRIu64 " B", bytes);
    } else {
        snprintf(buf, buflen, "%.1f %s", size, units[unit_idx]);
    }
}

/* Вивід у людському форматі */
static void print_human(const ProcessMetric *procs, size_t count, bool color, bool no_heading) {
    if (!no_heading) {
        if (color) {
            printf("%s%-8s %-20s %-8s %-12s %-12s%s\n",
                   ANSI_BOLD, "PID", "NAME", "STATE", "RSS", "VSZ", ANSI_RESET);
        } else {
            printf("%-8s %-20s %-8s %-12s %-12s\n",
                   "PID", "NAME", "STATE", "RSS", "VSZ");
        }
    }

    char rss_str[32], vsz_str[32];
    for (size_t i = 0; i < count; i++) {
        format_human_bytes(procs[i].rss_bytes, rss_str, sizeof(rss_str));
        format_human_bytes(procs[i].vsz_bytes, vsz_str, sizeof(vsz_str));

        if (color) {
            const char *state_col = (procs[i].state == 'R') ? ANSI_GREEN : ANSI_CYAN;
            printf("%-8d %-20s %s%-8c%s %-12s %-12s\n",
                   procs[i].pid, procs[i].name,
                   state_col, procs[i].state, ANSI_RESET,
                   rss_str, vsz_str);
        } else {
            printf("%-8d %-20s %-8c %-12s %-12s\n",
                   procs[i].pid, procs[i].name, procs[i].state, rss_str, vsz_str);
        }
    }
}

/* Вивід у машинному форматі TSV */
static void print_tsv(const ProcessMetric *procs, size_t count, bool no_heading, bool null_delim) {
    char term = null_delim ? '\0' : '\n';
    if (!no_heading && !null_delim) {
        printf("pid\tname\tstate\trss_bytes\tvsz_bytes\n");
    }
    for (size_t i = 0; i < count; i++) {
        printf("%d\t%s\t%c\t%" PRIu64 "\t%" PRIu64 "%c",
               procs[i].pid, procs[i].name, procs[i].state,
               procs[i].rss_bytes, procs[i].vsz_bytes, term);
    }
}

/* Вивід у машинному форматі JSON */
static void print_json(const ProcessMetric *procs, size_t count) {
    printf("{\n  \"timestamp\": %ld,\n  \"processes\": [\n", (long)time(NULL));
    for (size_t i = 0; i < count; i++) {
        printf("    {\n"
               "      \"pid\": %d,\n"
               "      \"name\": \"%s\",\n"
               "      \"state\": \"%c\",\n"
               "      \"rss_bytes\": %" PRIu64 ",\n"
               "      \"vsz_bytes\": %" PRIu64 "\n"
               "    }%s\n",
               procs[i].pid, procs[i].name, procs[i].state,
               procs[i].rss_bytes, procs[i].vsz_bytes,
               (i + 1 < count) ? "," : "");
    }
    printf("  ]\n}\n");
}

int main(int argc, char **argv) {
    /* Безпечна обробка розриву конвеєра */
    signal(SIGPIPE, SIG_DFL);

    Config cfg = {
        .mode = OUT_AUTO,
        .enable_color = false,
        .null_delimited = false,
        .no_heading = false
    };

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--json") == 0 || strcmp(argv[i], "-j") == 0) {
            cfg.mode = OUT_JSON;
        } else if (strcmp(argv[i], "--raw") == 0 || strcmp(argv[i], "--tsv") == 0) {
            cfg.mode = OUT_TSV;
        } else if (strcmp(argv[i], "--human") == 0 || strcmp(argv[i], "-H") == 0) {
            cfg.mode = OUT_HUMAN;
        } else if (strcmp(argv[i], "-z") == 0 || strcmp(argv[i], "--null") == 0) {
            cfg.null_delimited = true;
            cfg.mode = OUT_TSV;
        } else if (strcmp(argv[i], "--no-heading") == 0 || strcmp(argv[i], "-n") == 0) {
            cfg.no_heading = true;
        }
    }

    bool is_terminal = isatty(STDOUT_FILENO) == 1;

    /* Автоматичний вибір режиму виводу на основі типу дескриптора */
    if (cfg.mode == OUT_AUTO) {
        cfg.mode = is_terminal ? OUT_HUMAN : OUT_TSV;
    }

    cfg.enable_color = (cfg.mode == OUT_HUMAN) && detect_color_support(STDOUT_FILENO);

    /* Налаштування оптимальної буферизації потоку */
    if (cfg.mode == OUT_HUMAN && is_terminal) {
        setvbuf(stdout, NULL, _IOLBF, 0);
    } else {
        setvbuf(stdout, NULL, _IOFBF, 8192);
    }

    /* Симуляція зібраних метрик процесів */
    ProcessMetric sample_procs[] = {
        {1, "systemd", 'S', 12451840, 168427520},
        {412, "dbus-daemon", 'S', 4890624, 25165824},
        {1024, "nginx", 'S', 34078720, 142606336},
        {2048, "rust-worker", 'R', 268435456, 1073741824}
    };
    size_t count = sizeof(sample_procs) / sizeof(sample_procs[0]);

    switch (cfg.mode) {
        case OUT_JSON:
            print_json(sample_procs, count);
            break;
        case OUT_TSV:
            print_tsv(sample_procs, count, cfg.no_heading, cfg.null_delimited);
            break;
        case OUT_HUMAN:
        case OUT_AUTO:
            print_human(sample_procs, count, cfg.enable_color, cfg.no_heading);
            break;
    }

    return 0;
}
