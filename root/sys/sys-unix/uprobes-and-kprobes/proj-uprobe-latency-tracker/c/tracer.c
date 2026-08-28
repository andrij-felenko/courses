/* tracer.c - Завантажувач трасування мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "uprobe_tracer.skel.h"

static volatile bool exiting = false;

static void sig_handler(int sig) {
    exiting = true;
}

static int handle_event(void *ctx, void *data, size_t size) {
    const struct event *e = data;
    printf("PID %d | Виконання compute_hash: %llu мкс (%.2f мс)\n",
           e->pid, e->duration_ns / 1000, (double)e->duration_ns / 1000000.0);
    return 0;
}

int main(int argc, char **argv) {
    struct uprobe_tracer_bpf *skel;
    struct ring_buffer *rb = NULL;
    int err;

    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_target_app>\n", argv[0]);
        return 1;
    }
    const char *binary_path = argv[1];

    signal(SIGINT, sig_handler);

    skel = uprobe_tracer_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка відкриття BPF скелета\n");
        return 1;
    }

    /* Автоматичне прикріплення uprobe за іменем символу та шляхом до бінарника */
    skel->links.trace_entry = bpf_program__attach_uprobe(
        skel->progs.trace_entry, false, -1, binary_path, 0);
    skel->links.trace_exit = bpf_program__attach_uprobe(
        skel->progs.trace_exit, true, -1, binary_path, 0);

    rb = ring_buffer__new(bpf_map__fd(skel->maps.ringbuf), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення Ring Buffer\n");
        uprobe_tracer_bpf__destroy(skel);
        return 1;
    }

    printf("Трасування затримки активовано для %s. Натисніть Ctrl+C для виходу.\n", binary_path);

    while (!exiting) {
        err = ring_buffer__poll(rb, 100);
        if (err < 0 && err != -EINTR) {
            break;
        }
    }

    ring_buffer__free(rb);
    uprobe_tracer_bpf__destroy(skel);
    return 0;
}
