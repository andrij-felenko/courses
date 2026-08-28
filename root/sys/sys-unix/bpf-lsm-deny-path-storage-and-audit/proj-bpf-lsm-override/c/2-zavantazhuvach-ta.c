// C (libbpf Native C Implementation)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct audit_event {
    uint32_t pid;
    uint32_t ppid;
    uint32_t uid;
    uint32_t action;
    char comm[16];
    char filename[256];
};

static volatile bool keep_running = true;

static void sig_handler(int sig)
{
    (void)sig;
    keep_running = false;
}

static int handle_event(void *ctx, void *data, size_t data_sz)
{
    (void)ctx;
    (void)data_sz;
    const struct audit_event *e = data;

    if (e->action == 1) {
        printf("[BLOCKED] PID: %u | UID: %u | COMM: %s | PATH: %s\n",
               e->pid, e->uid, e->comm, e->filename);
    } else {
        printf("[ALLOW]   PID: %u | UID: %u | COMM: %s | PATH: %s\n",
               e->pid, e->uid, e->comm, e->filename);
    }
    return 0;
}

int main(int argc, char **argv)
{
    struct bpf_object *obj = NULL;
    struct bpf_link *link = NULL;
    struct ring_buffer *rb = NULL;
    int err;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    obj = bpf_object__open_file("bpf_lsm_exec.bpf.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка відкриття BPF-об'єкта\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка завантаження BPF у ядро: %d\n", err);
        bpf_object__close(obj);
        return 1;
    }

    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "restrict_exec");
    if (!prog) {
        fprintf(stderr, "Не знайдено програму restrict_exec\n");
        bpf_object__close(obj);
        return 1;
    }

    link = bpf_program__attach(prog);
    if (!link) {
        fprintf(stderr, "Помилка прив'язки LSM-хука\n");
        bpf_object__close(obj);
        return 1;
    }

    int map_fd = bpf_object__find_map_fd_by_name(obj, "audit_ringbuf");
    if (map_fd < 0) {
        fprintf(stderr, "Не знайдено BPF map audit_ringbuf\n");
        bpf_link__destroy(link);
        bpf_object__close(obj);
        return 1;
    }

    rb = ring_buffer__new(map_fd, handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення ring buffer\n");
        bpf_link__destroy(link);
        bpf_object__close(obj);
        return 1;
    }

    printf("BPF LSM модуль успішно активовано. Очікування подій...\n");

    while (keep_running) {
        err = ring_buffer__poll(rb, 100);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка при опитуванні ring buffer: %d\n", err);
            break;
        }
    }

    ring_buffer__free(rb);
    bpf_link__destroy(link);
    bpf_object__close(obj);
    printf("Модуль BPF LSM вивантажено.\n");
    return 0;
}
