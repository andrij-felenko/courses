#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <stdatomic.h>
#include <linux/perf_event.h>

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                             int cpu, int group_fd, unsigned long flags) {
    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

int main(void) {
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = PERF_COUNT_HW_CPU_CYCLES;
    pe.sample_period = 100000; // Самплінг кожні 100 000 циклів CPU
    pe.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    int fd = (int)perf_event_open(&pe, 0, -1, -1, 0);
    if (fd == -1) {
        perror("perf_event_open failed");
        return EXIT_FAILURE;
    }

    // Виділяємо 1 сторінку управління + 8 сторінок даних (1 + 8 * 4096 байтів)
    const size_t page_size = (size_t)sysconf(_SC_PAGESIZE);
    const size_t data_pages = 8;
    const size_t mmap_size = page_size * (1 + data_pages);

    void *base = mmap(NULL, mmap_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (base == MAP_FAILED) {
        perror("mmap failed");
        close(fd);
        return EXIT_FAILURE;
    }

    struct perf_event_mmap_page *hdr = (struct perf_event_mmap_page *)base;
    char *data_boundary = (char *)base + page_size;
    size_t data_size = page_size * data_pages;

    // Вмикаємо лічильник
    ioctl(fd, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

    // Імітація обчислювального навантаження
    volatile unsigned long long dummy = 0;
    for (unsigned long long i = 0; i < 50000000ULL; ++i) {
        dummy += i;
    }

    // Вимикаємо моніторинг
    ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);

    // Зчитуємо записи з кільцевого буфера
    uint64_t head = atomic_load_explicit((_Atomic uint64_t *)&hdr->data_head, memory_order_acquire);
    uint64_t tail = hdr->data_tail;

    printf("Зчитано data_head = %lu, data_tail = %lu\n", head, tail);

    size_t samples_count = 0;
    while (tail < head) {
        uint64_t offset = tail % data_size;
        struct perf_event_header *phead = (struct perf_event_header *)(data_boundary + offset);

        if (phead->size == 0) {
            break; // Захист від пошкоджених даних
        }

        if (phead->type == PERF_RECORD_SAMPLE) {
            struct {
                uint64_t ip;
                uint32_t pid, tid;
                uint64_t time;
            } *sample = (void *)((char *)phead + sizeof(struct perf_event_header));

            samples_count++;
            if (samples_count <= 5) {
                printf("  [Вибірка #%zu] RIP = 0x%lx, PID = %u, TID = %u, Time = %lu ns\n",
                       samples_count, sample->ip, sample->pid, sample->tid, sample->time);
            }
        }

        tail += phead->size;
    }

    // Оновлюємо курсор tail для ядра
    atomic_store_explicit((_Atomic uint64_t *)&hdr->data_tail, tail, memory_order_release);
    printf("Усього вибірок оброблено: %zu\n", samples_count);

    munmap(base, mmap_size);
    close(fd);
    return EXIT_SUCCESS;
}
