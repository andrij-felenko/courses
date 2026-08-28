#include <stdio.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

/* Callback, який викликається при отриманні кожної події */
void handle_event(void *ctx, int cpu, void *data, __u32 data_sz)
{
    struct my_event_t *e = data;
    printf("CPU %d: PID %d, Comm: %s, Time: %llu\n", 
           cpu, e->pid, e->comm, e->timestamp);
}

/* Callback для обробки втрачених подій (dropped events) */
void handle_lost_events(void *ctx, int cpu, __u64 lost_cnt)
{
    fprintf(stderr, "Попередження: Втрачено %llu подій на CPU %d\n", lost_cnt, cpu);
}

int main(int argc, char **argv)
{
    struct bpf_object *obj;
    struct perf_buffer *pb = NULL;
    int map_fd, err;

    /* ... Завантаження об'єкта bpf (bpf_object__open, bpf_object__load) ... */
    
    map_fd = bpf_object__find_map_fd_by_name(obj, "my_perf_map");

    /* Налаштування perf buffer через libbpf */
    pb = perf_buffer__new(map_fd, 8, /* 8 сторінок пам'яті на кожен CPU буфер */
                          handle_event, handle_lost_events, NULL, NULL);
    if (libbpf_get_error(pb)) {
        fprintf(stderr, "Помилка ініціалізації perf buffer\n");
        return 1;
    }

    printf("Початок трасування... Натисніть Ctrl-C для зупинки.\n");

    /* Безкінечний цикл читання подій */
    while (1) {
        err = perf_buffer__poll(pb, 100 /* таймаут у мілісекундах */);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка опитування perf buffer: %d\n", err);
            break;
        }
    }

    perf_buffer__free(pb);
    /* ... Звільнення ресурсів ... */
    return 0;
}
