#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "exec_monitor.skel.h"
#include "exec_event.h"   // спільне оголошення struct exec_event

static volatile bool exiting = false;

// Обробник сигналів для коректного завершення роботи
static void sig_handler(int sig)
{
    exiting = true;
}

// Функція обробки події, яка викликається бібліотекою libbpf при отриманні даних з Ring Buffer
static int handle_event(void *ctx, void *data, size_t data_sz)
{
    const struct exec_event *e = data;
    printf("[EXEC] PID: %6d | PPID: %6d | UID: %4d | GID: %4d | COMM: %-16s | PATH: %s\n",
           e->pid, e->ppid, e->uid, e->gid, e->comm, e->filename);
    return 0;
}

int main(int argc, char **argv)
{
    struct exec_monitor_bpf *skel;
    struct ring_buffer *rb = NULL;
    int err;

    // Реєстрація обробників сигналів SIGINT та SIGTERM
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // 1. Відкриття та завантаження BPF-скелета у ядро
    skel = exec_monitor_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка: не вдалося завантажити BPF-скелет\n");
        return 1;
    }

    // 2. Прив'язка BPF-програми до точки tracepoint sys_enter_execve
    err = exec_monitor_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Помилка: не вдалося прив'язати BPF-програму: %d\n", err);
        goto cleanup;
    }

    // 3. Створення об'єкта Ring Buffer із вказівником на колбек handle_event
    rb = ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка: не вдалося створити Ring Buffer\n");
        goto cleanup;
    }

    printf("eBPF Process Monitor (C) успішно запущено. Натисніть Ctrl-C для виходу...\n");

    // 4. Головний цикл зчитування подій з таймаутом 100 мс
    while (!exiting) {
        err = ring_buffer__poll(rb, 100);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка читання Ring Buffer: %d\n", err);
            break;
        }
    }

cleanup:
    // Звільнення ресурсів у зворотному порядку
    ring_buffer__free(rb);
    exec_monitor_bpf__destroy(skel);
    printf("\nМонітор зупинено, ресурси звільнено.\n");
    return 0;
}
