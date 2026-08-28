#include <stdio.h>
#include <stdlib.h>

static uint8_t g_sim_flash[FLASH_SECTOR_SIZE * FLASH_SECTOR_COUNT];

static bool sim_flash_read(uint32_t addr, uint8_t *buf, size_t len) {
    if (addr + len > sizeof(g_sim_flash)) return false;
    memcpy(buf, &g_sim_flash[addr], len);
    return true;
}

static bool sim_flash_write(uint32_t addr, const uint8_t *buf, size_t len) {
    if (addr + len > sizeof(g_sim_flash)) return false;
    for (size_t i = 0; i < len; i++) {
        /* Фізика NOR Flash: можна змінити 1 на 0, але не 0 на 1 */
        g_sim_flash[addr + i] &= buf[i];
    }
    return true;
}

static bool sim_flash_erase(uint32_t sector_addr) {
    uint32_t s_idx = sector_addr / FLASH_SECTOR_SIZE;
    if (s_idx >= FLASH_SECTOR_COUNT) return false;
    memset(&g_sim_flash[s_idx * FLASH_SECTOR_SIZE], 0xFF, FLASH_SECTOR_SIZE);
    return true;
}

int main(void) {
    memset(g_sim_flash, 0xFF, sizeof(g_sim_flash));

    flash_hal_t hal = {
        .read = sim_flash_read,
        .write = sim_flash_write,
        .erase_sector = sim_flash_erase
    };

    flash_logger_t logger;
    flash_logger_init(&logger, &hal, 0);

    /* 1. Запис тестових повідомлень */
    uint32_t val1 = 120;
    flash_logger_write(&logger, LOG_LEVEL_INFO, 1, 1000, 0x1001, (uint8_t *)&val1, sizeof(val1));
    uint32_t val2 = 404;
    flash_logger_write(&logger, LOG_LEVEL_WARN, 2, 1050, 0x1002, (uint8_t *)&val2, sizeof(val2));

    /* 2. Імітація раптового збою живлення посеред запису третього кадру */
    uint32_t incomplete_addr = get_sector_address(&logger, logger.active_sector_idx) + logger.write_offset_in_sector;
    log_entry_header_t bad_hdr = {
        .magic = LOG_RECORD_MAGIC,
        .length = 24,
        .level = LOG_LEVEL_ERROR,
        .module_id = 3,
        .timestamp_ms = 1100,
        .token_id = 0x1003
    };
    /* Записано лише заголовок без корисного навантаження й без валідного CRC */
    hal.write(incomplete_addr, (const uint8_t *)&bad_hdr, sizeof(bad_hdr));

    /* 3. Перезапуск мікроконтролера (Boot Recovery) */
    flash_logger_t recovered_logger;
    flash_logger_init(&recovered_logger, &hal, 0);

    /* Перевірка: пошкоджений запис відсічено, покажчик став перед битими байтами */
    uint32_t val3 = 200;
    flash_logger_write(&recovered_logger, LOG_LEVEL_INFO, 1, 1200, 0x1004, (uint8_t *)&val3, sizeof(val3));

    return 0;
}
