#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_RANGES 16

typedef struct {
    uint64_t start;
    uint64_t end;
} ByteRange;

typedef struct {
    ByteRange ranges[MAX_RANGES];
    size_t count;
    bool unsatisfiable;
} RangeResult;

/* Функція порівняння для швидкого сортування за початковим зміщенням */
static int compare_ranges(const void *a, const void *b) {
    const ByteRange *ra = (const ByteRange *)a;
    const ByteRange *rb = (const ByteRange *)b;
    if (ra->start < rb->start) return -1;
    if (ra->start > rb->start) return 1;
    return 0;
}

/* Коалесценція: злиття перекритих та суміжних інтервалів */
static void coalesce_ranges(RangeResult *res) {
    if (res->count <= 1) return;

    qsort(res->ranges, res->count, sizeof(ByteRange), compare_ranges);

    size_t write_idx = 0;
    for (size_t i = 1; i < res->count; ++i) {
        if (res->ranges[i].start <= res->ranges[write_idx].end + 1) {
            if (res->ranges[i].end > res->ranges[write_idx].end) {
                res->ranges[write_idx].end = res->ranges[i].end;
            }
        } else {
            write_idx++;
            res->ranges[write_idx] = res->ranges[i];
        }
    }
    res->count = write_idx + 1;
}

/* Розбір вхідного рядка заголовка Range */
RangeResult parse_range_header(const char *header, uint64_t file_size) {
    RangeResult res = { .count = 0, .unsatisfiable = false };
    if (!header || file_size == 0) {
        res.unsatisfiable = true;
        return res;
    }

    while (isspace((unsigned char)*header)) header++;
    if (strncmp(header, "bytes=", 6) != 0) {
        return res; /* Невідома одиниця виміру: повертаємо порожній результат */
    }
    header += 6;

    char buf[512];
    strncpy(buf, header, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';

    char *token = strtok(buf, ",");
    while (token && res.count < MAX_RANGES) {
        while (isspace((unsigned char)*token)) token++;
        char *dash = strchr(token, '-');
        if (!dash) {
            token = strtok(NULL, ",");
            continue;
        }

        *dash = '\0';
        char *start_str = token;
        char *end_str = dash + 1;

        if (start_str == dash) {
            /* Суфіксний запит: -suffix */
            char *end_ptr;
            uint64_t suffix = strtoull(end_str, &end_ptr, 10);
            if (end_ptr != end_str && suffix > 0) {
                uint64_t start = (suffix >= file_size) ? 0 : (file_size - suffix);
                res.ranges[res.count++] = (ByteRange){ start, file_size - 1 };
            }
        } else if (*end_str == '\0' || isspace((unsigned char)*end_str)) {
            /* Напіввідкритий інтервал: start- */
            char *end_ptr;
            uint64_t start = strtoull(start_str, &end_ptr, 10);
            if (end_ptr != start_str) {
                if (start < file_size) {
                    res.ranges[res.count++] = (ByteRange){ start, file_size - 1 };
                } else {
                    res.unsatisfiable = true;
                }
            }
        } else {
            /* Замкнений інтервал: start-end */
            char *end_ptr1, *end_ptr2;
            uint64_t start = strtoull(start_str, &end_ptr1, 10);
            uint64_t end = strtoull(end_str, &end_ptr2, 10);
            if (end_ptr1 != start_str && end_ptr2 != end_str && start <= end) {
                if (start < file_size) {
                    if (end >= file_size) end = file_size - 1;
                    res.ranges[res.count++] = (ByteRange){ start, end };
                } else {
                    res.unsatisfiable = true;
                }
            }
        }
        token = strtok(NULL, ",");
    }

    if (res.count > 0) {
        res.unsatisfiable = false;
        coalesce_ranges(&res);
    }
    return res;
}
