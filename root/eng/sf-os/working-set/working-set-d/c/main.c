#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

/*
 * Зчитує показники RSS та Referenced зі smaps_rollup для заданого PID.
 */
static int get_working_set_kb(pid_t pid, unsigned long *rss_kb, unsigned long *ref_kb) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/smaps_rollup", pid);

    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char line[256];
    *rss_kb = 0;
    *ref_kb = 0;

    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "Rss:", 4) == 0) {
            sscanf(line + 4, "%lu", rss_kb);
        } else if (strncmp(line, "Referenced:", 11) == 0) {
            sscanf(line + 11, "%lu", ref_kb);
        }
    }

    fclose(f);
    return 0;
}

/*
 * Скидає біти звернення через clear_refs.
 */
static int reset_page_references(pid_t pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/clear_refs", pid);

    FILE *f = fopen(path, "w");
    if (!f) return -1;

    fputs("1\n", f);
    fclose(f);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <pid> <вікно_сек>\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    int window_sec = atoi(argv[2]);

    if (reset_page_references(pid) != 0) {
        perror("Не вдалося скинути біти звернення (перевірте права доступу)");
        return EXIT_FAILURE;
    }

    printf("Спостереження за процесом PID=%d протягом %d с...\n", pid, window_sec);
    sleep(window_sec);

    unsigned long rss = 0, referenced = 0;
    if (get_working_set_kb(pid, &rss, &referenced) != 0) {
        perror("Помилка зчитування smaps_rollup");
        return EXIT_FAILURE;
    }

    double active_ratio = (rss > 0) ? ((double)referenced / (double)rss) * 100.0 : 0.0;

    printf("Повна резидентна пам'ять (RSS):       %lu kB\n", rss);
    printf("Активна робоча множина W(t, Δ):        %lu kB\n", referenced);
    printf("Частка активно задіяної пам'яті:       %.1f %%\n", active_ratio);

    return EXIT_SUCCESS;
}
