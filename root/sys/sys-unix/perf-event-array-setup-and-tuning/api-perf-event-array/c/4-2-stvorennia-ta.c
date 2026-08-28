#include <stdio.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

void sample_handler(void *ctx, int cpu, void *data, __u32 size) {
    (void)ctx;
    printf("CPU %d: отримано %u байт\n", cpu, size);
}

void lost_handler(void *ctx, int cpu, __u64 lost_cnt) {
    (void)ctx;
    fprintf(stderr, "УВАГА: Втрачено %llu подій на CPU %d!\n", lost_cnt, cpu);
}

struct perf_buffer *init_buffer(int map_fd) {
    /* Створення буфера на 16 сторінок (64 КБ) на кожен CPU */
    struct perf_buffer *pb = perf_buffer__new(
        map_fd,
        16,
        sample_handler,
        lost_handler,
        NULL,
        NULL
    );

    if (libbpf_get_error(pb)) {
        return NULL;
    }
    return pb;
}

void poll_loop(struct perf_buffer *pb) {
    while (1) {
        int err = perf_buffer__poll(pb, 100 /* ms */);
        if (err < 0 && err != -EINTR) {
            break;
        }
    }
}
