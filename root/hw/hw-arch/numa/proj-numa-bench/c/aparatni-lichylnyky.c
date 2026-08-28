#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// Обгортка над системним викликом perf_event_open
static int open_hw_perf_counter(uint32_t type, uint64_t config) {
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = type;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = config;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0);
}

// Зчитування 64-бітного значення лічильника
static uint64_t read_perf_counter(int fd) {
    uint64_t val = 0;
    if (read(fd, &val, sizeof(uint64_t)) != sizeof(uint64_t)) {
        return 0;
    }
    return val;
}
