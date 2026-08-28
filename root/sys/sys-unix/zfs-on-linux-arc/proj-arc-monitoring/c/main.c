#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ARCSTATS_PATH "/proc/spl/kstat/zfs/arcstats"
#define BUFFER_SIZE 256

typedef struct {
    unsigned long long hits;
    unsigned long long misses;
    unsigned long long mru_hits;
    unsigned long long mfu_hits;
    unsigned long long size;
    unsigned long long c;
    unsigned long long p;
    unsigned long long arc_meta_used;
} arc_stats_t;

int read_arcstats(arc_stats_t *stats) {
    FILE *fp = fopen(ARCSTATS_PATH, "r");
    if (!fp) {
        perror("Не вдалося відкрити " ARCSTATS_PATH);
        return -1;
    }

    char line[BUFFER_SIZE];
    char key[64];
    unsigned long long value;
    int type;

    memset(stats, 0, sizeof(arc_stats_t));

    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "%63s %d %llu", key, &type, &value) == 3) {
            if (strcmp(key, "hits") == 0) stats->hits = value;
            else if (strcmp(key, "misses") == 0) stats->misses = value;
            else if (strcmp(key, "mru_hits") == 0) stats->mru_hits = value;
            else if (strcmp(key, "mfu_hits") == 0) stats->mfu_hits = value;
            else if (strcmp(key, "size") == 0) stats->size = value;
            else if (strcmp(key, "c") == 0) stats->c = value;
            else if (strcmp(key, "p") == 0) stats->p = value;
            else if (strcmp(key, "arc_meta_used") == 0) stats->arc_meta_used = value;
        }
    }

    fclose(fp);
    return 0;
}

void print_report(const arc_stats_t *stats) {
    unsigned long long total_accesses = stats->hits + stats->misses;
    double hit_ratio = total_accesses > 0 ? ((double)stats->hits * 100.0) / total_accesses : 0.0;
    double mru_pct = stats->hits > 0 ? ((double)stats->mru_hits * 100.0) / stats->hits : 0.0;
    double mfu_pct = stats->hits > 0 ? ((double)stats->mfu_hits * 100.0) / stats->hits : 0.0;

    double size_mb = (double)stats->size / (1024.0 * 1024.0);
    double c_mb = (double)stats->c / (1024.0 * 1024.0);
    double p_mb = (double)stats->p / (1024.0 * 1024.0);
    double meta_mb = (double)stats->arc_meta_used / (1024.0 * 1024.0);

    printf("================ ZFS ARC Diagnostics (C) ================\n");
    printf("Поточний розмір ARC (size) : %8.2f МБ\n", size_mb);
    printf("Цільовий розмір кешу (c)   : %8.2f МБ\n", c_mb);
    printf("Вага Recency MRU (p)       : %8.2f МБ\n", p_mb);
    printf("Пам'ять під метадані       : %8.2f МБ\n", meta_mb);
    printf("---------------------------------------------------------\n");
    printf("Загальний Hit Ratio        : %8.2f %%\n", hit_ratio);
    printf("Частка MRU Hits            : %8.2f %%\n", mru_pct);
    printf("Частка MFU Hits            : %8.2f %%\n", mfu_pct);
    printf("=========================================================\n");
}

int main(void) {
    arc_stats_t stats;
    if (read_arcstats(&stats) != 0) {
        return EXIT_FAILURE;
    }
    print_report(&stats);
    return EXIT_SUCCESS;
}
