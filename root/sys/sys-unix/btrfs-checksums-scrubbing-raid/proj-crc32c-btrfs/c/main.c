#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#if defined(__x86_64__) || defined(_M_X64)
#include <nmmintrin.h> // Intel SSE4.2 intrinsics (_mm_crc32_u64)
#define HAS_SSE42 1
#else
#define HAS_SSE42 0
#endif

// Початковий стан CRC32c у Btrfs (усі біти 1)
#define BTRFS_CRC32C_INIT 0xFFFFFFFFU

// Апаратно-прискорене обчислення CRC32c через SSE4.2
uint32_t btrfs_crc32c_hardware(uint32_t crc, const void *data, size_t length)
{
    const uint8_t *p8 = (const uint8_t *)data;
    uint64_t crc64 = (uint64_t)crc;

#if HAS_SSE42
    // 1. Вирівнювання вказівника до 8-байтної межі в пам'яті
    while (length > 0 && ((uintptr_t)p8 & 7)) {
        crc64 = _mm_crc32_u8((uint32_t)crc64, *p8++);
        length--;
    }

    // 2. Основна обробка 64-бітними блоками (8 байтів за інструкцію)
    const uint64_t *p64 = (const uint64_t *)p8;
    size_t blocks = length / sizeof(uint64_t);
    for (size_t i = 0; i < blocks; i++) {
        crc64 = _mm_crc32_u64(crc64, p64[i]);
    }

    // 3. Обробка залишкових байтів
    p8 = (const uint8_t *)(p64 + blocks);
    length %= sizeof(uint64_t);
    while (length > 0) {
        crc64 = _mm_crc32_u8((uint32_t)crc64, *p8++);
        length--;
    }
#else
    // Програмний фолбек для систем без SSE4.2 (побайтовий обхід)
    for (size_t i = 0; i < length; i++) {
        crc64 ^= p8[i];
        for (int bit = 0; bit < 8; bit++) {
            if (crc64 & 1) {
                crc64 = (crc64 >> 1) ^ 0x82F63B78U; // Зазеркалений поліном Castagnoli
            } else {
                crc64 >>= 1;
            }
        }
    }
#endif

    return (uint32_t)crc64;
}

// Завершальна інверсія бітів для специфікації Btrfs
uint32_t btrfs_crc32c_final(uint32_t raw_crc)
{
    return raw_crc ^ 0xFFFFFFFFU;
}

int main(void)
{
    // Буфер сектора даних Btrfs (4096 байтів)
    uint8_t sector_buffer[4096];
    for (size_t i = 0; i < sizeof(sector_buffer); i++) {
        sector_buffer[i] = (uint8_t)(i & 0xFF);
    }

    uint32_t crc_state = BTRFS_CRC32C_INIT;
    crc_state = btrfs_crc32c_hardware(crc_state, sector_buffer, sizeof(sector_buffer));
    uint32_t checksum = btrfs_crc32c_final(crc_state);

    printf("Обчислено CRC32c для сектора 4 КіБ: 0x%08X\n", checksum);
    return 0;
}
