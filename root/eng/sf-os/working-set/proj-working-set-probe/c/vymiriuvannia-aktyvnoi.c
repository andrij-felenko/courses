#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

/*
 * Зчитує поле Referenced (у кілобайтах) із файлу /proc/[pid]/smaps_rollup.
 * Повертає 0 у разі успіху, -1 у разі помилки.
 */
static int read_referenced_kb(pid_t pid, unsigned long *referenced_kb, unsigned long *rss_kb) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/smaps_rollup", pid);

    FILE *f = fopen(path, "r");
    if (!f) {
        return -1;
    }

    char line[256];
    *referenced_kb = 0;
    *rss_kb = 0;
    int found = 0;

    while (fgets(line, sizeof(line), f)) {
        if (sscanf(line, "Rss: %lu kB", rss_kb) == 1) {
            found |= 1;
        } else if (sscanf(line, "Referenced: %lu kB", referenced_kb) == 1) {
            found |= 2;
        }
        if (found == 3) {
            break;
        }
    }

    fclose(f);
    return (found & 2) ? 0 : -1;
}

/*
 * Скидає біти звернення PTE через /proc/[pid]/clear_refs.
 */
static int clear_referenced_bits(pid_t pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/clear_refs", pid);

    FILE *f = fopen(path, "w");
    if (!f) {
        return -1;
    }

    if (fputs("1\n", f) == EOF) {
        fclose(f);
        return -1;
    }

    fclose(f);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <pid> <вікно_сек>\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    int delta_sec = atoi(argv[2]);

    if (pid <= 0 || delta_sec <= 0) {
        fprintf(stderr, "Помилка: PID та інтервал мають бути додатними числами.\n");
        return EXIT_FAILURE;
    }

    printf("=== Інспекція робочої множини процесу PID=%d (вікно Δ=%d с) ===\n", pid, delta_sec);

    if (clear_referenced_bits(pid) != 0) {
        fprintf(stderr, "Помилка запису в /proc/%d/clear_refs: %s (потрібні права root або власника)\n",
                pid, strerror(errno));
        return EXIT_FAILURE;
    }

    printf("Біти звернення MMU скинуто. Збір статистики звернень протягом %d с...\n", delta_sec);
    sleep(delta_sec);

    unsigned long referenced_kb = 0;
    unsigned long rss_kb = 0;

    if (read_referenced_kb(pid, &referenced_kb, &rss_kb) != 0) {
        fprintf(stderr, "Помилка зчитування /proc/%d/smaps_rollup: %s\n", pid, strerror(errno));
        return EXIT_FAILURE;
    }

    double ws_ratio = (rss_kb > 0) ? ((double)referenced_kb / (double)rss_kb) * 100.0 : 0.0;

    printf("Загальний обсяг резидентної пам'яті (RSS): %lu kB\n", rss_kb);
    printf("Активна робоча множина W(t, Δ):           %lu kB\n", referenced_kb);
    printf("Частка активно використовуваної пам'яті:   %.2f%%\n", ws_ratio);

    return EXIT_SUCCESS;
}
