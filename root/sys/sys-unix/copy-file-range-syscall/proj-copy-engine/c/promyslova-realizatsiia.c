#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

#ifndef FICLONE
#define FICLONE _IOW(0x94, 9, int)
#endif

/* Розмір буфера користувача для крайнього фолбеку */
#define FALLBACK_BUF_SIZE (64 * 1024)

/* Резервний цикл копіювання через read / write */
static ssize_t copy_fallback_read_write(int fd_in, int fd_out, size_t count) {
    char buf[FALLBACK_BUF_SIZE];
    size_t total_copied = 0;

    while (total_copied < count) {
        size_t to_read = count - total_copied;
        if (to_read > sizeof(buf)) {
            to_read = sizeof(buf);
        }

        ssize_t nread = read(fd_in, buf, to_read);
        if (nread < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (nread == 0) break; /* Досягнуто EOF */

        size_t written = 0;
        while (written < (size_t)nread) {
            ssize_t nwritten = write(fd_out, buf + written, nread - written);
            if (nwritten < 0) {
                if (errno == EINTR) continue;
                return -1;
            }
            written += (size_t)nwritten;
        }
        total_copied += (size_t)nread;
    }
    return (ssize_t)total_copied;
}

/* Головна функція каскадного копіювання */
ssize_t robust_copy_file(int fd_in, int fd_out, size_t count) {
    size_t total_copied = 0;
    bool use_copy_file_range = true;

    /* Підказка ядру про послідовний характер зчитування */
    posix_fadvise(fd_in, 0, count, POSIX_FADV_SEQUENTIAL);

    /* Перевіряємо можливість CoW клонування через FICLONE (якщо копіюється весь файл) */
    if (count == 0) {
        struct stat st;
        if (fstat(fd_in, &st) == 0 && S_ISREG(st.st_mode)) {
            if (ioctl(fd_out, FICLONE, fd_in) == 0) {
                return st.st_size;
            }
            /* Клон не вдався — копіюємо весь файл звичайним шляхом */
            count = (size_t)st.st_size;
        }
        if (count == 0) {
            return 0; /* Порожній файл або невідомий розмір */
        }
    }

    while (total_copied < count) {
        size_t chunk = count - total_copied;

        if (use_copy_file_range) {
            ssize_t ret = copy_file_range(fd_in, NULL, fd_out, NULL, chunk, 0);

            if (ret > 0) {
                total_copied += (size_t)ret;
                continue;
            }

            if (ret == 0) {
                /* Досягнуто кінця вихідного файлу */
                break;
            }

            /* Обробка системних переривань сигналами */
            if (errno == EINTR) {
                continue;
            }

            const int err = errno;
            struct stat si, so;
            const bool same_inode = fstat(fd_in, &si) == 0 && fstat(fd_out, &so) == 0 &&
                                    si.st_dev == so.st_dev && si.st_ino == so.st_ino;

            /* EINVAL на СПІЛЬНОМУ іноді означає перекриття діапазонів: відкат на
               read/write тут переписав би дані, які ще належить зчитати */
            if (err == EXDEV || err == ENOSYS || err == EOPNOTSUPP ||
                (err == EINVAL && !same_inode)) {
                /* Ядро або ФС не підтримує copy_file_range між цими дескрипторами */
                use_copy_file_range = false;
                /* Переходимо до читання/запису для залишку даних */
                ssize_t fb_ret = copy_fallback_read_write(fd_in, fd_out, count - total_copied);
                if (fb_ret < 0) return -1;
                total_copied += (size_t)fb_ret;
                break;
            }

            /* Інші фатальні помилки (EIO, ENOSPC тощо) */
            return -1;
        }
    }

    return (ssize_t)total_copied;
}
