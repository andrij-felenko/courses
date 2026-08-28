#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>
#include <errno.h>

#define PAGE_SIZE 4096

/*
 * Демонстрація аналізу резидентності виділеного діапазону віртуальної пам'яті.
 */
int main(void) {
    const size_t num_pages = 16;
    const size_t alloc_size = num_pages * PAGE_SIZE;

    /* Виділяємо анонімну пам'ять (ліниве виділення, сторінки ще не існують у RAM) */
    char *buffer = (char *)mmap(NULL, alloc_size, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buffer == MAP_FAILED) {
        perror("mmap failed");
        return EXIT_FAILURE;
    }

    unsigned char vec[num_pages];
    memset(vec, 0, sizeof(vec));

    printf("=== Перевірка резидентності сторінок через mincore() ===\n");

    /* 1. Стан одразу після mmap */
    if (mincore(buffer, alloc_size, vec) != 0) {
        perror("mincore failed");
        munmap(buffer, alloc_size);
        return EXIT_FAILURE;
    }

    size_t resident_initial = 0;
    for (size_t i = 0; i < num_pages; ++i) {
        if (vec[i] & 1) resident_initial++;
    }
    printf("1. Одразу після mmap(): у RAM перебуває %zu з %zu сторінок\n",
           resident_initial, num_pages);

    /* 2. Торкаємося лише парних сторінок (формуємо штучну робочу множину) */
    for (size_t i = 0; i < num_pages; i += 2) {
        buffer[i * PAGE_SIZE] = (char)(i + 1); /* Сторінковий збій ініціалізує кадр */
    }

    memset(vec, 0, sizeof(vec));
    if (mincore(buffer, alloc_size, vec) != 0) {
        perror("mincore failed");
        munmap(buffer, alloc_size);
        return EXIT_FAILURE;
    }

    printf("2. Після звернення до парних сторінок:\n   ");
    size_t resident_active = 0;
    for (size_t i = 0; i < num_pages; ++i) {
        int in_ram = vec[i] & 1;
        if (in_ram) resident_active++;
        printf("P%zu:%s ", i, in_ram ? "[RAM]" : "[---]");
    }
    printf("\n   Всього в активній робочій множині RAM: %zu сторінок (%zu kB)\n",
           resident_active, (resident_active * PAGE_SIZE) / 1024);

    munmap(buffer, alloc_size);
    return EXIT_SUCCESS;
}
