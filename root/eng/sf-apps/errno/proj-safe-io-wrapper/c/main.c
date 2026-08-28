#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* Результат операції системного вводу-виводу */
typedef enum {
    IO_SUCCESS = 0,
    IO_EOF     = 1,
    IO_ERROR   = -1
} io_status_t;

/*
 * Потокобезпечне отримання опису помилки.
 * Підтримує як стандартну версію POSIX XSI strerror_r, так і GNU-специфічну.
 */
static void safe_strerror(int errnum, char *buf, size_t buflen) {
    if (buflen == 0) return;
    buf[0] = '\0';

#if defined(_GNU_SOURCE) && !defined(__APPLE__) && !defined(__FreeBSD__)
    /* GNU-версія: повертає char*, який може бути вказівником на статичний рядок */
    char *msg = strerror_r(errnum, buf, buflen);
    if (msg != buf) {
        strncpy(buf, msg, buflen - 1);
        buf[buflen - 1] = '\0';
    }
#else
    /* POSIX XSI-версія: повертає int (0 при успіху або код помилки) */
    if (strerror_r(errnum, buf, buflen) != 0) {
        snprintf(buf, buflen, "Unknown error %d", errnum);
    }
#endif
}

/*
 * Надійний повний запис буфера в дескриптор.
 * Гарантує передачу ВСІХ байтів count або повернення помилки.
 * Автоматично повторює спробу при перериванні сигналом (EINTR).
 */
io_status_t safe_write_all(int fd, const void *buf, size_t count,
                           size_t *bytes_written, int *out_errno) {
    const uint8_t *ptr = (const uint8_t *)buf;
    size_t total_written = 0;

    while (total_written < count) {
        ssize_t n = write(fd, ptr + total_written, count - total_written);
        if (n > 0) {
            total_written += (size_t)n;
            continue;
        }
        if (n == 0) {
            /* Запис 0 байтів при count > 0 свідчить про закриття каналу */
            if (bytes_written) *bytes_written = total_written;
            if (out_errno) *out_errno = EPIPE;
            return IO_ERROR;
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                /* Виклик перервано сигналом — повторюємо спробу негайно */
                continue;
            }
            /* Справжня апаратна чи системна помилка */
            if (bytes_written) *bytes_written = total_written;
            if (out_errno) *out_errno = err;
            return IO_ERROR;
        }
    }

    if (bytes_written) *bytes_written = total_written;
    if (out_errno) *out_errno = 0;
    return IO_SUCCESS;
}

/*
 * Надійне повне читання буфера з дескриптора.
 * Читає рівно count байтів, обробляє EINTR та виявляє кінець потоку (EOF).
 */
io_status_t safe_read_exact(int fd, void *buf, size_t count,
                            size_t *bytes_read, int *out_errno) {
    uint8_t *ptr = (uint8_t *)buf;
    size_t total_read = 0;

    while (total_read < count) {
        ssize_t n = read(fd, ptr + total_read, count - total_read);
        if (n > 0) {
            total_read += (size_t)n;
            continue;
        }
        if (n == 0) {
            /* Досягнуто кінця файлу або сокет закрито віддаленою стороною */
            if (bytes_read) *bytes_read = total_read;
            if (out_errno) *out_errno = 0;
            return (total_read == 0) ? IO_EOF : IO_ERROR;
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                /* Переривання сигналом — продовжуємо читання */
                continue;
            }
            if (bytes_read) *bytes_read = total_read;
            if (out_errno) *out_errno = err;
            return IO_ERROR;
        }
    }

    if (bytes_read) *bytes_read = total_read;
    if (out_errno) *out_errno = 0;
    return IO_SUCCESS;
}

/*
 * Безпечне закриття дескриптора з обробкою помилок.
 */
int safe_close(int fd, int *out_errno) {
    if (fd < 0) return 0;
    int res = close(fd);
    if (res == -1) {
        int err = errno;
        if (out_errno) *out_errno = err;
        return -1;
    }
    if (out_errno) *out_errno = 0;
    return 0;
}
