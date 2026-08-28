/* C11 procfs memory reader for Logspace Verification */
#include <stdio.h>
#include <stdint.h>

typedef struct {
    uint64_t total_pages;
    uint64_t resident_pages;
    uint64_t shared_pages;
} StatmMemoryInfo;

bool read_proc_statm(StatmMemoryInfo *info) {
    FILE *f = fopen("/proc/self/statm", "r");
    if (!f) return false;

    if (fscanf(f, "%lu %lu %lu", &info->total_pages, &info->resident_pages, &info->shared_pages) != 3) {
        fclose(f);
        return false;
    }

    fclose(f);
    return true;
}
