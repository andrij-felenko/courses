#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>

#define BUFFER_SIZE (16 * 1024 * 1024) /* 16 МБ */

/*
 * Демонстрація оптимізації робочої множини через madvise().
 */
int main(void) {
    char *buf = (char *)mmap(NULL, BUFFER_SIZE, PROT_READ | PROT_WRITE,
                             MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) {
        perror("mmap failed");
        return EXIT_FAILURE;
    }

    /* Заповнюємо дані (всі сторінки стають резидентними) */
    memset(buf, 0xAB, BUFFER_SIZE);
    printf("16 МБ пам'яті алоковано та заповнено даними.\n");

    /* Фаза 1: Позначаємо сторінки як холодні (MADV_COLD) */
    if (madvise(buf, BUFFER_SIZE, MADV_COLD) == 0) {
        printf("Сторінки позначено як MADV_COLD (демоція у список Inactive LRU).\n");
    }

    /* Фаза 2: Звільняємо непотрібний діапазон без munmap (MADV_DONTNEED) */
    if (madvise(buf, BUFFER_SIZE, MADV_DONTNEED) == 0) {
        printf("Діапазон скинуто через MADV_DONTNEED (фізичні кадри повернено ядру).\n");
    }

    munmap(buf, BUFFER_SIZE);
    return EXIT_SUCCESS;
}
