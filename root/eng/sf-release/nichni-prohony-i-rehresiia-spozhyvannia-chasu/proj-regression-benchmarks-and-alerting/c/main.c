#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <malloc.h>
#include <time.h>

typedef struct {
    uint64_t timestamp_ms;
    size_t total_free_bytes;
    size_t max_contiguous_free_bytes;
    double fragmentation_index;
    uint32_t max_isr_latency_us;
} MemoryTelemetry;

/* Визначення найбільшого доступного неперервного блоку в купі методом бінарного зондування */
static size_t probe_max_contiguous_block(size_t upper_bound) {
    size_t low = 0;
    size_t high = upper_bound;
    size_t max_success = 0;

    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        if (mid == 0) {
            low = 1;
            continue;
        }

        void* ptr = malloc(mid);
        if (ptr != NULL) {
            max_success = mid;
            free(ptr);
            low = mid + 1; /* Пробуємо виділити більший блок */
        } else {
            if (mid == 0) break;
            high = mid - 1; /* Зменшуємо запит */
        }
    }
    return max_success;
}

MemoryTelemetry capture_heap_telemetry(uint32_t isr_latency_us) {
    MemoryTelemetry report;
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    report.timestamp_ms = (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;

    struct mallinfo2 info = mallinfo2();
    /* fordblks — загальний обсяг вільної пам'яті, що утримується алокатором */
    report.total_free_bytes = info.fordblks;

    /* Зондуємо найбільший блок у межах відомого вільного обсягу */
    report.max_contiguous_free_bytes = probe_max_contiguous_block(report.total_free_bytes);

    if (report.total_free_bytes > 0) {
        report.fragmentation_index = 1.0 - ((double)report.max_contiguous_free_bytes / (double)report.total_free_bytes);
    } else {
        report.fragmentation_index = 1.0;
    }

    report.max_isr_latency_us = isr_latency_us;
    return report;
}

void emit_telemetry_json(const MemoryTelemetry* rep) {
    printf("{\"type\":\"soak_telemetry\",\"ts\":%llu,\"free_bytes\":%zu,\"max_block\":%zu,\"frag_idx\":%.4f,\"max_latency_us\":%u}\n",
           (unsigned long long)rep->timestamp_ms,
           rep->total_free_bytes,
           rep->max_contiguous_free_bytes,
           rep->fragmentation_index,
           rep->max_isr_latency_us);
    fflush(stdout);
}
