// C Implementation (libbpf)
#include <stdio.h>
#include <bpf/libbpf.h>

static int handle_ringbuf_event(void *ctx, void *data, size_t size) {
    const char *msg = (const char *)data;
    printf("Отримано подію в хронологічному порядку: %s\n", msg);
    return 0;
}

int run_c_consumer(int map_fd) {
    struct ring_buffer *rb = ring_buffer__new(map_fd, handle_ringbuf_event, NULL, NULL);
    if (!rb) return -1;

    while (1) {
        // Поллінг подій з адаптивним спинням
        int err = ring_buffer__poll(rb, 100 /* ms */);
        if (err < 0) break;
    }

    ring_buffer__free(rb);
    return 0;
}
