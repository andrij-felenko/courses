#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура Віртуальної Адреси Даних (DVA - 16 байтів) */
typedef struct dva {
    uint64_t dva_word0; /* vdev (32 біти) | grid (8 бітів) | asize (24 біти) */
    uint64_t dva_word1; /* G (1 біт) | offset у 512-байтових секторах (63 біти) */
} dva_t;

/* Розширене обчислення контрольної суми Fletcher4 (256 бітів) */
typedef struct zio_cksum {
    uint64_t zc_word[4];
} zio_cksum_t;

/* Повна структура Вказівника Блоку ZFS (128 байтів) */
typedef struct blkptr {
    dva_t        blk_dva[3];    /* До 3 віртуальних адрес носія (48 байтів) */
    uint64_t     blk_prop;      /* Властивості: endian, compression, checksum, type, lsize, psize */
    uint64_t     blk_pad[2];    /* Зарезервовано */
    uint64_t     blk_phys_birth;/* TXG фізичного розміщення блоку */
    uint64_t     blk_birth;     /* Порядковий номер транзакції створення (Birth TXG) */
    uint64_t     blk_fill;      /* Лічильник заповнених dnodes */
    zio_cksum_t  blk_cksum;     /* 256-бітна контрольна сума вмісту дитячого блоку */
} blkptr_t;

/* Витягування полів із бітового поля blk_prop */
static inline uint32_t blkptr_get_lsize(const blkptr_t *bp) {
    return (uint32_t)((bp->blk_prop & 0xFFFFULL) + 1) * 512;
}

static inline uint32_t blkptr_get_psize(const blkptr_t *bp) {
    return (uint32_t)(((bp->blk_prop >> 16) & 0xFFFFULL) + 1) * 512;
}

static inline uint8_t blkptr_get_checksum_type(const blkptr_t *bp) {
    return (uint8_t)((bp->blk_prop >> 40) & 0xFFULL);
}

static inline uint8_t blkptr_get_compression_type(const blkptr_t *bp) {
    return (uint8_t)((bp->blk_prop >> 32) & 0x7FULL);
}

/* 
 * Алгоритм Fletcher4: 256-бітне накопичувальне підсумовування 64-бітних слів.
 * Вважається найшвидшим алгоритмом перевірки цілісності ZFS.
 */
zio_cksum_t zio_checksum_fletcher4(const uint64_t *buf, uint64_t size_bytes) {
    zio_cksum_t zc = {{0, 0, 0, 0}};
    uint64_t words = size_bytes / sizeof(uint64_t);
    uint64_t a = 0, b = 0, c = 0, d = 0;

    for (uint64_t i = 0; i < words; i++) {
        a += buf[i];
        b += a;
        c += b;
        d += c;
    }

    zc.zc_word[0] = a;
    zc.zc_word[1] = b;
    zc.zc_word[2] = c;
    zc.zc_word[3] = d;
    return zc;
}

int main(void) {
    blkptr_t bp;
    memset(&bp, 0, sizeof(bp));

    /* Налаштування тестового вказівника блоку */
    bp.blk_prop = (127ULL) | (63ULL << 16) | (15ULL << 32) | (7ULL << 40); /* LSIZE=64KB, PSIZE=32KB, LZ4, Fletcher4 */
    bp.blk_birth = 1042500ULL;
    bp.blk_phys_birth = 1042500ULL;
    bp.blk_dva[0].dva_word0 = (1ULL << 32) | 0x40ULL; /* VDEV=1, ASIZE=64 сектори = 32 КБ */
    bp.blk_dva[0].dva_word1 = 0x4000ULL;              /* Offset = 16384 сектори = 8 МБ */

    printf("=== ДЕКОДУВАННЯ ZFS BLKPTR_T ===\n");
    printf("Логічний розмір (LSIZE): %u байтів\n", blkptr_get_lsize(&bp));
    printf("Фізичний розмір (PSIZE): %u байтів\n", blkptr_get_psize(&bp));
    printf("Тег стиснення: %u (LZ4)\n", blkptr_get_compression_type(&bp));
    printf("Тег контрольної суми: %u (Fletcher4)\n", blkptr_get_checksum_type(&bp));
    printf("Birth TXG: %lu\n", bp.blk_birth);
    printf("DVA[0] VDEV ID: %u, Offset: 0x%lx\n", 
           (uint32_t)(bp.blk_dva[0].dva_word0 >> 32), 
           (unsigned long)((bp.blk_dva[0].dva_word1 & 0x7FFFFFFFFFFFFFFFULL) << 9));

    /* Тестовий блок даних 1024 байти (128 слів по 64 біти) */
    uint64_t sample_data[128];
    for (int i = 0; i < 128; i++) {
        sample_data[i] = 0xDEADBEEF00000000ULL | (uint64_t)i;
    }

    zio_cksum_t sum = zio_checksum_fletcher4(sample_data, sizeof(sample_data));
    printf("\n=== ОБЧИСЛЕНУ ЧЕКСУМУ FLETCHER4 ===\n");
    printf("ZC[0]: 0x%016lx\nZC[1]: 0x%016lx\nZC[2]: 0x%016lx\nZC[3]: 0x%016lx\n",
           sum.zc_word[0], sum.zc_word[1], sum.zc_word[2], sum.zc_word[3]);

    return 0;
}
