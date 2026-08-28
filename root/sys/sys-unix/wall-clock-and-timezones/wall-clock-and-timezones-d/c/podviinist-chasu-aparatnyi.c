#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <time.h>
#include <stdlib.h>

static void print_clock(clockid_t clk_id, const char *name) {
    struct timespec ts;
    if (clock_gettime(clk_id, &ts) == 0) {
        printf("%-20s: %ld.%09ld с\n", name, (long)ts.tv_sec, ts.tv_nsec);
    } else {
        perror(name);
    }
}

int main(void) {
    print_clock(CLOCK_REALTIME, "CLOCK_REALTIME");
    print_clock(CLOCK_MONOTONIC, "CLOCK_MONOTONIC");
    print_clock(CLOCK_BOOTTIME, "CLOCK_BOOTTIME");
    print_clock(CLOCK_TAI, "CLOCK_TAI");
    return 0;
}
