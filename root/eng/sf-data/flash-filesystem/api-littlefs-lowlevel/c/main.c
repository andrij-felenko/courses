#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define LFS_ERR_OK       0
#define LFS_ERR_IO      -5
#define LFS_ERR_CORRUPT -84

typedef uint32_t lfs_block_t;
typedef uint32_t lfs_off_t;
typedef uint32_t lfs_size_t;

struct lfs_config;

/* Зовнішній апаратний рівень передачі даних SPI */
extern bool spi_flash_hardware_read(uint32_t address, uint8_t *dest, size_t length);
extern bool spi_flash_hardware_page_prog(uint32_t address, const uint8_t *src, size_t length);
extern bool spi_flash_hardware_sector_erase(uint32_t address);
extern bool spi_flash_hardware_wait_ready(uint32_t timeout_ms);

typedef struct {
    uint32_t base_address;
    uint32_t sector_size;
    uint32_t total_blocks;
} spi_flash_context_t;

int bdev_read(const struct lfs_config *c, lfs_block_t block, lfs_off_t off, void *buffer, lfs_size_t size) {
    const spi_flash_context_t *ctx = (const spi_flash_context_t *)c->context;
    if (block >= ctx->total_blocks || off + size > ctx->sector_size) {
        return LFS_ERR_IO;
    }

    uint32_t phys_addr = ctx->base_address + (block * ctx->sector_size) + off;
    if (!spi_flash_hardware_read(phys_addr, (uint8_t *)buffer, size)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int bdev_prog(const struct lfs_config *c, lfs_block_t block, lfs_off_t off, const void *buffer, lfs_size_t size) {
    const spi_flash_context_t *ctx = (const spi_flash_context_t *)c->context;
    if (block >= ctx->total_blocks || off + size > ctx->sector_size) {
        return LFS_ERR_IO;
    }

    uint32_t phys_addr = ctx->base_address + (block * ctx->sector_size) + off;
    if (!spi_flash_hardware_page_prog(phys_addr, (const uint8_t *)buffer, size)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int bdev_erase(const struct lfs_config *c, lfs_block_t block) {
    const spi_flash_context_t *ctx = (const spi_flash_context_t *)c->context;
    if (block >= ctx->total_blocks) {
        return LFS_ERR_IO;
    }

    uint32_t phys_addr = ctx->base_address + (block * ctx->sector_size);
    if (!spi_flash_hardware_sector_erase(phys_addr)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int bdev_sync(const struct lfs_config *c) {
    (void)c;
    /* Таймаут 500 мс покриває максимальний час стирання сектора */
    if (!spi_flash_hardware_wait_ready(500)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}
