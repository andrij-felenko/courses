#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t start;
    uint64_t end;
    bool is_valid;
} SingleByteRange;

SingleByteRange parse_single_range(const char *header, uint64_t file_size) {
    SingleByteRange range = {0, 0, false};
    if (!header || strncmp(header, "bytes=", 6) != 0 || file_size == 0) {
        return range;
    }
    const char *p = header + 6;
    char *dash = strchr(p, '-');
    if (!dash) return range;

    if (p == dash) {
        /* Формат -suffix: останні N байтів */
        char *end_ptr;
        uint64_t suffix = strtoull(dash + 1, &end_ptr, 10);
        if (end_ptr != dash + 1 && suffix > 0) {
            range.start = (suffix >= file_size) ? 0 : (file_size - suffix);
            range.end = file_size - 1;
            range.is_valid = true;
        }
    } else if (*(dash + 1) == '\0') {
        /* Формат start-: від start до кінця */
        char *end_ptr;
        uint64_t start = strtoull(p, &end_ptr, 10);
        if (end_ptr == dash && start < file_size) {
            range.start = start;
            range.end = file_size - 1;
            range.is_valid = true;
        }
    } else {
        /* Формат start-end */
        char *end_ptr1, *end_ptr2;
        uint64_t start = strtoull(p, &end_ptr1, 10);
        uint64_t end = strtoull(dash + 1, &end_ptr2, 10);
        if (end_ptr1 == dash && *end_ptr2 == '\0' && start <= end && start < file_size) {
            range.start = start;
            range.end = (end >= file_size) ? (file_size - 1) : end;
            range.is_valid = true;
        }
    }
    return range;
}
