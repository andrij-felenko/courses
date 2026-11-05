#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define COREDUMP_MAGIC_HEADER       0x434F5245U /* Сигнатура 'CORE' */
#define COREDUMP_FLASH_PAGE_SIZE    256U        /* Фізична сторінка програмування */
#define FLASH_POLL_TIMEOUT_CYCLES   500000U     /* Ліміт таймауту опитування шини */
#define COREDUMP_MAX_REGIONS        4U

/* Монотонні стани збереження аварійного слота */
typedef enum {
    COREDUMP_STATE_ERASED     = 0xFFFFFFFFU,
    COREDUMP_STATE_START      = 0xFFFFFFFEU,
    COREDUMP_STATE_DATA_OK    = 0xFFFFFFFCU,
    COREDUMP_STATE_VALID      = 0xFFFFFFF8U,
    COREDUMP_STATE_EXTRACTED  = 0xFFFFFFF0U,
    COREDUMP_STATE_DIRTY      = 0x00000000U
} coredump_state_t;

/* Опис сегмента пам'яті */
typedef struct {
    uint32_t start_address;
    uint32_t length_bytes;
    uint32_t memory_type;
} memory_region_desc_t;

/* Заголовок аварійного слота */
typedef struct {
    uint32_t magic;
    uint32_t state;
    uint32_t seq_num;
    uint64_t timestamp_ticks;
    uint32_t crash_reason_code;
    uint16_t arch_id;
    uint16_t num_regions;
    memory_region_desc_t regions[COREDUMP_MAX_REGIONS];
    uint32_t header_crc;
} __attribute__((packed, aligned(4))) coredump_slot_header_t;

/* Знімок процесорного контексту ARM Cortex-M */
typedef struct {
    uint32_t r0, r1, r2, r3, r4, r5, r6, r7;
    uint32_t r8, r9, r10, r11, r12;
    uint32_t sp, lr, pc, xpsr;
    uint32_t cfsr, hfsr, mmar, bfar;
} __attribute__((packed, aligned(4))) coredump_cpu_context_t;

/* Апаратні регістри Flash-контролера (базова адреса Flash) */
#define FLASH_BASE_ADDR        0x40023C00U
#define FLASH_SR_REG           (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x0CU))
#define FLASH_CR_REG           (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x10U))
#define FLASH_KEYR_REG         (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x04U))

#define FLASH_SR_BSY           (1U << 16)
#define FLASH_SR_ERRORS        (0x000000F2U)
#define FLASH_CR_PG            (1U << 0)
#define FLASH_CR_LOCK          (1U << 31)

/* Регістр апаратного сторожового таймера */
#define IWDG_KR_REG            (*(volatile uint32_t *)(0x40003000U))
#define IWDG_RELOAD_KEY        0x0000AAAAU

static void watchdog_feed(void) {
    IWDG_KR_REG = IWDG_RELOAD_KEY;
}

/* Швидке потокове обчислення CRC32 без виділення динамічної пам'яті */
static uint32_t crc32_step(uint32_t crc, const uint8_t *data, size_t length) {
    crc = ~crc;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            uint32_t mask = -(crc & 1U);
            crc = (crc >> 1) ^ (0xEDB88320U & mask);
        }
    }
    return ~crc;
}

/* Опитування апаратного регістра статусу Flash з лімітом таймауту */
static bool flash_wait_ready(void) {
    uint32_t timeout = FLASH_POLL_TIMEOUT_CYCLES;
    while ((FLASH_SR_REG & FLASH_SR_BSY) && (--timeout > 0)) {
        __asm__ volatile("nop");
    }
    if (timeout == 0) {
        return false; /* Зависання шини Flash */
    }
    if (FLASH_SR_REG & FLASH_SR_ERRORS) {
        FLASH_SR_REG = FLASH_SR_ERRORS; /* Скидання прапорців помилок */
        return false;
    }
    return true;
}

