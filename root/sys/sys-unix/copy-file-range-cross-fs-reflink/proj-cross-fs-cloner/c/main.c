#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/fs.h>

#ifndef FICLONE
#define FICLONE _IOW(0x94, 9, int)
#endif

#define BUFFER_SIZE (256 * 1024)

// Базовий каскадний клонер мовою C
ssize_t robust_copy_file_range(int fd_in, loff_t *off_in,
                               int fd_out, loff_t *off_out,
                               size_t len)
{
    // Крок 1: Спроба FICLONE (Reflink), якщо зміщення дорівнюють 0 і copy від початку
    if ((off_in == NULL || *off_in == 0) &&
        (off_out == NULL || *off_out == 0) && len == 0) {
        if (ioctl(fd_out, FICLONE, fd_in) == 0) {
            // Склоновано весь файл; повертаємо його розмір, бо 0 означає EOF
            struct stat st;
            if (fstat(fd_in, &st) != 0) return -1;
            return (ssize_t)st.st_size;
        }
        // Якщо повернуто EXDEV, EOPNOTSUPP або ENOTTY — каскадно переходимо нижче
        if (errno != EXDEV && errno != EOPNOTSUPP && errno != ENOTTY && errno != EINVAL) {
            return -1; // Критична помилка доступу або файлової системи
        }
    }

    // Крок 2: Спроба системного виклику copy_file_range(2)
    size_t total_copied = 0;
    size_t bytes_remaining = len;

    while (bytes_remaining > 0 || len == 0) {
        size_t chunk = (len == 0) ? (1024 * 1024 * 1024) : bytes_remaining;
        ssize_t ret = copy_file_range(fd_in, off_in, fd_out, off_out, chunk, 0);

        if (ret > 0) {
            total_copied += (size_t)ret;
            if (len > 0) {
                bytes_remaining -= (size_t)ret;
            }
            continue;
        }

        if (ret == 0) {
            // Досягнуто EOF джерела
            break;
        }

        // Аналіз помилок copy_file_range
        if (errno == EINTR) {
            continue; // Переривання сигналом — повторюємо спробу
        }

        if (errno == EXDEV || errno == EOPNOTSUPP || errno == ENOSYS || errno == EINVAL) {
            // copy_file_range не підтримується ядром/ФС або виявлено крос-протокольне обмеження
            // Переходимо до Кроку 3: splice fallback
            break;
        }

        // Непереборна помилка (наприклад, ENOSPC або EIO)
        return -1;
    }

    if (total_copied > 0 || (len > 0 && bytes_remaining == 0)) {
        return (ssize_t)total_copied;
    }

    // Крок 3: Zero-Copy Splice Fallback через анонімний pipe
    int pipefd[2];
    if (pipe2(pipefd, O_CLOEXEC | O_NONBLOCK) == 0) {
        // Опціональне збільшення розміру pipe до 1 МБ
        fcntl(pipefd[1], F_SETPIPE_SZ, 1024 * 1024);

        while (bytes_remaining > 0 || len == 0) {
            size_t chunk = (len == 0 || bytes_remaining > BUFFER_SIZE) ? BUFFER_SIZE : bytes_remaining;
            ssize_t s_in = splice(fd_in, off_in, pipefd[1], NULL, chunk, SPLICE_F_MOVE | SPLICE_F_MORE);

            if (s_in > 0) {
                ssize_t s_out = splice(pipefd[0], NULL, fd_out, off_out, (size_t)s_in, SPLICE_F_MOVE);
                if (s_out > 0) {
                    total_copied += (size_t)s_out;
                    if (len > 0) {
                        bytes_remaining -= (size_t)s_out;
                    }
                    continue;
                }
            }

            if (s_in == 0) break; // EOF

            if (errno == EINTR) continue;

            // Сплайс не підтримується для даного типу файлів (наприклад, O_DIRECT)
            break;
        }
        close(pipefd[0]);
        close(pipefd[1]);
    }

    if (total_copied > 0 || (len > 0 && bytes_remaining == 0)) {
        return (ssize_t)total_copied;
    }

    // Крок 4: Традиційний User Space буферизований цикл (POSIX fallback)
    char *buf = malloc(BUFFER_SIZE);
    if (!buf) return -1;

    // Рекомендація ядру про послідовний доступ
    posix_fadvise(fd_in, (off_in ? *off_in : 0), bytes_remaining, POSIX_FADV_SEQUENTIAL);

    while (bytes_remaining > 0 || len == 0) {
        size_t chunk = (len == 0 || bytes_remaining > BUFFER_SIZE) ? BUFFER_SIZE : bytes_remaining;
        ssize_t r_bytes = (off_in != NULL) ? pread(fd_in, buf, chunk, *off_in) : read(fd_in, buf, chunk);

        if (r_bytes > 0) {
            if (off_in != NULL) *off_in += r_bytes;

            ssize_t w_bytes = (off_out != NULL) ? pwrite(fd_out, buf, (size_t)r_bytes, *off_out) : write(fd_out, buf, (size_t)r_bytes);
            if (w_bytes > 0) {
                if (off_out != NULL) *off_out += w_bytes;
                total_copied += (size_t)w_bytes;
                if (len > 0) bytes_remaining -= (size_t)w_bytes;
                continue;
            }
        }

        if (r_bytes == 0) break; // EOF

        if (errno == EINTR) continue;

        free(buf);
        return -1;
    }

    free(buf);
    return (ssize_t)total_copied;
}
