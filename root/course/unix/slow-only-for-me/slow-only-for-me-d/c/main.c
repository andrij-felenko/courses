#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

#define TOTAL_RECORDS 500000
#define RECORD_TEXT "METRIC:id=42,sensor=temp,val=23.75,status=OK\n"

/* Наївна функція: системний виклик write() на кожен окремий запис */
void write_unbuffered(const char *path) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open unbuffered");
        return;
    }

    const size_t len = strlen(RECORD_TEXT);
    for (size_t i = 0; i < TOTAL_RECORDS; ++i) {
        /* 500 000 переходів у простір ядра Ring 0 */
        if (write(fd, RECORD_TEXT, len) != (ssize_t)len) {
            perror("write error");
            break;
        }
    }
    close(fd);
}

/* Оптимізована функція: буферизація у пам'яті блоками по 64 КіБ */
void write_buffered(const char *path) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open buffered");
        return;
    }

    const size_t BUFFER_SIZE = 64 * 1024;
    char *buffer = (char *)malloc(BUFFER_SIZE);
    if (!buffer) {
        close(fd);
        return;
    }

    const size_t rec_len = strlen(RECORD_TEXT);
    size_t offset = 0;

    for (size_t i = 0; i < TOTAL_RECORDS; ++i) {
        if (offset + rec_len > BUFFER_SIZE) {
            /* Запис повного блоку одним системним викликом */
            if (write(fd, buffer, offset) != (ssize_t)offset) {
                perror("write buffer error");
                break;
            }
            offset = 0;
        }
        memcpy(buffer + offset, RECORD_TEXT, rec_len);
        offset += rec_len;
    }

    if (offset > 0) {
        if (write(fd, buffer, offset) != (ssize_t)offset) {
            perror("final flush error");
        }
    }

    free(buffer);
    close(fd);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s [unbuffered|buffered]\n", argv[0]);
        return 1;
    }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    if (strcmp(argv[1], "unbuffered") == 0) {
        write_unbuffered("/tmp/bench_unbuffered.log");
    } else {
        write_buffered("/tmp/bench_buffered.log");
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + 
                     (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("Режим %s завершено за %.4f секунд\n", argv[1], elapsed);
    return 0;
}
