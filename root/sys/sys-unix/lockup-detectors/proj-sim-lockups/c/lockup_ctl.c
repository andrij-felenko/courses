/* lockup_ctl.c — Утиліта моніторингу та ініціалізації тестів зависань ядра (C99/POSIX) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

static void print_usage(const char *prog) {
    fprintf(stderr, "Використання: %s <soft|hard|hung|status>\n", prog);
    fprintf(stderr, "  soft   - викликати Soft Lockup (25 с утримування spinlock)\n");
    fprintf(stderr, "  hard   - викликати Hard Lockup (local_irq_disable + dead loop)\n");
    fprintf(stderr, "  hung   - викликати Hung Task (150 с у TASK_UNINTERRUPTIBLE)\n");
    fprintf(stderr, "  status - перевірити поточні параметри watchdog у sysctl\n");
}

static int read_sysctl_int(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    char buf[32] = {0};
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return -1;
    return atoi(buf);
}

static void show_status(void) {
    printf("=== Стан сторожових таймерів ядра Linux ===\n");
    printf("kernel.watchdog:         %d\n", read_sysctl_int("/proc/sys/kernel/watchdog"));
    printf("kernel.watchdog_thresh:  %d с\n", read_sysctl_int("/proc/sys/kernel/watchdog_thresh"));
    printf("kernel.nmi_watchdog:     %d\n", read_sysctl_int("/proc/sys/kernel/nmi_watchdog"));
    printf("kernel.softlockup_panic: %d\n", read_sysctl_int("/proc/sys/kernel/softlockup_panic"));
    printf("kernel.hardlockup_panic: %d\n", read_sysctl_int("/proc/sys/kernel/hardlockup_panic"));
    printf("kernel.hung_task_timeout:%d с\n", read_sysctl_int("/proc/sys/kernel/hung_task_timeout_secs"));
    printf("kernel.hung_task_panic:  %d\n", read_sysctl_int("/proc/sys/kernel/hung_task_panic"));
}

static int write_trigger(const char *node) {
    char path[128];
    snprintf(path, sizeof(path), "/sys/kernel/debug/lockup_trigger/%s", node);
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s (чи завантажено модуль?)\n",
                path, strerror(errno));
        return 1;
    }
    if (write(fd, "1", 1) < 0) {
        fprintf(stderr, "Помилка запису у тригер: %s\n", strerror(errno));
        close(fd);
        return 1;
    }
    close(fd);
    printf("Тригер '%s' успішно активовано.\n", node);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "status") == 0) {
        show_status();
        return 0;
    } else if (strcmp(argv[1], "soft") == 0) {
        return write_trigger("trigger_soft_lockup");
    } else if (strcmp(argv[1], "hard") == 0) {
        return write_trigger("trigger_hard_lockup");
    } else if (strcmp(argv[1], "hung") == 0) {
        return write_trigger("trigger_hung_task");
    } else {
        print_usage(argv[0]);
        return 1;
    }
}
