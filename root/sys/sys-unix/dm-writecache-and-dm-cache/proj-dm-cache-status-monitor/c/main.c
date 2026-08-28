#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

#define CMD_MAX 256
#define BUFFER_SIZE 2048

typedef struct {
    unsigned long long read_hits;
    unsigned long long read_misses;
    unsigned long long write_hits;
    unsigned long long write_misses;
    unsigned long long demotions;
    unsigned long long promotions;
    unsigned long long dirty_blocks;
    unsigned long long used_cache_blocks;
    unsigned long long total_cache_blocks;
    double hit_ratio;
} dm_cache_stats_t;

static int name_is_safe(const char *s) {
    if (*s == '\0') return 0;
    for (; *s; ++s) {
        if (!isalnum((unsigned char)*s) && *s != '-' && *s != '_' && *s != '.')
            return 0;
    }
    return 1;
}

static int read_dm_status(const char *dm_name, char *buffer, size_t buf_size) {
    char cmd[CMD_MAX];

    if (!name_is_safe(dm_name)) {
        fprintf(stderr, "Недопустиме ім'я пристрою: %s\n", dm_name);
        return -1;
    }
    snprintf(cmd, sizeof(cmd), "dmsetup status %s", dm_name);

    FILE *pipe = popen(cmd, "r");
    if (!pipe) {
        fprintf(stderr, "Не вдалося запустити dmsetup: %s\n", strerror(errno));
        return -1;
    }

    size_t bytes = fread(buffer, 1, buf_size - 1, pipe);
    int rc = pclose(pipe);

    if (bytes == 0 || rc != 0) {
        fprintf(stderr, "dmsetup status не повернув даних для %s\n", dm_name);
        return -1;
    }

    buffer[bytes] = '\0';
    return 0;
}

static int parse_dm_cache_status(const char *status_str, dm_cache_stats_t *stats) {
    long long start, length;
    char target_type[32];
    unsigned int meta_block_size;
    unsigned long long meta_used, meta_total;
    unsigned int chunk_size;

    int parsed = sscanf(status_str, "%lld %lld %31s %u %llu/%llu %u %llu/%llu %llu %llu %llu %llu %llu %llu %llu",
                       &start, &length, target_type,
                       &meta_block_size, &meta_used, &meta_total,
                       &chunk_size, &stats->used_cache_blocks, &stats->total_cache_blocks,
                       &stats->read_hits, &stats->read_misses,
                       &stats->write_hits, &stats->write_misses,
                       &stats->demotions, &stats->promotions, &stats->dirty_blocks);

    if (parsed < 16 || strcmp(target_type, "cache") != 0) {
        fprintf(stderr, "Рядок статусу не відповідає формату dm-cache або це інший target\n");
        return -1;
    }

    unsigned long long total_ops = stats->read_hits + stats->read_misses + stats->write_hits + stats->write_misses;
    if (total_ops > 0) {
        stats->hit_ratio = ((double)(stats->read_hits + stats->write_hits) / (double)total_ops) * 100.0;
    } else {
        stats->hit_ratio = 0.0;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <dm-пристрій> (наприклад, my_cached_dev)\n", argv[0]);
        return EXIT_FAILURE;
    }

    char buffer[BUFFER_SIZE];
    if (read_dm_status(argv[1], buffer, sizeof(buffer)) != 0) {
        return EXIT_FAILURE;
    }

    dm_cache_stats_t stats = {0};
    if (parse_dm_cache_status(buffer, &stats) != 0) {
        return EXIT_FAILURE;
    }

    printf("=== Телеметрія dm-cache для %s ===\n", argv[1]);
    double usage_pct = stats.total_cache_blocks
                     ? (double)stats.used_cache_blocks / (double)stats.total_cache_blocks * 100.0
                     : 0.0;
    printf("Кешовано блоків:   %llu / %llu (%.2f%%)\n",
           stats.used_cache_blocks, stats.total_cache_blocks, usage_pct);
    printf("Влучання (Hits):   Читання: %llu, Запис: %llu\n", stats.read_hits, stats.write_hits);
    printf("Промахи (Misses):  Читання: %llu, Запис: %llu\n", stats.read_misses, stats.write_misses);
    printf("Коефіцієнт Hit Ratio: %.2f%%\n", stats.hit_ratio);
    printf("Брудні блоки:      %llu\n", stats.dirty_blocks);
    printf("Міграція даних:    Promotions: %llu, Demotions: %llu\n", stats.promotions, stats.demotions);

    if (stats.hit_ratio < 50.0 && (stats.read_hits + stats.read_misses) > 10000) {
        printf("УВАГА: Низький Hit Ratio! Розмір кешу може бути замалим для робочого набору.\n");
    }

    return EXIT_SUCCESS;
}
