#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define BUF_SIZE 8192

void stream_head(int fd_in, size_t max_lines) {
    char buffer[BUF_SIZE];
    size_t lines_count = 0;
    ssize_t bytes_read;

    while (lines_count < max_lines && (bytes_read = read(fd_in, buffer, sizeof(buffer))) > 0) {
        char *start = buffer;
        char *end = buffer + bytes_read;
        char *nl;

        while (lines_count < max_lines && (nl = memchr(start, '\n', end - start)) != NULL) {
            lines_count++;
            size_t chunk_len = (nl - start) + 1;
            if (write(STDOUT_FILENO, start, chunk_len) < 0) {
                return;
            }
            start = nl + 1;
        }

        if (lines_count < max_lines && start < end) {
            size_t remaining = end - start;
            if (write(STDOUT_FILENO, start, remaining) < 0) {
                return;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    size_t lines = (argc > 1) ? strtoul(argv[1], NULL, 10) : 10;
    stream_head(STDIN_FILENO, lines);
    return 0;
}
