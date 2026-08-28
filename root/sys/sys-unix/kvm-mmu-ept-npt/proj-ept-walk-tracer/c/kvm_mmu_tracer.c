/*
 * kvm_mmu_tracer.c — моніторинг подій KVM MMU та EPT через tracefs
 * Компіляція: gcc -O2 -Wall kvm_mmu_tracer.c -o kvm_mmu_tracer
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <time.h>

#define TRACE_BASE "/sys/kernel/tracing"
#define FALLBACK_TRACE_BASE "/sys/kernel/debug/tracing"

static volatile sig_atomic_t g_running = 1;

static void sig_handler(int sig) {
    (void)sig;
    g_running = 0;
}

static int write_file(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    ssize_t len = strlen(val);
    if (write(fd, val, len) != len) {
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

static const char *get_tracefs_root(void) {
    if (access(TRACE_BASE "/trace_pipe", R_OK) == 0) {
        return TRACE_BASE;
    }
    if (access(FALLBACK_TRACE_BASE "/trace_pipe", R_OK) == 0) {
        return FALLBACK_TRACE_BASE;
    }
    return NULL;
}

int main(void) {
    const char *root = get_tracefs_root();
    if (!root) {
        fprintf(stderr, "Помилка: tracefs не змонтовано або відсутні права root\n");
        return 1;
    }

    char path[256];
    snprintf(path, sizeof(path), "%s/events/kvm/kvm_exit/enable", root);
    if (write_file(path, "1") < 0) {
        perror("Не вдалося активувати kvm_exit");
        return 1;
    }

    snprintf(path, sizeof(path), "%s/events/kvm/kvm_page_fault/enable", root);
    write_file(path, "1");

    snprintf(path, sizeof(path), "%s/trace_pipe", root);
    FILE *pipe = fopen(path, "r");
    if (!pipe) {
        perror("Не вдалося відкрити trace_pipe");
        return 1;
    }

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    printf("Розпочато трасування KVM MMU подій (Ctrl+C для виходу)...\n");

    char line[1024];
    unsigned long long ept_violations = 0;
    unsigned long long ept_misconfigs = 0;
    unsigned long long page_faults = 0;
    unsigned long long other_exits = 0;

    time_t last_report = time(NULL);

    while (g_running && fgets(line, sizeof(line), pipe)) {
        if (strstr(line, "kvm_exit:")) {
            /* 0x30 = 48 (EPT Violation), 0x31 = 49 (EPT Misconfig) */
            if (strstr(line, "reason 0x30") || strstr(line, "reason EPT_VIOLATION")) {
                ept_violations++;
            } else if (strstr(line, "reason 0x31") || strstr(line, "reason EPT_MISCONFIG")) {
                ept_misconfigs++;
            } else {
                other_exits++;
            }
        } else if (strstr(line, "kvm_page_fault:")) {
            page_faults++;
        }

        time_t now = time(NULL);
        if (now - last_report >= 1) {
            printf("\r[KVM MMU] EPT Violations: %llu/s | Page Faults: %llu/s | Misconfigs: %llu/s | Інші виходи: %llu/s",
                   ept_violations, page_faults, ept_misconfigs, other_exits);
            fflush(stdout);
            ept_violations = 0;
            ept_misconfigs = 0;
            page_faults = 0;
            other_exits = 0;
            last_report = now;
        }
    }

    printf("\nЗавершення роботи. Вимикаємо точки трасування...\n");
    snprintf(path, sizeof(path), "%s/events/kvm/kvm_exit/enable", root);
    write_file(path, "0");
    snprintf(path, sizeof(path), "%s/events/kvm/kvm_page_fault/enable", root);
    write_file(path, "0");
    fclose(pipe);

    return 0;
}
