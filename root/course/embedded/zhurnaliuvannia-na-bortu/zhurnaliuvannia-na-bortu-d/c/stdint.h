#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define FLASH_SECTOR_SIZE     4096
#define FLASH_SECTOR_COUNT    8

typedef struct {
    bool (*read)(uint32_t addr, uint8_t *buf, size_t len);
    bool (*write)(uint32_t addr, const uint8_t *buf, size_t len);
    bool (*erase_sector)(uint32_t sector_addr);
} flash_hal_t;

typedef struct {
    flash_hal_t hal;
    uint32_t    base_addr;
    uint32_t    active_sector_idx;
    uint32_t    write_offset;
    uint32_t    tail_sector_idx;
    uint32_t    seq_num;
} flash_ring_logger_t;

/* Ініціалізація та сканування існуючих секторів */
bool flash_logger_init(flash_ring_logger_t *logger, const flash_hal_t *hal, uint32_t base_addr);

/* Потокобезпечний запис двійкової події */
bool flash_logger_write(flash_ring_logger_t *logger, uint8_t level, uint8_t module_id,
                        uint32_t timestamp_ms, uint32_t token_id,
                        const uint8_t *payload, uint8_t payload_len);

/* Підтвердження успішного вивантаження сектора на сервер */
bool flash_logger_commit_tail(flash_ring_logger_t *logger, uint32_t sector_idx);
