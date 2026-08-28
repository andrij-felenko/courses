#include <stdint.h>
#include <stdbool.h>

#pragma pack(push, 1)

/* 16-бітний селектор сегмента */
typedef union {
    uint16_t raw;
    struct {
        uint16_t rpl   : 2;  /* Запитаний рівень привілеїв (0..3) */
        uint16_t ti    : 1;  /* 0 = GDT, 1 = LDT */
        uint16_t index : 13; /* Номер запису в таблиці дескрипторів */
    };
} segment_selector_t;

/* 8-байтовий дескриптор сегмента IA-32 */
typedef struct {
    uint16_t limit_low;       /* Межа [15:0] */
    uint16_t base_low;        /* База [15:0] */
    uint8_t  base_mid;        /* База [23:16] */
    uint8_t  type        : 4; /* Тип сегмента та права доступу */
    uint8_t  s           : 1; /* 1 = Код/Дані, 0 = Системний дескриптор */
    uint8_t  dpl         : 2; /* Рівень привілеїв дескриптора (0..3) */
    uint8_t  present     : 1; /* 1 = Сегмент присутній у пам'яті */
    uint8_t  limit_high  : 4; /* Межа [19:16] */
    uint8_t  avl         : 1; /* Вільний біт для використання ОС */
    uint8_t  long_mode   : 1; /* 1 = 64-бітний код (x86-64 Long Mode) */
    uint8_t  db_size     : 1; /* 1 = 32-бітні операнди/стек, 0 = 16-бітні */
    uint8_t  granularity : 1; /* 1 = Межа в блоках по 4 КБ, 0 = у байтах */
    uint8_t  base_high;       /* База [31:24] */
} segment_descriptor_t;

/* 16-байтовий системний дескриптор x86-64 (LDT, TSS, Call Gate) */
typedef struct {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t  base_mid_low;
    uint8_t  type        : 4;
    uint8_t  s           : 1;
    uint8_t  dpl         : 2;
    uint8_t  present     : 1;
    uint8_t  limit_high  : 4;
    uint8_t  avl         : 1;
    uint8_t  reserved0   : 2;
    uint8_t  granularity : 1;
    uint8_t  base_mid_high;
    uint32_t base_high;       /* Базова адреса [63:32] */
    uint32_t reserved1;       /* Має містити нуль */
} system_descriptor64_t;

/* 48-бітний псевдодескриптор GDTR / IDTR для 32-бітного режиму */
typedef struct {
    uint16_t limit;           /* Розмір таблиці в байтах - 1 */
    uint32_t base_address;    /* Лінійна адреса початку масиву GDT */
} gdtr32_t;

/* 80-бітний псевдодескриптор GDTR / IDTR для 64-бітного режиму */
typedef struct {
    uint16_t limit;
    uint64_t base_address;
} gdtr64_t;

#pragma pack(pop)

/* Складання 32-бітної бази з розрізнених полів дескриптора */
static inline uint32_t descriptor_decode_base32(const segment_descriptor_t *d) {
    return ((uint32_t)d->base_high << 24) |
           ((uint32_t)d->base_mid  << 16) |
           ((uint32_t)d->base_low);
}

/* Обчислення реальної межі сегмента в байтах */
static inline uint32_t descriptor_decode_limit_bytes(const segment_descriptor_t *d) {
    uint32_t raw_limit = ((uint32_t)d->limit_high << 16) | (uint32_t)d->limit_low;
    if (d->granularity) {
        return (raw_limit << 12) | 0xFFF; /* Масштабування на 4096 байтів */
    }
    return raw_limit;
}

/* Завантаження регістра GDTR у 64-бітному режимі */
static inline void load_gdtr64(const gdtr64_t *gdtr) {
    __asm__ volatile("lgdt %0" : : "m"(*gdtr) : "memory");
}
