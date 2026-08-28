#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

static volatile sig_atomic_t stop_requested = 0;

static void sig_handler(int sig)
{
    (void)sig;
    stop_requested = 1;
}

struct event_t {
    unsigned int pid;
    unsigned int tgid;
    unsigned long long duration_ns;
    int ret_code;
    char comm[16];
};

static int handle_event(void *ctx, void *data, size_t data_sz)
{
    (void)ctx;
    (void)data_sz;
    const struct event_t *e = (const struct event_t *)data;

    printf("[TGID %5u] %-16s | openat FD: %3d | Затримка: %6.2f мкс\n",
           e->tgid, e->comm, e->ret_code, (double)e->duration_ns / 1000.0);
    return 0;
}

int main(void)
{
    struct bpf_object *obj = NULL;
    struct ring_buffer *rb = NULL;
    int err = 0;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* 1. Відкриття та завантаження скомпільованого BPF ELF */
    obj = bpf_object__open_file("openat_tracker.bpf.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка відкриття об'єкта BPF\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка завантаження програми верифікатором ядра: %d\n", err);
        bpf_object__close(obj);
        return 1;
    }

    /* 2. Прикріплення обробників зондів */
    struct bpf_program *prog_kprobe = bpf_object__find_program_by_name(obj, "trace_openat_enter");
    struct bpf_program *prog_kretprobe = bpf_object__find_program_by_name(obj, "trace_openat_exit");

    struct bpf_link *link_enter = bpf_program__attach(prog_kprobe);
    struct bpf_link *link_exit = bpf_program__attach(prog_kretprobe);

    if (!link_enter || !link_exit) {
        fprintf(stderr, "Помилка прикріплення kprobes\n");
        goto cleanup;
    }

    /* 3. Ініціалізація Ring Buffer */
    int events_map_fd = bpf_object__find_map_fd_by_name(obj, "events");
    rb = ring_buffer__new(events_map_fd, handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення обробника Ring Buffer\n");
        goto cleanup;
    }

    printf("Трасування openat запущено. Натисніть Ctrl+C для виходу...\n");

    /* 4. Головний цикл опитування */
    while (!stop_requested) {
        err = ring_buffer__poll(rb, 100 /* таймаут 100 мс */);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка опитування буфера: %d\n", err);
            break;
        }
    }

cleanup:
    if (rb) ring_buffer__free(rb);
    if (link_enter) bpf_link__destroy(link_enter);
    if (link_exit) bpf_link__destroy(link_exit);
    if (obj) bpf_object__close(obj);
    return 0;
}
