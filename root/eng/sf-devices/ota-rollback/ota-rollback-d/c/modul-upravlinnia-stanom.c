#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BOOT_MAGIC_VALUE       0x424F4F54UL /* "BOOT" */
#define MAX_BOOT_RETRIES       3
#define FLASH_SECTOR_SIZE      4096

typedef enum {
    SLOT_A = 0,
    SLOT_B = 1,
    SLOT_NONE = 0xFF
} slot_id_t;

typedef enum {
    STATE_EMPTY         = 0xFF,
    STATE_PENDING_TEST  = 0x01,
    STATE_CONFIRMED_OK  = 0x02,
    STATE_MARKED_FAILED = 0x03
} slot_status_t;

typedef struct {
    uint32_t magic;
    uint32_t sequence;
    uint8_t  active_slot;
    uint8_t  status;
    uint8_t  retries_left;
    uint8_t  reserved;
    uint32_t crc32;
} __attribute__((packed)) boot_record_t;

/* Програмний розрахунок CRC32 (IEEE 802.3) */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1)));
        }
    }
    return ~crc;
}

/* Емуляція апаратного читання/запису секторів Flash */
extern bool flash_read(uint32_t address, void *dest, size_t size);
extern bool flash_erase_sector(uint32_t sector_address);
extern bool flash_write(uint32_t address, const void *src, size_t size);

#define SECTOR_0_ADDR 0x08008000UL
#define SECTOR_1_ADDR 0x08009000UL

/* Перевірка цілісності запису метаданих */
static bool is_record_valid(const boot_record_t *rec) {
    if (rec->magic != BOOT_MAGIC_VALUE) return false;
    uint32_t expected_crc = calculate_crc32((const uint8_t *)rec, sizeof(boot_record_t) - sizeof(uint32_t));
    return rec->crc32 == expected_crc;
}

/* Запис нового стану в енергонезалежну пам'ять із чергуванням секторів */
bool boot_metadata_write(const boot_record_t *new_rec) {
    boot_record_t rec0, rec1;
    flash_read(SECTOR_0_ADDR, &rec0, sizeof(boot_record_t));
    flash_read(SECTOR_1_ADDR, &rec1, sizeof(boot_record_t));

    bool valid0 = is_record_valid(&rec0);
    bool valid1 = is_record_valid(&rec1);

    uint32_t target_addr = SECTOR_0_ADDR;
    uint32_t next_seq = 1;

    if (valid0 && valid1) {
        if (rec0.sequence >= rec1.sequence) {
            target_addr = SECTOR_1_ADDR;
            next_seq = rec0.sequence + 1;
        } else {
            target_addr = SECTOR_0_ADDR;
            next_seq = rec1.sequence + 1;
        }
    } else if (valid0) {
        target_addr = SECTOR_1_ADDR;
        next_seq = rec0.sequence + 1;
    } else if (valid1) {
        target_addr = SECTOR_0_ADDR;
        next_seq = rec1.sequence + 1;
    }

    boot_record_t to_write = *new_rec;
    to_write.magic = BOOT_MAGIC_VALUE;
    to_write.sequence = next_seq;
    to_write.crc32 = calculate_crc32((const uint8_t *)&to_write, sizeof(boot_record_t) - sizeof(uint32_t));

    if (!flash_erase_sector(target_addr)) return false;
    return flash_write(target_addr, &to_write, sizeof(boot_record_t));
}

/* Вибір слота та обслуговування лічильника спроб під час старту завантажувача */
slot_id_t bootloader_select_slot_and_serve_wdt(void) {
    boot_record_t rec0, rec1;
    flash_read(SECTOR_0_ADDR, &rec0, sizeof(boot_record_t));
    flash_read(SECTOR_1_ADDR, &rec1, sizeof(boot_record_t));

    bool valid0 = is_record_valid(&rec0);
    bool valid1 = is_record_valid(&rec1);

    boot_record_t active_rec;
    if (valid0 && valid1) {
        active_rec = (rec0.sequence >= rec1.sequence) ? rec0 : rec1;
    } else if (valid0) {
        active_rec = rec0;
    } else if (valid1) {
        active_rec = rec1;
    } else {
        /* Обидва сектори метаданих недійсні: аварійне відновлення на SLOT_A */
        active_rec.magic = BOOT_MAGIC_VALUE;
        active_rec.sequence = 1;
        active_rec.active_slot = (uint8_t)SLOT_A;
        active_rec.status = (uint8_t)STATE_CONFIRMED_OK;
        active_rec.retries_left = 0;
        boot_metadata_write(&active_rec);
        return SLOT_A;
    }

    /* Обробка випробувального режиму */
    if (active_rec.status == STATE_PENDING_TEST) {
        if (active_rec.retries_left > 0) {
            /* Зменшуємо лічильник спроб та перезаписуємо метадані */
            active_rec.retries_left--;
            boot_metadata_write(&active_rec);
            return (slot_id_t)active_rec.active_slot;
        } else {
            /* Спроби вичерпано: фіксуємо відкат на протилежний слот */
            active_rec.status = (uint8_t)STATE_MARKED_FAILED;
            slot_id_t fallback_slot = (active_rec.active_slot == SLOT_A) ? SLOT_B : SLOT_A;
            active_rec.active_slot = (uint8_t)fallback_slot;
            active_rec.status = (uint8_t)STATE_CONFIRMED_OK;
            active_rec.retries_left = 0;
            boot_metadata_write(&active_rec);
            return fallback_slot;
        }
    }

    if (active_rec.status == STATE_CONFIRMED_OK) {
        return (slot_id_t)active_rec.active_slot;
    }

    /* Якщо активний слот помічено як збійний, форсуємо перемикання */
    slot_id_t safe_slot = (active_rec.active_slot == SLOT_A) ? SLOT_B : SLOT_A;
    active_rec.active_slot = (uint8_t)safe_slot;
    active_rec.status = (uint8_t)STATE_CONFIRMED_OK;
    boot_metadata_write(&active_rec);
    return safe_slot;
}
