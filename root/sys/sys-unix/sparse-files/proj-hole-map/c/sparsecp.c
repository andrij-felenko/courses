/* sparsecp.c — копія файлу, що зберігає діри. */
#define _GNU_SOURCE          /* SEEK_DATA і SEEK_HOLE оголошено під ним */
#define _FILE_OFFSET_BITS 64 /* off_t на 64 біти навіть у 32-бітній збірці */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

/* pread/pwrite, а не read/write: lseek, яким ми питаємо карту, пересуває
   позицію в описі відкритого файлу — ту саму, від якої відлічував би read.
   Виклики зі своїм зсувом позиції не чіпають, і два заняття перестають
   заважати одне одному. */

static ssize_t pread_full(int fd, void *buf, size_t n, off_t off)
{
    size_t done = 0;
    while (done < n) {
        ssize_t k = pread(fd, (char *)buf + done, n - done, off + (off_t)done);
        if (k < 0) {
            if (errno == EINTR) continue;       /* сигнал — не збій */
            return -1;
        }
        if (k == 0) break;                      /* файл кінчився раніше, ніж просили */
        done += (size_t)k;
    }
    return (ssize_t)done;
}

static int pwrite_full(int fd, const void *buf, size_t n, off_t off)
{
    size_t done = 0;
    while (done < n) {
        ssize_t k = pwrite(fd, (const char *)buf + done, n - done, off + (off_t)done);
        if (k < 0) {
            if (errno == EINTR) continue;
            return -1;                          /* сюди прилітає ENOSPC */
        }
        if (k == 0) { errno = EIO; return -1; } /* нуля без помилки не буває — але страхуємось */
        done += (size_t)k;
    }
    return 0;
}

/* Чи все вікно — нулі. Побайтово перевіряти мегабайт — марна робота
   для процесора, тож ідемо машинними словами, вирівнявшись на початку. */
static int all_zero(const void *p, size_t n)
{
    const unsigned char *b = (const unsigned char *)p;
    size_t i = 0;
    while (i < n && ((uintptr_t)(b + i) % sizeof(unsigned long)) != 0)
        if (b[i++] != 0) return 0;
    for (; i + sizeof(unsigned long) <= n; i += sizeof(unsigned long))
        if (*(const unsigned long *)(const void *)(b + i) != 0) return 0;
    for (; i < n; i++)
        if (b[i] != 0) return 0;
    return 1;
}
