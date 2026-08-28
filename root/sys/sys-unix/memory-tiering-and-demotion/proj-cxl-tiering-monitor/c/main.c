#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <time.h>
#include <stdbool.h>

#define SYSFS_TIERS "/sys/devices/system/node/memory_tiers"
#define VMSTAT_PATH "/proc/vmstat"
#define PAGE_SIZE_KB 4

typedef struct {
    unsigned long pgdemote_kswapd;
    unsigned long pgdemote_direct;
    unsigned long pgpromote_success;
    unsigned long pgpromote_candidate;
    unsigned long numa_hint_faults;
} vmstat_tier_metrics_t;

static void discover_memory_tiers(void) {
    DIR *dir = opendir(SYSFS_TIERS);
    if (!dir) {
        printf("[WARN] Memory tiers sysfs directory not found: %s\n", SYSFS_TIERS);
        printf("[INFO] System may lack CXL/PMEM hardware or CONFIG_TIERED_MEMORY.\n\n");
        return;
    }

    printf("=== Виявлені яруси пам'яті (Memory Tiers) ===\n");
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, "memory_tier", 11) == 0) {
            char nodes_path[512];
            snprintf(nodes_path, sizeof(nodes_path), "%s/%s/nodelist", SYSFS_TIERS, entry->d_name);
            FILE *f = fopen(nodes_path, "r");
            char nodelist[128] = "unknown";
            if (f) {
                if (fgets(nodelist, sizeof(nodelist), f)) {
                    nodelist[strcspn(nodelist, "\r\n")] = 0;
                }
                fclose(f);
            }
            printf("  • %-14s -> NUMA-вузли: [%s]\n", entry->d_name, nodelist);
        }
    }
    closedir(dir);
    printf("\n");
}

static bool read_vmstat_metrics(vmstat_tier_metrics_t *out) {
    FILE *f = fopen(VMSTAT_PATH, "r");
    if (!f) return false;

    memset(out, 0, sizeof(*out));
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        char key[64];
        unsigned long val;
        if (sscanf(line, "%63s %lu", key, &val) == 2) {
            if (strcmp(key, "pgdemote_kswapd") == 0) out->pgdemote_kswapd = val;
            else if (strcmp(key, "pgdemote_direct") == 0) out->pgdemote_direct = val;
            else if (strcmp(key, "pgpromote_success") == 0) out->pgpromote_success = val;
            else if (strcmp(key, "pgpromote_candidate") == 0) out->pgpromote_candidate = val;
            else if (strcmp(key, "numa_hint_faults") == 0) out->numa_hint_faults = val;
        }
    }
    fclose(f);
    return true;
}

int main(int argc, char **argv) {
    int interval_sec = 1;
    if (argc > 1) {
        interval_sec = atoi(argv[1]);
        if (interval_sec < 1) interval_sec = 1;
    }

    discover_memory_tiers();

    vmstat_tier_metrics_t prev, curr;
    if (!read_vmstat_metrics(&prev)) {
        perror("Помилка читання /proc/vmstat");
        return 1;
    }

    printf("%-10s | %-16s | %-16s | %-16s | %-14s\n",
           "Час", "Demote kswapd", "Demote Direct", "Promote Success", "NUMA Hints");
    printf("-----------------------------------------------------------------------------------\n");

    while (1) {
        sleep((unsigned int)interval_sec);
        if (!read_vmstat_metrics(&curr)) break;

        time_t rawtime;
        time(&rawtime);
        struct tm *ti = localtime(&rawtime);
        char time_buf[16];
        strftime(time_buf, sizeof(time_buf), "%H:%M:%S", ti);

        double demote_kswapd_mbs = ((double)(curr.pgdemote_kswapd - prev.pgdemote_kswapd) * PAGE_SIZE_KB) / (1024.0 * interval_sec);
        double demote_direct_mbs = ((double)(curr.pgdemote_direct - prev.pgdemote_direct) * PAGE_SIZE_KB) / (1024.0 * interval_sec);
        double promote_mbs = ((double)(curr.pgpromote_success - prev.pgpromote_success) * PAGE_SIZE_KB) / (1024.0 * interval_sec);
        unsigned long hints_rate = (curr.numa_hint_faults - prev.numa_hint_faults) / (unsigned long)interval_sec;

        printf("%-10s | %10.2f MB/s | %10.2f MB/s | %10.2f MB/s | %10lu f/s\n",
               time_buf, demote_kswapd_mbs, demote_direct_mbs, promote_mbs, hints_rate);
        fflush(stdout);

        prev = curr;
    }

    return 0;
}
