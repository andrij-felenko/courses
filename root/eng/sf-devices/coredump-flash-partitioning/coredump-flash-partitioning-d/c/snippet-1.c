#include <stdint.h>
#include <stdbool.h>

#define COREDUMP_MAGIC_HEADER       0x434F5245U /* ASCII сигнатура 'CORE' */
#define COREDUMP_MAX_REGIONS        4U

/* Монотонні стани комірок Flash-пам'яті */
typedef enum {
    COREDUMP_STATE_ERASED     = 0xFFFFFFFFU, /* Чистий сектор, готовий до запису */
    COREDUMP_STATE_START      = 0xFFFFFFFEU, /* Запис розпочато */
    COREDUMP_STATE_DATA_OK    = 0xFFFFFFFCU, /* Дані успішно запрограмовано */
    COREDUMP_STATE_VALID      = 0xFFFFFFF8U, /* Контрольну суму перевірено і записано */
    COREDUMP_STATE_EXTRACTED  = 0xFFFFFFF0U, /* Дамп зчитано та оброблено */
    COREDUMP_STATE_DIRTY      = 0x00000000U  /* Потребує попереднього стирання */
} coredump_state_t;

/* Опитувач сегмента пам'яті */
typedef struct {
    uint32_t start_address;                  /* Початкова адреса в RAM */
    uint32_t length_bytes;                   /* Розмір збереженого блоку */
    uint32_t memory_type;                    /* 0: Стек задачі, 1: Стек винятків, 2: Лог */
} memory_region_desc_t;

/* Заголовок слота coredump */
typedef struct {
    uint32_t magic;                          /* Сигнатура перевірки формату */
    uint32_t state;                          /* Монотонне слово стану слота */
    uint32_t seq_num;                        /* Лічильник покоління аварії */
    uint64_t timestamp_ticks;                /* Час роботи пристрою до збою */
    uint32_t crash_reason_code;              /* Код причини фатальної помилки */
    uint16_t arch_id;                        /* Архітектура процесорного ядра */
    uint16_t num_regions;                    /* Кількість збережених областей */
    memory_region_desc_t regions[COREDUMP_MAX_REGIONS];
    uint32_t header_crc;                     /* Контрольна сума метаданих */
} __attribute__((packed, aligned(4))) coredump_slot_header_t;
