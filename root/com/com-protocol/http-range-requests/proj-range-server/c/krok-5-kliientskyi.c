#include <unistd.h>
#include <stdint.h>
#include <stdio.h>

/* Запис отриманого чанка потоком без блокування курсору файлу */
ssize_t write_segment_chunk(int local_file_fd, const void *buffer, size_t count, uint64_t file_offset) {
    off_t pos = (off_t)file_offset;
    const char *ptr = (const char *)buffer;
    size_t remaining = count;

    while (remaining > 0) {
        ssize_t written = pwrite(local_file_fd, ptr, remaining, pos);
        if (written <= 0) {
            return -1;
        }
        remaining -= (size_t)written;
        pos += (off_t)written;
        ptr += written;
    }
    return (ssize_t)count;
}
