/* loader.c — C імплементація з класичним низькорівневим API libbpf */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>
#include <bpf/libbpf.h>
#include "lsm_policy.skel.h"

static volatile bool keep_running = true;

static void sig_handler(int sig) {
    keep_running = false;
}

// Callback-функція, яка викликається при появі нової події у Ring Buffer
static int handle_event(void *ctx, void *data, size_t data_sz) {
    const struct audit_event *evt = data;
    
    printf("[AUDIT LOG] PID: %-6d | PPID: %-6d | UID: %-4d | Comm: %-10s | Action: %s | File: %s\n",
           evt->pid, evt->ppid, evt->uid, evt->comm,
           evt->blocked ? "\033[1;31mDENIED\033[0m" : "\033[1;32mALLOWED\033[0m",
           evt->filename);
    return 0;
}

int main(int argc, char **argv) {
    struct lsm_policy_bpf *skel = NULL;
    struct ring_buffer *rb = NULL;
    int err;

    // Встановлюємо обробники сигналів для коректного завершення
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // 1. Відкриваємо та завантажуємо BPF-програму в ядро
    skel = lsm_policy_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "ERROR: Failed to open and load BPF skeleton\n");
        return 1;
    }

    // 2. Прикріплюємо програму до LSM-хука
    err = lsm_policy_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "ERROR: Failed to attach BPF LSM program: %d\n", err);
        goto cleanup;
    }

    // 3. Ініціалізуємо споживача Ring Buffer
    rb = ring_buffer__new(bpf_map__fd(skel->maps.audit_ringbuf), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "ERROR: Failed to create ring buffer consumer\n");
        goto cleanup;
    }

    printf("====================================================================\n");
    printf(" BPF-LSM Enforcement & Audit Daemon Started Successfully\n");
    printf(" Monitoring 'bprm_check_security' hook. Press Ctrl+C to stop.\n");
    printf("====================================================================\n");

    // Головний цикл опитування Ring Buffer
    while (keep_running) {
        err = ring_buffer__poll(rb, 100 /* ms timeout */);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "ERROR: Ring buffer polling failed: %d\n", err);
            break;
        }
    }

cleanup:
    // Порядок очищення ресурсів у C
    if (rb) ring_buffer__free(rb);
    if (skel) lsm_policy_bpf__destroy(skel);
    printf("\n[INFO] BPF-LSM Policy detached. Daemon exiting safely.\n");
    return 0;
}
