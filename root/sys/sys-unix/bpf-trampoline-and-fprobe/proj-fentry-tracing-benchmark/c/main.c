/* main.c — Ідіоматична реалізація мовою C (libbpf C API) */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <bpf/libbpf.h>
#include "bench.skel.h"

static volatile bool exiting = false;

static void sig_handler(int sig)
{
    exiting = true;
}

int main(int argc, char **argv)
{
    struct bench_bpf *skel;
    int err;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* 1. Відкриття та завантаження BPF-скелета */
    skel = bench_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка завантаження BPF-скелета\n");
        return 1;
    }

    /* 2. Приєднання програм fentry та kprobe */
    err = bench_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Помилка приєднання BPF-програм: %d\n", err);
        bench_bpf__destroy(skel);
        return 1;
    }

    printf("Бенчмарк запущено. Натисніть Ctrl+C для зупинки...\n");

    /* 3. Головний цикл зчитування статистики */
    while (!exiting) {
        sleep(1);
        
        uint32_t kprobe_key = 0, fentry_key = 1;
        uint64_t kprobe_time = 0, fentry_time = 0;

        bpf_map__lookup_elem(skel->maps.bench_stats, &kprobe_key, sizeof(kprobe_key),
                             &kprobe_time, sizeof(kprobe_time), 0);
        bpf_map__lookup_elem(skel->maps.bench_stats, &fentry_key, sizeof(fentry_key),
                             &fentry_time, sizeof(fentry_time), 0);

        printf("[Статистика] Kprobe total: %llu ns | Fentry total: %llu ns\n",
               (unsigned long long)kprobe_time, (unsigned long long)fentry_time);
    }

    bench_bpf__destroy(skel);
    return 0;
}
