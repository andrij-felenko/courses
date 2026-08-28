#include <sys/resource.h>
#include <stdio.h>

void print_peak_memory_usage(void) {
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        /* ru_maxrss returns memory in kilobytes on Linux */
        printf("Peak Resident Set Size (RSS): %ld KB\n", usage.ru_maxrss);
    }
}
