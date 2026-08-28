/* Захищений буфер для роботи з секретами в оперативній пам'яті мовою C */
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct {
    void *data;
    size_t size;
} SecureBuffer;

SecureBuffer* secure_buffer_alloc(size_t size) {
    long page_size = sysconf(_SC_PAGESIZE);
    size_t aligned_size = (size + (size_t)page_size - 1) & ~((size_t)page_size - 1);

    void *ptr = mmap(NULL, aligned_size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        return NULL;
    }

    /* 1. Блокуємо сторінку від вивантаження у swap */
    if (mlock(ptr, aligned_size) < 0) {
        perror("mlock");
    }

    /* 2. Забороняємо включення сторінки у coredump */
    if (madvise(ptr, aligned_size, MADV_DONTDUMP) < 0) {
        perror("madvise MADV_DONTDUMP");
    }

    SecureBuffer *buf = malloc(sizeof(SecureBuffer));
    if (!buf) {
        munlock(ptr, aligned_size);
        munmap(ptr, aligned_size);
        return NULL;
    }
    buf->data = ptr;
    buf->size = aligned_size;
    return buf;
}

void secure_buffer_free(SecureBuffer *buf) {
    if (!buf) return;
    if (buf->data) {
        /* 3. Гарантоване занулення перед звільненням */
        explicit_bzero(buf->data, buf->size);
        munlock(buf->data, buf->size);
        munmap(buf->data, buf->size);
    }
    free(buf);
}
