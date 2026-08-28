/* proc_spy.c — Неінвазивний аналізатор стану процесу через procfs (C99 / POSIX) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>

#define BUF_SIZE 4096

typedef struct {
    char state[32];
    int threads;
    unsigned long voluntary_switches;
    unsigned long nonvoluntary_switches;
    unsigned long vmrss_kb;
} ProcessStatus;

static int read_status(pid_t pid, ProcessStatus *ps) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/status", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char line[256];
    memset(ps, 0, sizeof(*ps));

    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "State:", 6) == 0) {
            sscanf(line + 6, "%31s", ps->state);
        } else if (strncmp(line, "Threads:", 8) == 0) {
            sscanf(line + 8, "%d", &ps->threads);
        } else if (strncmp(line, "VmRSS:", 6) == 0) {
            sscanf(line + 6, "%lu", &ps->vmrss_kb);
        } else if (strncmp(line, "vvoluntary_ctxt_switches:", 24) == 0) {
            sscanf(line + 24, "%lu", &ps->voluntary_switches);
        } else if (strncmp(line, "nonvvoluntary_ctxt_switches:", 27) == 0) {
            sscanf(line + 27, "%lu", &ps->nonvoluntary_switches);
        }
    }
    fclose(f);
    return 0;
}

static void print_file_content(const char *title, const char *path) {
    printf("=== %s ===\n", title);
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        if (errno == EACCES) {
            printf("  [Увага: для читання потрібні права root або CAP_SYS_ADMIN]\n");
        } else {
            printf("  [Не вдалося відкрити: %s]\n", strerror(errno));
        }
        return;
    }

    char buf[BUF_SIZE];
    ssize_t bytes_read = read(fd, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("%s", buf);
    } else if (bytes_read == 0) {
        printf("  [Порожньо: процес активний на CPU або завершився]\n");
    }
    close(fd);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID>\n", argv[0]);
        return 1;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    if (pid <= 0) {
        fprintf(stderr, "Помилка: некоректний PID %s\n", argv[1]);
        return 1;
    }

    ProcessStatus ps;
    if (read_status(pid, &ps) != 0) {
        fprintf(stderr, "Помилка: процес із PID %d не знайдено або доступ заборонено (%s)\n",
                pid, strerror(errno));
        return 1;
    }

    printf("====================================================\n");
    printf("ДІАГНОСТИЧНИЙ ПАСПОРТ ПРОЦЕСУ PID: %d\n", pid);
    printf("====================================================\n");
    printf("Стан (State):             %s\n", ps.state);
    printf("Кількість ниток (Threads):%d\n", ps.threads);
    printf("Резидентна пам'ять (RSS): %lu KiB (%.2f MiB)\n", ps.vmrss_kb, ps.vmrss_kb / 1024.0);
    printf("Добровільні перемикання:  %lu (очікування I/O або замків)\n", ps.voluntary_switches);
    printf("Примусові перемикання:    %lu (витіснення планувальником)\n", ps.nonvoluntary_switches);

    unsigned long total_sw = ps.voluntary_switches + ps.nonvoluntary_switches;
    if (total_sw > 0) {
        double vol_pct = (double)ps.voluntary_switches / total_sw * 100.0;
        printf("Частка добровільних:      %.1f%%\n", vol_pct);
    }
    printf("\n");

    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/wchan", pid);
    print_file_content("Канал очікування ядра (wchan)", path);
    printf("\n");

    snprintf(path, sizeof(path), "/proc/%d/stack", pid);
    print_file_content("Стек викликів ядра сплячого потоку (stack)", path);

    return 0;
}
