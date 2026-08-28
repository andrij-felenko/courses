/* atomic_storage.h — Транзакційне A/B сховище для вбудованих систем */
#ifndef ATOMIC_STORAGE_H
#define ATOMIC_STORAGE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ATOMIC_MAGIC_WORD     0x54534F4CUL /* "LOST" у LE */
#define ATOMIC_COMMIT_MARKER  0xA55A1234UL
#define ATOMIC_MAX_PAYLOAD    256

typedef enum {
    ATOMIC_OK = 0,
    ATOMIC_ERR_INVALID_PARAM,
    ATOMIC_ERR_FLASH_IO,
    ATOMIC_ERR_NO_VALID_DATA,
    ATOMIC_ERR_PAYLOAD_TOO_LARGE
} atomic_status_t;

/* Апаратний інтерфейс абстракції Flash */
typedef struct {
    bool (*read)(uint32_t address, void *dest, size_t size);
    bool (*write)(uint32_t address, const void *src, size_t size);
    bool (*erase_sector)(uint32_t address);
    size_t sector_size;
} flash_ops_t;

/* Заголовок сектора Flash */
typedef struct __attribute__((packed)) {
    uint32_t magic;           /* ATOMIC_MAGIC_WORD */
    uint32_t generation;      /* Монотонний лічильник покоління */
    uint16_t payload_len;     /* Довжина корисних даних */
    uint16_t reserved;        /* Вирівнювання */
    uint32_t payload_crc32;   /* Контрольна сума CRC32 корисних даних */
    uint32_t commit_marker;   /* ATOMIC_COMMIT_MARKER */
} atomic_header_t;

/* Контекст сховища */
typedef struct {
    const flash_ops_t *ops;
    uint32_t sector_a_addr;
    uint32_t sector_b_addr;
    uint32_t active_addr;
    uint32_t current_generation;
    bool is_initialized;
} atomic_store_t;

/* Публічний API */
atomic_status_t atomic_store_init(atomic_store_t *store, const flash_ops_t *ops, 
                                  uint32_t sector_a, uint32_t sector_b);
atomic_status_t atomic_store_read(atomic_store_t *store, void *dest, 
                                  size_t max_len, size_t *out_len);
atomic_status_t atomic_store_write(atomic_store_t *store, const void *src, 
                                   size_t len);

#endif /* ATOMIC_STORAGE_H */
