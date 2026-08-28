// C Implementation using libbpf
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>

struct event_t {
    unsigned long long timestamp_ns;
    unsigned int pid;
    unsigned int cpu_id;
    char comm[16];
    char filename[256];
};

static volatile bool exiting = false;

static void sig_handler(int sig) {
    exiting = true;
}

static int handle_ring_event(void *ctx, void *data, size_t data_sz) {
    const struct event_t *e = data;
    printf("[%llu ns][CPU %u] PID %u (%s) opened: %s\n",
           e->timestamp_ns, e->cpu_id, e->pid, e->comm, e->filename);
    return 0;
}

int main(int argc, char **argv) {
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    int map_fd = 0; // Вказівник на fd карти ringbuf

    struct ring_buffer *rb = ring_buffer__new(map_fd, handle_ring_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка виділення ring_buffer\n");
        return 1;
    }

    printf("Розпочато трасування системних викликів. Натисніть Ctrl+C для виходу...\n");
    while (!exiting) {
        int err = ring_buffer__poll(rb, 100 /* ms */);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка поллінгу: %d\n", err);
            break;
        }
    }

    ring_buffer__free(rb);
    return 0;
}
