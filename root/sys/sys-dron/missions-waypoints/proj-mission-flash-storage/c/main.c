#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MISSION_MAGIC           0x4D495353u // 'MISS'
#define STORAGE_SLOT_A_OFFSET   0x1000u
#define STORAGE_SLOT_B_OFFSET   0x10000u
#define MAX_MISSION_ITEMS       1500u

typedef struct __attribute__((packed)) {
    float param1;
    float param2;
    float param3;
    float param4;
    int32_t x;
    int32_t y;
    float z;
    uint16_t seq;
    uint16_t command;
    uint8_t frame;
    uint8_t current;
    uint8_t autocontinue;
    uint8_t mission_type;
} mission_item_storage_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t version;
    uint16_t count;
    uint16_t current_seq;
    uint16_t crc16;
    uint8_t reserved[20];
} mission_storage_header_t;

typedef struct {
    uint8_t active_slot; // 1 = Slot A, 2 = Slot B
    uint16_t cached_count;
    uint16_t current_seq;
    bool is_valid;
} mission_storage_driver_t;

// Апаратні функції читання/запису Flash/FRAM
extern bool hal_flash_read(uint32_t addr, void *buf, size_t len);
extern bool hal_flash_write(uint32_t addr, const void *buf, size_t len);
extern bool hal_flash_erase_sector(uint32_t addr);

// Табличний розрахунок CRC-16-CCITT (поліном 0x1021, ініціалізація 0xFFFF)
uint16_t calculate_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// Ініціалізація та пошук валідного слота при старті
bool mission_storage_init(mission_storage_driver_t *drv) {
    drv->active_slot = 0;
    drv->cached_count = 0;
    drv->current_seq = 0;
    drv->is_valid = false;

    uint8_t slot_ptr = 0;
    if (!hal_flash_read(0x0000, &slot_ptr, 1)) {
        return false;
    }

    uint8_t preferred_slot = (slot_ptr == 2) ? 2 : 1;
    uint8_t fallback_slot = (preferred_slot == 1) ? 2 : 1;

    uint8_t slots[2] = {preferred_slot, fallback_slot};
    for (int i = 0; i < 2; ++i) {
        uint8_t s = slots[i];
        uint32_t offset = (s == 1) ? STORAGE_SLOT_A_OFFSET : STORAGE_SLOT_B_OFFSET;
        
        mission_storage_header_t hdr;
        if (!hal_flash_read(offset, &hdr, sizeof(hdr))) {
            continue;
        }

        if (hdr.magic != MISSION_MAGIC || hdr.count > MAX_MISSION_ITEMS) {
            continue;
        }

        // Перевірка CRC усього масиву точок
        uint16_t calculated_crc = 0xFFFF;
        bool read_ok = true;
        mission_item_storage_t item;
        for (uint16_t j = 0; j < hdr.count; ++j) {
            uint32_t item_addr = offset + sizeof(mission_storage_header_t) + j * sizeof(mission_item_storage_t);
            if (!hal_flash_read(item_addr, &item, sizeof(item))) {
                read_ok = false;
                break;
            }
            calculated_crc = calculate_crc16((const uint8_t*)&item, sizeof(item));
        }

        if (read_ok && calculated_crc == hdr.crc16) {
            drv->active_slot = s;
            drv->cached_count = hdr.count;
            drv->current_seq = hdr.current_seq;
            drv->is_valid = true;
            return true;
        }
    }

    return false; // Обидва слоти пошкоджені або порожні
}

// Запис нового списку місії в тіньовий слот з атомарним перемиканням
bool mission_storage_commit(mission_storage_driver_t *drv, const mission_item_storage_t *items, uint16_t count) {
    if (count > MAX_MISSION_ITEMS) {
        return false;
    }

    uint8_t target_slot = (drv->active_slot == 1) ? 2 : 1;
    uint32_t target_offset = (target_slot == 1) ? STORAGE_SLOT_A_OFFSET : STORAGE_SLOT_B_OFFSET;

    // Стираємо сектори цільового слота
    hal_flash_erase_sector(target_offset);

    // Розрахунок контрольної суми та послідовний запис точок
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < count; ++i) {
        crc = calculate_crc16((const uint8_t*)&items[i], sizeof(mission_item_storage_t));
        uint32_t item_addr = target_offset + sizeof(mission_storage_header_t) + i * sizeof(mission_item_storage_t);
        if (!hal_flash_write(item_addr, &items[i], sizeof(mission_item_storage_t))) {
            return false;
        }
    }

    // Запис заголовка цільового слота
    mission_storage_header_t hdr = {
        .magic = MISSION_MAGIC,
        .version = 1,
        .count = count,
        .current_seq = 0,
        .crc16 = crc,
        .reserved = {0}
    };

    if (!hal_flash_write(target_offset, &hdr, sizeof(hdr))) {
        return false;
    }

    // Атомарне оновлення покажчика активного слота
    if (!hal_flash_erase_sector(0x0000) || !hal_flash_write(0x0000, &target_slot, 1)) {
        return false;
    }

    drv->active_slot = target_slot;
    drv->cached_count = count;
    drv->current_seq = 0;
    drv->is_valid = true;
    return true;
}
