#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "execve_event.h"

static volatile bool keep_running = true;

static void sig_handler(int sig)
{
    (void)sig;
    keep_running = false;
}

/* Callback для обробки звичайних подій */
static void handle_event(void *ctx, int cpu, void *data, __u32 data_sz)
{
    (void)ctx;
    (void)data_sz;
    const struct execve_event *e = (const struct execve_event *)data;
    printf("[CPU %2d] TIME: %12llu ns | PID: %6u | COMM: %s\n",
           cpu, e->boot_time_ns, e->pid, e->comm);
}

/* Callback для обробки втрачених подій при переповненні */
static void handle_lost_events(void *ctx, int cpu, __u64 lost_cnt)
{
    (void)ctx;
    fprintf(stderr, "УВАГА: Втрачено %llu подій на CPU %d!\n", lost_cnt, cpu);
}

int main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    struct bpf_object *obj = NULL;
    struct perf_buffer *pb = NULL;
    int map_fd, err;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* Завантажуємо eBPF об'єкт з файла */
    obj = bpf_object__open_file("execve_monitor.bpf.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "Помилка відкриття BPF об'єкта execve_monitor.bpf.o\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка завантаження BPF програми у ядро: %d\n", err);
        bpf_object__close(obj);
        return 1;
    }

    map_fd = bpf_object__find_map_fd_by_name(obj, "events");
    if (map_fd < 0) {
        fprintf(stderr, "Не знайдено карту 'events'\n");
        bpf_object__close(obj);
        return 1;
    }

    /* Створення perf_buffer: 8 сторінок пам'яті (32 КБ) на кожен CPU */
    pb = perf_buffer__new(map_fd, 8, handle_event, handle_lost_events, NULL, NULL);
    if (libbpf_get_error(pb)) {
        fprintf(stderr, "Помилка створення perf_buffer\n");
        bpf_object__close(obj);
        return 1;
    }

    printf("Трасування викликів execve успішно запущено. Натисніть Ctrl+C для виходу.\n");

    while (keep_running) {
        err = perf_buffer__poll(pb, 100);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка опитування perf buffer: %d\n", err);
            break;
        }
    }

    printf("\nЗавершення роботи, очищення ресурсів...\n");
    perf_buffer__free(pb);
    bpf_object__close(obj);

    return 0;
}
