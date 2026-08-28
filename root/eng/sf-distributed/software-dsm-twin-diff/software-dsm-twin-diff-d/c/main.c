#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define PAGE_SIZE 4096

typedef struct {
    uint16_t offset;
    uint16_t length;
} DiffHeader;

size_t generate_page_diff(const uint8_t *page, const uint8_t *twin, uint8_t *diff_out) {
    const uint64_t *p64 = (const uint64_t*)page;
    const uint64_t *t64 = (const uint64_t*)twin;
    size_t num_words = PAGE_SIZE / sizeof(uint64_t);
    size_t out_idx = 0;
    size_t i = 0;

    while (i < num_words) {
        /* Швидкий пропуск незмінених 64-бітних слів */
        if (p64[i] == t64[i]) {
            i++;
            continue;
        }

        /* Знайдено змінене слово: визначаємо межі неперервного блоку змін */
        size_t start_byte = i * sizeof(uint64_t);
        while (start_byte < PAGE_SIZE && page[start_byte] == twin[start_byte]) {
            start_byte++;
        }

        size_t end_byte = (i + 1) * sizeof(uint64_t);
        if (end_byte > PAGE_SIZE) end_byte = PAGE_SIZE;

        /* Розширюємо кінець блоку змін вперед */
        while (end_byte < PAGE_SIZE && page[end_byte] != twin[end_byte]) {
            end_byte++;
        }

        size_t run_len = end_byte - start_byte;

        /* Записуємо дескриптор: зсув, довжина та байти даних */
        DiffHeader hdr;
        hdr.offset = (uint16_t)start_byte;
        hdr.length = (uint16_t)run_len;

        memcpy(&diff_out[out_idx], &hdr, sizeof(DiffHeader));
        out_idx += sizeof(DiffHeader);

        memcpy(&diff_out[out_idx], &page[start_byte], run_len);
        out_idx += run_len;

        i = end_byte / sizeof(uint64_t) + 1;
    }

    return out_idx; /* Повертає загальний розмір згенерованого Diff-пакета в байтах */
}
