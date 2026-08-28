// C API (libbpf)
#include <stdio.h>
#include <stdlib.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

// 1. Callback обробника події для Perf Buffer
static void handle_perf_event(void *ctx, int cpu, void *data, __u32 size) {
    const char *msg = (const char *)data;
    printf("[Perfbuf CPU %d] Event size %u: %s\n", cpu, size, msg);
}

// 2. Callback обробника події для Ring Buffer (без CPU аргументу!)
static int handle_ring_event(void *ctx, void *data, size_t size) {
    const char *msg = (const char *)data;
    printf("[Ringbuf Total Order] Event size %zu: %s\n", size, msg);
    return 0; // Повертає 0 для продовження поллінгу
}

int setup_buffers(int perf_map_fd, int ring_map_fd) {
    // Налаштування Perf Buffer
    struct perf_buffer_opts pb_opts = {};
    pb_opts.sample_cb = handle_perf_event;
    struct perf_buffer *pb = perf_buffer__new(perf_map_fd, 8 /* pages per CPU */, &pb_opts);
    if (!pb) {
        fprintf(stderr, "Failed to create perf buffer\n");
        return -1;
    }

    // Налаштування Ring Buffer
    struct ring_buffer *rb = ring_buffer__new(ring_map_fd, handle_ring_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Failed to create ring buffer\n");
        perf_buffer__free(pb);
        return -1;
    }

    // Цикл поллінгу під час обробки подій
    int err = ring_buffer__poll(rb, 100 /* timeout_ms */);
    
    ring_buffer__free(rb);
    perf_buffer__free(pb);
    return err;
}
