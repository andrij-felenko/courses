# ⚙️ Обчислення контрольної суми CRC32c на SSE4.2

Ця вставка пояснює ⚙️ обчислення контрольної суми crc32c на sse4.2 та дозволяє зрозуміти її детальніше. Ця проектна стаття описує C-код апаратно-прискореного обчислення контрольної суми CRC32c (Castagnoli), використовуючи інструкції процесора SSE4.2, за аналогією з ядерним модулем `crc32c-intel` у Btrfs.

Btrfs за замовчуванням розбиває дані на сектори по 4096 байт і обчислює для кожного сектора 32-бітну контрольну суму CRC32c з поліномом `0x1EDC6F41`.

```c
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <nmmintrin.h> // Інструкції Intel SSE4.2 (_mm_crc32_u64)

uint32_t btrfs_crc32c_hardware(uint32_t crc, const void *buf, size_t len)
{
    const uint64_t *p64 = (const uint64_t *)buf;
    size_t blocks = len / sizeof(uint64_t);

    // Зворотний стан CRC32c (інверсія бітів)
    uint64_t crc64 = (uint64_t)~crc;

    for (size_t i = 0; i < blocks; i++) {
        crc64 = _mm_crc32_u64(crc64, p64[i]);
    }

    // Хвіст, якщо довжина не кратна 8 байтам
    const uint8_t *p8 = (const uint8_t *)(p64 + blocks);
    size_t tail = len % sizeof(uint64_t);
    for (size_t i = 0; i < tail; i++) {
        crc64 = _mm_crc32_u8((uint32_t)crc64, p8[i]);
    }

    return (uint32_t)~crc64;
}
```

## Продуктивність і виграш

Завдяки апаратній інструкції `__builtin_ia32_crc32di` / `_mm_crc32_u64`, процес обчислення CRC32c займає лише 3 такти процесора на кожні 8 байт даних. Це дозволяє Btrfs підтримувати швидкість обчислення контрольних сум на рівні **7-10 ГБ/с на одне ядро CPU**, усуваючи будь-яке навантаження на процесор під час інтенсивного I/O.
