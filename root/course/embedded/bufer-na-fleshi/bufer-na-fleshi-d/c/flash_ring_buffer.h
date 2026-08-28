/* flash_ring_buffer.h */
#ifndef FLASH_RING_BUFFER_H
#define FLASH_RING_BUFFER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FLASH_SECTOR_SIZE       4096U
#define FLASH_SECTOR_MAGIC      0x53454354U /* ASCII "SECT" */
#define FLASH_RECORD_MAGIC      0x5243U     /* ASCII "RC"   */

/* Прапорці життєвого циклу запису */
#define RECORD_STATUS_FREE        0xFFU
#define RECORD_STATUS_WRITING     0xFEU
#define RECORD_STATUS_COMMITTED   0xFCU
#define RECORD_STATUS_CONSUMED    0x00U

/* Результати операцій */
typedef enum {
    FLASH_RING_OK = 0,
    FLASH_RING_ERR_FULL,
    FLASH_RING_ERR_EMPTY,
    FLASH_RING_ERR_CORRUPTED,
    FLASH_RING_ERR_IO,
    FLASH_RING_ERR_INVALID_PARAM
} flash_ring_status_t;

/* Апаратні операції Flash HAL */
typedef struct {
    int (*read)(uint32_t addr, uint8_t *buf, size_t len);
    int (*write_page)(uint32_t addr, const uint8_t *buf, size_t len);
    int (*erase_sector)(uint32_t sector_addr);
} flash_hal_t;

/* Заголовок сектора (16 байтів) */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t sector_seq;
    uint8_t  state_flag;
    uint8_t  reserved[3];
    uint32_t header_crc32;
} flash_sector_hdr_t;

/* Заголовок запису (16 байтів) */
typedef struct __attribute__((packed)) {
    uint16_t record_magic;
    uint16_t payload_len;
    uint32_t record_seq;
    uint8_t  status_flag;
    uint8_t  priority;
    uint16_t reserved;
    uint32_t payload_crc32;
} flash_record_hdr_t;

/* Контекст кільцевого буфера */
typedef struct {
    flash_hal_t hal;
    uint32_t    start_addr;       /* Початкова фізична адреса у Flash */
    uint32_t    sector_count;     /* Загальна кількість виділених секторів */
    uint32_t    head_sector_idx;  /* Індекс активного сектора для запису (0..sector_count-1) */
    uint32_t    tail_sector_idx;  /* Індекс активного сектора для читання */
    uint32_t    head_offset;      /* Зміщення всередині Head-сектора для наступного запису */
    uint32_t    tail_offset;      /* Зміщення всередині Tail-сектора для читання */
    uint32_t    next_record_seq;  /* Монотонний лічильник повідомлень */
    uint32_t    next_sector_seq;  /* Монотонний лічильник секторів */
    bool        overwrite_on_full;/* true = FIFO Drop, false = блокування при переповненні */
} flash_ring_t;

/* Публічний API */
flash_ring_status_t flash_ring_init(flash_ring_t *ring, const flash_hal_t *hal, 
                                    uint32_t start_addr, uint32_t sector_count, 
                                    bool overwrite_on_full);

flash_ring_status_t flash_ring_push(flash_ring_t *ring, const uint8_t *payload, 
                                    uint16_t len, uint8_t priority);

flash_ring_status_t flash_ring_peek(flash_ring_t *ring, uint8_t *payload_buf, 
                                    uint16_t max_buf_len, uint16_t *out_len, 
                                    uint32_t *out_record_seq);

flash_ring_status_t flash_ring_commit_pop(flash_ring_t *ring);

#ifdef __cplusplus
}
#endif

#endif /* FLASH_RING_BUFFER_H */
