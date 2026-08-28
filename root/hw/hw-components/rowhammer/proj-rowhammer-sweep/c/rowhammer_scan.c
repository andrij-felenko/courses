/* rowhammer_scan.c — Системний сканер Rowhammer на мові C (POSIX/x86_64) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <x86intrin.h>

#define BUFFER_SIZE      (4 * 1024 * 1024)   /* Буфер 4 МБ для тестування */
#define ROW_SIZE_BYTES   (8 * 1024)          /* Типовий розмір рядка DRAM (8 КБ) */
#define DEFAULT_HAMMERS  200000              /* 200 тисяч активацій на пару */
#define TEST_PATTERN     0xAA                /* Чергований бітовий патерн 10101010 */

/* Отримання фізичної адреси віртуального покажчика через /proc/self/pagemap */
uintptr_t get_physical_address(const void *virtual_addr) {
    uintptr_t vaddr = (uintptr_t)virtual_addr;
    int pagemap_fd = open("/proc/self/pagemap", O_RDONLY);
    if (pagemap_fd < 0) {
        return 0; /* Доступ обмежено операційною системою */
    }

    uint64_t entry = 0;
    size_t page_size = sysconf(_SC_PAGESIZE);
    off_t offset = (vaddr / page_size) * sizeof(uint64_t);

    if (pread(pagemap_fd, &entry, sizeof(uint64_t), offset) != sizeof(uint64_t)) {
        close(pagemap_fd);
        return 0;
    }
    close(pagemap_fd);

    /* Перевіряємо, чи сторінка присутня в оперативній пам'яті (біт 63) */
    if (!(entry & (1ULL << 63))) {
        return 0;
    }

    uintptr_t pfn = entry & ((1ULL << 55) - 1);
    return (pfn * page_size) | (vaddr % page_size);
}

/* Швидкісний цикл Double-Sided Hammer з контролем серіалізації */
static inline void hammer_pair(volatile uint8_t *addr1, volatile uint8_t *addr2, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        /* Читання першого агресора зі скиданням кешу */
        (void)*addr1;
        _mm_clflush((const void *)addr1);

        /* Читання другого агресора зі скиданням кешу */
        (void)*addr2;
        _mm_clflush((const void *)addr2);

        /* Бар'єр гарантує скидання ліній перед наступною ітерацією */
        _mm_mfence();
    }
}

/* Сканування області жертви на наявність інвертованих бітів */
size_t verify_and_report_flips(const uint8_t *victim_row, size_t row_len, uint8_t expected_pattern, size_t row_idx) {
    size_t flips_found = 0;
    for (size_t i = 0; i < row_len; ++i) {
        uint8_t actual = victim_row[i];
        if (actual != expected_pattern) {
            uint8_t diff = actual ^ expected_pattern;
            for (int bit = 0; bit < 8; ++bit) {
                if (diff & (1 << bit)) {
                    flips_found++;
                    printf("[!] ЗБІЙ: Рядок %zu, байт %zu, біт %d інвертовано (%d -> %d)\n",
                           row_idx, i, bit,
                           (expected_pattern >> bit) & 1,
                           (actual >> bit) & 1);
                }
            }
        }
    }
    return flips_found;
}

int main(void) {
    printf("[*] Ініціалізація сканера Rowhammer (C-версія)\n");

    /* Виділяємо анонімну пам'ять із блокуванням у RAM */
    uint8_t *buffer = mmap(NULL, BUFFER_SIZE,
                           PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE,
                           -1, 0);

    if (buffer == MAP_FAILED) {
        perror("Помилка mmap");
        return EXIT_FAILURE;
    }

    /* Заповнюємо весь буфер контрольним шаблоном */
    memset(buffer, TEST_PATTERN, BUFFER_SIZE);

    size_t num_rows = BUFFER_SIZE / ROW_SIZE_BYTES;
    printf("[*] Виділено %zu рядків DRAM по %d байтів\n", num_rows, ROW_SIZE_BYTES);

    size_t total_bitflips = 0;

    /* Проходимо трійками: Рядок(N-1) — Агресор 1, Рядок(N) — Жертва, Рядок(N+1) — Агресор 2 */
    for (size_t r = 1; r < num_rows - 1; ++r) {
        volatile uint8_t *aggressor1 = &buffer[(r - 1) * ROW_SIZE_BYTES];
        uint8_t          *victim     = &buffer[r * ROW_SIZE_BYTES];
        volatile uint8_t *aggressor2 = &buffer[(r + 1) * ROW_SIZE_BYTES];

        uintptr_t phys_victim = get_physical_address(victim);
        if (phys_victim != 0) {
            printf("[*] Тестування сендвіча навколо рядка %zu (Phys: 0x%lx)...\n", r, (unsigned long)phys_victim);
        }

        /* Запускаємо двосторонній молот */
        hammer_pair(aggressor1, aggressor2, DEFAULT_HAMMERS);

        /* Перевіряємо рядок-жертву на перекидання бітів */
        size_t flips = verify_and_report_flips(victim, ROW_SIZE_BYTES, TEST_PATTERN, r);
        total_bitflips += flips;

        /* Відновлюємо еталонний патерн у жертві перед наступним тестом */
        if (flips > 0) {
            memset(victim, TEST_PATTERN, ROW_SIZE_BYTES);
        }
    }

    printf("[+] Сканування завершено. Загалом виявлено збоїв: %zu\n", total_bitflips);

    munmap(buffer, BUFFER_SIZE);
    return total_bitflips > 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
