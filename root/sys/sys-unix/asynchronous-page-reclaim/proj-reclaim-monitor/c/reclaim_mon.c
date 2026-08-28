/* reclaim_mon.c — C99/C11 монітор системного витіснення сторінок */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

typedef struct {
    unsigned long long pgscan_kswapd;
    unsigned long long pgscan_direct;
    unsigned long long pgsteal_kswapd;
    unsigned long long pgsteal_direct;
    unsigned long long allocstall;
    unsigned long long pageoutrun;
} vmstat_metrics_t;

static int read_vmstat(vmstat_metrics_t *m) {
    FILE *fp = fopen("/proc/vmstat", "r");
    if (!fp) {
        perror("Не вдалося відкрити /proc/vmstat");
        return -1;
    }

    memset(m, 0, sizeof(*m));
    char line[256];
    
    while (fgets(line, sizeof(line), fp)) {
        char key[64];
        unsigned long long val;
        if (sscanf(line, "%63s %llu", key, &val) == 2) {
            if (strcmp(key, "pgscan_kswapd") == 0)      m->pgscan_kswapd = val;
            else if (strcmp(key, "pgscan_direct") == 0)  m->pgscan_direct = val;
            else if (strcmp(key, "pgsteal_kswapd") == 0) m->pgsteal_kswapd = val;
            else if (strcmp(key, "pgsteal_direct") == 0) m->pgsteal_direct = val;
            /* від ядра 4.9 лічильник розбито по зонах: allocstall_dma, allocstall_normal, … */
            else if (strncmp(key, "allocstall", 10) == 0) m->allocstall += val;
            else if (strcmp(key, "pageoutrun") == 0)     m->pageoutrun = val;
        }
    }

    fclose(fp);
    return 0;
}

int main(int argc, char *argv[]) {
    int interval_sec = 1;
    if (argc > 1) {
        interval_sec = atoi(argv[1]);
        if (interval_sec <= 0) interval_sec = 1;
    }

    printf("Starting Reclaim Monitor (interval: %d s)...\n", interval_sec);
    printf("%-10s | %-14s | %-14s | %-10s | %-10s\n", 
           "Time", "kswapd scan/s", "Direct scan/s", "Stalls/s", "kswapd Eff");
    printf("-------------------------------------------------------------------\n");

    vmstat_metrics_t prev, curr;
    if (read_vmstat(&prev) < 0) return 1;

    while (1) {
        sleep(interval_sec);
        if (read_vmstat(&curr) < 0) break;

        unsigned long long dk_scan  = curr.pgscan_kswapd - prev.pgscan_kswapd;
        unsigned long long dd_scan  = curr.pgscan_direct - prev.pgscan_direct;
        unsigned long long dk_steal = curr.pgsteal_kswapd - prev.pgsteal_kswapd;
        unsigned long long dstalls  = curr.allocstall - prev.allocstall;

        double k_eff = (dk_scan > 0) ? ((double)dk_steal / dk_scan * 100.0) : 100.0;
        
        time_t now = time(NULL);
        struct tm *t = localtime(&now);
        char time_str[16];
        strftime(time_str, sizeof(time_str), "%H:%M:%S", t);

        const char *alert = (dstalls > 0) ? " [STALL DETECTED!]" : "";

        printf("%-10s | %-14llu | %-14llu | %-10llu | %6.1f%%%s\n",
               time_str, dk_scan / interval_sec, dd_scan / interval_sec,
               dstalls / interval_sec, k_eff, alert);

        prev = curr;
    }

    return 0;
}
