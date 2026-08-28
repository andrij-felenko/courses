#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "my_fifo.skel.h"

static volatile sig_atomic_t stop = 0;

static void sig_handler(int sig)
{
    (void)sig;
    stop = 1;
}

int main(int argc, char **argv)
{
    struct my_fifo_bpf *skel = NULL;
    struct bpf_link *link = NULL;
    int err;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // 1. Відкриваємо та завантажуємо BPF скелет у ядро
    skel = my_fifo_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка: не вдалося відкрити або завантажити BPF скелет\n");
        return 1;
    }

    // 2. Приєднуємо struct_ops до ядра (вмикає планувальник sched_ext)
    link = bpf_map__attach_struct_ops(skel->maps.fifo_ops);
    if (!link) {
        fprintf(stderr, "Помилка: не вдалося приєднати struct_ops до sched_ext\n");
        my_fifo_bpf__destroy(skel);
        return 1;
    }

    printf("Планувальник simple_fifo успішно завантажено та активовано в ядрі.\n");
    printf("Натисніть Ctrl+C для вивантаження...\n");

    while (!stop) {
        sleep(1);
    }

    printf("\nВивантаження планувальника sched_ext...\n");
    bpf_link__destroy(link);
    my_fifo_bpf__destroy(skel);
    printf("Система повернулася до стандартного планувальника EEVDF.\n");
    return 0;
}
