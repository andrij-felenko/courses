#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>

int copy_file_data_c(const char* src_path, const char* dst_path) {
    int in_fd = -1;
    int out_fd = -1;
    char* buffer = NULL;
    int status = -1;

    in_fd = open(src_path, O_RDONLY);
    if (in_fd < 0) {
        goto cleanup;
    }

    out_fd = open(dst_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out_fd < 0) {
        goto cleanup;
    }

    buffer = (char*)malloc(4096);
    if (!buffer) {
        goto cleanup;
    }

    while (1) {
        ssize_t bytes_read = read(in_fd, buffer, 4096);
        if (bytes_read < 0) {
            goto cleanup;
        }
        if (bytes_read == 0) {
            break;
        }

        ssize_t bytes_written = write(out_fd, buffer, (size_t)bytes_read);
        if (bytes_written != bytes_read) {
            goto cleanup;
        }
    }

    status = 0; // Успіх

cleanup:
    // Ручне розмотування ресурсів у зворотному порядку
    if (buffer) {
        free(buffer);
    }
    if (out_fd >= 0) {
        close(out_fd);
    }
    if (in_fd >= 0) {
        close(in_fd);
    }
    return status;
}
