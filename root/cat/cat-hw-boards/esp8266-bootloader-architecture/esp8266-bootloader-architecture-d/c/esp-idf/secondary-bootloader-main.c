// Логіка перевірки цілісності та атомарного вибору слота прошивки у завантажувачі
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t active_slot;   // 0: user1.bin, 1: user2.bin
    uint32_t crc32_user1;
    uint32_t crc32_user2;
} boot_config_t;

bool verify_image_checksum(uint32_t flash_addr);
void mmu_set_partition_base(uint32_t base_addr);
void jump_to_app(void);

void secondary_bootloader_main(void) {
    boot_config_t config;
    flash_read(0x0C000, &config, sizeof(config));

    uint8_t slot = config.active_slot;
    uint32_t addr = (slot == 0) ? 0x01000 : 0x81000;

    // Аварійний відкот на резервний слот у разі пошкодження нового образу
    if (!verify_image_checksum(addr)) {
        slot = 1 - slot;
        addr = (slot == 0) ? 0x01000 : 0x81000;
    }

    mmu_set_partition_base(addr);
    jump_to_app();
}
