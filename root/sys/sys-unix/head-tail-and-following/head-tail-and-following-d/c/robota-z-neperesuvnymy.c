#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#define CHUNK_SIZE 4096

int tail_file_by_seek(const char *filepath, size_t target_lines) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("open");
        return -1;
    }

    off_t file_size = lseek(fd, 0, SEEK_END);
    if (file_size == (off_t)-1) {
        perror("lseek SEEK_END");
        close(fd);
        return -1;
    }

    if (file_size == 0) {
        close(fd);
        return 0;
    }

    off_t pos = file_size;
    size_t lines_found = 0;
    char buffer[CHUNK_SIZE];
    off_t print_start_pos = 0;

    while (pos > 0 && lines_found <= target_lines) {
        size_t bytes_to_read = (pos >= CHUNK_SIZE) ? CHUNK_SIZE : pos;
        pos -= bytes_to_read;

        if (lseek(fd, pos, SEEK_SET) == (off_t)-1) {
            perror("lseek SEEK_SET");
            close(fd);
            return -1;
        }

        ssize_t n_read = read(fd, buffer, bytes_to_read);
        if (n_read <= 0) {
            break;
        }

        // Скануємо зчитаний блок з кінця до початку
        for (ssize_t i = n_read - 1; i >= 0; --i) {
            // Ігноруємо '\n' на самому кінці файлу
            if (pos + i == file_size - 1 && buffer[i] == '\n') {
                continue;
            }

            if (buffer[i] == '\n') {
                lines_found++;
                if (lines_found == target_lines) {
                    print_start_pos = pos + i + 1;
                    goto output_tail;
                }
            }
        }
    }

output_tail:
    if (lseek(fd, print_start_pos, SEEK_SET) == (off_t)-1) {
        perror("lseek to print_start_pos");
        close(fd);
        return -1;
    }

    ssize_t bytes_in;
    while ((bytes_in = read(fd, buffer, sizeof(buffer))) > 0) {
        if (write(STDOUT_FILENO, buffer, bytes_in) < 0) {
            break;
        }
    }

    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файлу> [кількість_рядків]\n", argv[0]);
        return 1;
    }
    size_t lines = (argc > 2) ? strtoul(argv[2], NULL, 10) : 10;
    return tail_file_by_seek(argv[1], lines);
}
