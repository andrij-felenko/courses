/* atomic_storage.c — Реалізація стійкого до обриву живлення сховища */
#include "atomic_storage.h"
#include <string.h>

/* Табличний швидкий розрахунок IEEE 802.3 CRC32 */
static uint32_t crc32_calculate(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 1UL) {
                crc = (crc >> 1) ^ 0xEDB88320UL;
            } else {
                crc = (crc >> 1);
            }
        }
    }
    return ~crc;
}

/* Перевірка цілісності окремого сектора Flash */
static bool validate_sector(const atomic_store_t *store, uint32_t sector_addr, 
                            atomic_header_t *out_hdr) {
    atomic_header_t hdr;
    if (!store->ops->read(sector_addr, &hdr, sizeof(hdr))) {
        return false;
    }

    if (hdr.magic != ATOMIC_MAGIC_WORD) {
        return false;
    }
    if (hdr.commit_marker != ATOMIC_COMMIT_MARKER) {
        return false; /* Обрив стався до фінального комміту */
    }
    if (hdr.payload_len > ATOMIC_MAX_PAYLOAD) {
        return false;
    }

    /* Зчитування та перевірка CRC32 корисних даних */
    uint8_t buffer[ATOMIC_MAX_PAYLOAD];
    uint32_t payload_addr = sector_addr + sizeof(atomic_header_t);
    if (!store->ops->read(payload_addr, buffer, hdr.payload_len)) {
        return false;
    }

    uint32_t calc_crc = crc32_calculate(buffer, hdr.payload_len);
    if (calc_crc != hdr.payload_crc32) {
        return false; /* Спотворення бітів або незавершений запис */
    }

    if (out_hdr) {
        *out_hdr = hdr;
    }
    return true;
}

atomic_status_t atomic_store_init(atomic_store_t *store, const flash_ops_t *ops, 
                                  uint32_t sector_a, uint32_t sector_b) {
    if (!store || !ops || !ops->read || !ops->write || !ops->erase_sector) {
        return ATOMIC_ERR_INVALID_PARAM;
    }

    store->ops = ops;
    store->sector_a_addr = sector_a;
    store->sector_b_addr = sector_b;
    store->active_addr = 0;
    store->current_generation = 0;
    store->is_initialized = false;

    atomic_header_t hdr_a, hdr_b;
    bool valid_a = validate_sector(store, sector_a, &hdr_a);
    bool valid_b = validate_sector(store, sector_b, &hdr_b);

    if (valid_a && valid_b) {
        /* Обидва слоти валідні: обираємо найновіший за номером покоління */
        if ((int32_t)(hdr_a.generation - hdr_b.generation) >= 0) {
            store->active_addr = sector_a;
            store->current_generation = hdr_a.generation;
        } else {
            store->active_addr = sector_b;
            store->current_generation = hdr_b.generation;
        }
    } else if (valid_a) {
        store->active_addr = sector_a;
        store->current_generation = hdr_a.generation;
    } else if (valid_b) {
        store->active_addr = sector_b;
        store->current_generation = hdr_b.generation;
    } else {
        /* Жоден сектор не містить валідних даних (перший запуск) */
        store->active_addr = 0;
        store->current_generation = 0;
    }

    store->is_initialized = true;
    return ATOMIC_OK;
}

atomic_status_t atomic_store_read(atomic_store_t *store, void *dest, 
                                  size_t max_len, size_t *out_len) {
    if (!store || !store->is_initialized || !dest) {
        return ATOMIC_ERR_INVALID_PARAM;
    }
    if (store->active_addr == 0) {
        return ATOMIC_ERR_NO_VALID_DATA;
    }

    atomic_header_t hdr;
    if (!store->ops->read(store->active_addr, &hdr, sizeof(hdr))) {
        return ATOMIC_ERR_FLASH_IO;
    }

    size_t copy_len = (hdr.payload_len < max_len) ? hdr.payload_len : max_len;
    uint32_t payload_addr = store->active_addr + sizeof(atomic_header_t);
    
    if (!store->ops->read(payload_addr, dest, copy_len)) {
        return ATOMIC_ERR_FLASH_IO;
    }

    if (out_len) {
        *out_len = hdr.payload_len;
    }
    return ATOMIC_OK;
}

atomic_status_t atomic_store_write(atomic_store_t *store, const void *src, 
                                   size_t len) {
    if (!store || !store->is_initialized || !src) {
        return ATOMIC_ERR_INVALID_PARAM;
    }
    if (len > ATOMIC_MAX_PAYLOAD) {
        return ATOMIC_ERR_PAYLOAD_TOO_LARGE;
    }

    /* Обираємо цільовий неактивний сектор */
    uint32_t target_addr = (store->active_addr == store->sector_a_addr) 
                           ? store->sector_b_addr 
                           : store->sector_a_addr;

    /* 1. Стирання цільового сектора */
    if (!store->ops->erase_sector(target_addr)) {
        return ATOMIC_ERR_FLASH_IO;
    }

    /* 2. Підготовка заголовка (поки що без Commit Marker) */
    atomic_header_t hdr;
    hdr.magic = ATOMIC_MAGIC_WORD;
    hdr.generation = store->current_generation + 1;
    hdr.payload_len = (uint16_t)len;
    hdr.reserved = 0xFFFF;
    hdr.payload_crc32 = crc32_calculate((const uint8_t *)src, len);
    hdr.commit_marker = 0xFFFFFFFFUL; /* Маркер ще НЕ записано */

    /* 3. Запис заголовка у Flash */
    if (!store->ops->write(target_addr, &hdr, sizeof(hdr))) {
        return ATOMIC_ERR_FLASH_IO;
    }

    /* 4. Запис корисних даних */
    uint32_t payload_addr = target_addr + sizeof(atomic_header_t);
    if (!store->ops->write(payload_addr, src, len)) {
        return ATOMIC_ERR_FLASH_IO;
    }

    /* 5. Атомарний комміт: записуємо Commit Marker останнім кроком */
    uint32_t commit = ATOMIC_COMMIT_MARKER;
    uint32_t commit_offset = target_addr + offsetof(atomic_header_t, commit_marker);
    if (!store->ops->write(commit_offset, &commit, sizeof(commit))) {
        return ATOMIC_ERR_FLASH_IO;
    }

    /* 6. Оновлення стану в RAM після успішного комміту */
    store->active_addr = target_addr;
    store->current_generation = hdr.generation;

    return ATOMIC_OK;
}
