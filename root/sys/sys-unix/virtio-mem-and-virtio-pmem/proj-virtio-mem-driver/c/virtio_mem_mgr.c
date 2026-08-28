/* virtio_mem_mgr.c — Ідіоматична реалізація мовою C (стандарт C11) */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <inttypes.h>

#define SUBBLOCK_SIZE_BYTES (2 * 1024 * 1024ULL) /* 2 МБ суб-блок */
#define MAX_SUBBLOCKS 64                       /* Вікно 128 МБ */

typedef enum {
    BLOCK_STATE_UNPLUGGED = 0,
    BLOCK_STATE_PLUGGED   = 1,
    BLOCK_STATE_UNMOVABLE = 2
} block_state_t;

typedef struct {
    uint64_t gpa_start;
    uint64_t requested_size;
    uint64_t plugged_size;
    uint32_t block_count;
    block_state_t blocks[MAX_SUBBLOCKS];
} virtio_mem_device_t;

void virtio_mem_init(virtio_mem_device_t *dev, uint64_t base_gpa, uint32_t count) {
    if (!dev || count > MAX_SUBBLOCKS) return;
    dev->gpa_start = base_gpa;
    dev->requested_size = 0;
    dev->plugged_size = 0;
    dev->block_count = count;
    for (uint32_t i = 0; i < count; i++) {
        dev->blocks[i] = BLOCK_STATE_UNPLUGGED;
    }
}

/* Симуляція підключення суб-блоків */
int virtio_mem_plug_blocks(virtio_mem_device_t *dev, uint64_t target_bytes) {
    if (!dev) return -1;
    uint32_t plugged_now = 0;

    for (uint32_t i = 0; i < dev->block_count; i++) {
        if (dev->plugged_size >= target_bytes) break;

        if (dev->blocks[i] == BLOCK_STATE_UNPLUGGED) {
            /* Симуляція надсилання VIRTIO_MEM_REQ_PLUG хосту */
            dev->blocks[i] = BLOCK_STATE_PLUGGED;
            dev->plugged_size += SUBBLOCK_SIZE_BYTES;
            plugged_now++;
            printf("[virtio-mem C] Блок #%u (GPA: 0x%" PRIx64 ") -> PLUGGED\n",
                   i, dev->gpa_start + (uint64_t)i * SUBBLOCK_SIZE_BYTES);
        }
    }
    return (int)plugged_now;
}

/* Симуляція гнучкого вилучення суб-блоків (flexible unplug) */
int virtio_mem_unplug_blocks(virtio_mem_device_t *dev, uint64_t target_bytes) {
    if (!dev) return -1;
    uint32_t unplugged_now = 0;

    /* Скануємо з кінця для оптимізації неперервності */
    for (int32_t i = (int32_t)dev->block_count - 1; i >= 0; i--) {
        if (dev->plugged_size <= target_bytes) break;

        if (dev->blocks[(uint32_t)i] == BLOCK_STATE_PLUGGED) {
            /* Симуляція спроби offline_pages() */
            dev->blocks[(uint32_t)i] = BLOCK_STATE_UNPLUGGED;
            dev->plugged_size -= SUBBLOCK_SIZE_BYTES;
            unplugged_now++;
            printf("[virtio-mem C] Блок #%d (GPA: 0x%" PRIx64 ") -> UNPLUGGED\n",
                   i, dev->gpa_start + (uint64_t)i * SUBBLOCK_SIZE_BYTES);
        } else if (dev->blocks[(uint32_t)i] == BLOCK_STATE_UNMOVABLE) {
            printf("[virtio-mem C] Блок #%d містить unmovable pages -> Пропущено\n", i);
        }
    }
    return (int)unplugged_now;
}

int main(void) {
    virtio_mem_device_t dev;
    virtio_mem_init(&dev, 0x100000000ULL, 16); /* 32 МБ вікно з 0x100000000 */

    printf("--- Запит на підключення 16 МБ ---\n");
    virtio_mem_plug_blocks(&dev, 16 * 1024 * 1024ULL);

    /* Імітуємо, що блок #3 зайнятий непереміщуваними даними ядра */
    dev.blocks[3] = BLOCK_STATE_UNMOVABLE;

    printf("\n--- Запит на зменшення до 4 МБ (Unplug 12 МБ) ---\n");
    virtio_mem_unplug_blocks(&dev, 4 * 1024 * 1024ULL);

    printf("\nПідсумковий plugged_size: %" PRIu64 " МБ\n", dev.plugged_size / (1024 * 1024));
    return 0;
}
