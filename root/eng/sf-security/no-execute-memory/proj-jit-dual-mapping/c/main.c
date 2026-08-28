#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>

/* Сигнатура динамічно скомпільованої функції: int64_t func(int64_t a, int64_t b) */
typedef int64_t (*jit_func_t)(int64_t, int64_t);

/* Структура подвійного JIT-буфера */
typedef struct {
    int fd;
    size_t size;
    uint8_t *write_view;   /* Відображення для запису (PROT_READ | PROT_WRITE) */
    const void *exec_view; /* Відображення для виконання (PROT_READ | PROT_EXEC) */
} jit_buffer_t;

/* Ініціалізація та налаштування подвійного відображення */
int jit_buffer_init(jit_buffer_t *buf, size_t requested_size) {
    if (!buf || requested_size == 0) return -1;

    /* Вирівнювання розміру за межею сторінки апаратного MMU (4096 байтів) */
    long page_size = sysconf(_SC_PAGESIZE);
    buf->size = (requested_size + page_size - 1) & ~(page_size - 1);

    /* 1. Створення анонімного файлового дескриптора в пам'яті */
    buf->fd = memfd_create("jit_dual_mapped", MFD_CLOEXEC);
    if (buf->fd < 0) {
        perror("memfd_create failed");
        return -1;
    }

    /* 2. Фіксація розміру спільного сегмента пам'яті */
    if (ftruncate(buf->fd, (off_t)buf->size) < 0) {
        perror("ftruncate failed");
        close(buf->fd);
        return -1;
    }

    /* 3. Перший мапінг: доступ лише для запису та читання (RW) */
    buf->write_view = (uint8_t *)mmap(NULL, buf->size,
                                       PROT_READ | PROT_WRITE,
                                       MAP_SHARED, buf->fd, 0);
    if (buf->write_view == MAP_FAILED) {
        perror("mmap RW failed");
        close(buf->fd);
        return -1;
    }

    /* 4. Другий мапінг: доступ лише для виконання та читання (RX) */
    buf->exec_view = mmap(NULL, buf->size,
                          PROT_READ | PROT_EXEC,
                          MAP_SHARED, buf->fd, 0);
    if (buf->exec_view == MAP_FAILED) {
        perror("mmap RX failed");
        munmap(buf->write_view, buf->size);
        close(buf->fd);
        return -1;
    }

    return 0;
}

/* Коректне звільнення ресурсів */
void jit_buffer_free(jit_buffer_t *buf) {
    if (!buf) return;
    if (buf->exec_view && buf->exec_view != MAP_FAILED) {
        munmap((void *)buf->exec_view, buf->size);
    }
    if (buf->write_view && buf->write_view != MAP_FAILED) {
        munmap(buf->write_view, buf->size);
    }
    if (buf->fd >= 0) {
        close(buf->fd);
    }
    buf->write_view = NULL;
    buf->exec_view = NULL;
    buf->fd = -1;
}

int main(void) {
    jit_buffer_t jit;
    if (jit_buffer_init(&jit, 4096) != 0) {
        fprintf(stderr, "[-] Помилка створення JIT-буфера\n");
        return EXIT_FAILURE;
    }

    printf("[+] JIT Dual Buffer створено:\n");
    printf("    Write view (RW): %p\n", (void *)jit.write_view);
    printf("    Exec view  (RX): %p\n", jit.exec_view);

    /* Машинні інструкції x86-64 для функції f(a, b) = a * 3 + b + 7
     * System V AMD64 ABI:
     *   a знаходиться в RDI, b знаходиться в RSI, результат у RAX
     */
    const uint8_t code[] = {
        0x48, 0x8d, 0x04, 0x7f, /* lea rax, [rdi + rdi*2] ; RAX = a * 3        */
        0x48, 0x01, 0xf0,       /* add rax, rsi           ; RAX = (a * 3) + b  */
        0x48, 0x83, 0xc0, 0x07, /* add rax, 7             ; RAX += 7           */
        0xc3                    /* ret                    ; повернення         */
    };

    /* 1. Запис машинного коду через RW-покажчик */
    memcpy(jit.write_view, code, sizeof(code));

    /* 2. Інвалідація кешу інструкцій (Instruction Cache Flushing) */
    __builtin___clear_cache((char *)jit.write_view, (char *)jit.write_view + sizeof(code));

    /* 3. Виклик функції через RX-покажчик */
    jit_func_t fn = (jit_func_t)jit.exec_view;
    int64_t arg1 = 10;
    int64_t arg2 = 5;
    int64_t result = fn(arg1, arg2);

    /* Очікувано: 10 * 3 + 5 + 7 = 42 */
    printf("[+] Результат виклику JIT-коду: calculate(%ld, %ld) = %ld\n", arg1, arg2, result);

    if (result == 42) {
        printf("[✓] Інваріант W^X збережено, код виконано успішно.\n");
    }

    jit_buffer_free(&jit);
    return EXIT_SUCCESS;
}