/* Програмування одного 32-бітного слова у Flash у режимі опитування */
static bool flash_write_word(uint32_t address, uint32_t value) {
    if (!flash_wait_ready()) {
        return false;
    }
    FLASH_CR_REG |= FLASH_CR_PG;
    *(volatile uint32_t *)address = value;
    __asm__ volatile("dsb 0xF" ::: "memory");
    __asm__ volatile("isb 0xF" ::: "memory");
    bool ok = flash_wait_ready();
    FLASH_CR_REG &= ~FLASH_CR_PG;
    return ok && (*(volatile uint32_t *)address == value);
}

/* Запис буфера з розбиттям на вирівняні 32-бітні слова та скиданням WDT */
static bool flash_write_stream(uint32_t dest_addr, const uint8_t *src, size_t size, uint32_t *running_crc) {
    size_t words = size / 4;
    const uint32_t *src32 = (const uint32_t *)src;

    for (size_t i = 0; i < words; ++i) {
        if (!flash_write_word(dest_addr + (i * 4), src32[i])) {
            return false;
        }
        if ((i % (COREDUMP_FLASH_PAGE_SIZE / 4)) == 0) {
            watchdog_feed();
        }
    }

    size_t tail_bytes = size % 4;
    if (tail_bytes > 0) {
        uint32_t tail_word = 0xFFFFFFFFU;
        uint8_t *tail_ptr = (uint8_t *)&tail_word;
        for (size_t j = 0; j < tail_bytes; ++j) {
            tail_ptr[j] = src[(words * 4) + j];
        }
        if (!flash_write_word(dest_addr + (words * 4), tail_word)) {
            return false;
        }
    }

    *running_crc = crc32_step(*running_crc, src, size);
    watchdog_feed();
    return true;
}

/* Головна точка входу аварійного збереження дампа */
bool coredump_save_record(uint32_t slot_flash_addr,
                          const coredump_cpu_context_t *cpu_ctx,
                          const memory_region_desc_t *regions,
                          uint16_t num_regions,
                          uint32_t crash_reason,
                          uint32_t seq_num) {
    coredump_slot_header_t hdr;
    hdr.magic = COREDUMP_MAGIC_HEADER;
    hdr.state = COREDUMP_STATE_START;
    hdr.seq_num = seq_num;
    hdr.timestamp_ticks = 0; /* Опитування апаратного таймера або лічильника тактів */
    hdr.crash_reason_code = crash_reason;
    hdr.arch_id = 0x0001; /* ARM Cortex-M */
    hdr.num_regions = num_regions > COREDUMP_MAX_REGIONS ? COREDUMP_MAX_REGIONS : num_regions;

    for (uint16_t i = 0; i < hdr.num_regions; ++i) {
        hdr.regions[i] = regions[i];
    }
    hdr.header_crc = 0;

    /* Запис стану COREDUMP_STATE_START */
    if (!flash_write_word(slot_flash_addr + offsetof(coredump_slot_header_t, state), COREDUMP_STATE_START)) {
        return false;
    }

    uint32_t write_offset = sizeof(coredump_slot_header_t);
    uint32_t running_crc = 0;

    /* 1. Запис контексту процесора */
    if (!flash_write_stream(slot_flash_addr + write_offset,
                            (const uint8_t *)cpu_ctx,
                            sizeof(coredump_cpu_context_t),
                            &running_crc)) {
        return false;
    }
    write_offset += sizeof(coredump_cpu_context_t);

    /* 2. Запис збережених сегментів пам'яті */
    for (uint16_t r = 0; r < hdr.num_regions; ++r) {
        const uint8_t *reg_data = (const uint8_t *)hdr.regions[r].start_address;
        size_t reg_size = hdr.regions[r].length_bytes;
        if (!flash_write_stream(slot_flash_addr + write_offset, reg_data, reg_size, &running_crc)) {
            return false;
        }
        write_offset += reg_size;
    }

    /* 3. Запис кінцевика контрольної суми CRC32 */
    if (!flash_write_word(slot_flash_addr + write_offset, running_crc)) {
        return false;
    }

    /* 4. Атомарний коміт: перехід у стан COREDUMP_STATE_VALID */
    if (!flash_write_word(slot_flash_addr + offsetof(coredump_slot_header_t, state), COREDUMP_STATE_VALID)) {
        return false;
    }

    return true;
}
