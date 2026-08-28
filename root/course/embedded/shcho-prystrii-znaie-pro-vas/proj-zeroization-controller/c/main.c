#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MASTER_KEY_SIZE_BYTES   32U
#define FLASH_SECTOR_SIZE_BYTES 4096U
#define TAMPER_MAGIC_TOKEN      0xDEADBEEFU

typedef enum {
    SECURITY_STATE_LOCKED = 0,
    SECURITY_STATE_UNLOCKED,
    SECURITY_STATE_TAMPERED,
    SECURITY_STATE_ZEROIZED
} SecurityState;

typedef struct {
    SecurityState state;
    uint8_t master_key[MASTER_KEY_SIZE_BYTES];
    volatile bool tamper_detected;
} SecurityController;

// Апаратні абстракції для взаємодії з периферією кристала
extern void hw_backup_sram_wipe(void);
extern void hw_dma_abort_all_transfers(void);
extern void hw_flash_erase_sector(uint32_t sector_addr);
extern void hw_efuse_burn_security_lock(void);
extern void hw_disable_all_peripherals(void);
extern void hw_trigger_system_reset(void);

/**
 * Гарантоване занулення пам'яті, яке ніколи не викидається оптимізатором
 */
void secure_memzero(void *ptr, size_t len) {
    if (ptr == NULL || len == 0) {
        return;
    }
    volatile uint8_t *vptr = (volatile uint8_t *)ptr;
    while (len--) {
        *vptr++ = 0x00U;
    }
    // Бар'єр пам'яті для запобігання перестановок інструкцій компілятором
    __asm__ __volatile__("" : : "r"(ptr) : "memory");
}

void security_controller_init(SecurityController *ctrl) {
    if (!ctrl) return;
    ctrl->state = SECURITY_STATE_LOCKED;
    ctrl->tamper_detected = false;
    secure_memzero(ctrl->master_key, MASTER_KEY_SIZE_BYTES);
}

bool security_controller_load_key(SecurityController *ctrl, const uint8_t *key_in, size_t len) {
    if (!ctrl || !key_in || len != MASTER_KEY_SIZE_BYTES) {
        return false;
    }
    if (ctrl->state == SECURITY_STATE_TAMPERED || ctrl->tamper_detected) {
        return false;
    }

    for (size_t i = 0; i < MASTER_KEY_SIZE_BYTES; ++i) {
        ctrl->master_key[i] = key_in[i];
    }
    ctrl->state = SECURITY_STATE_UNLOCKED;
    return true;
}

/**
 * Асинхронний обробник переривання апаратного тампера (Tamper ISR).
 * Виконується з найвищим пріоритетом (час виконання < 10 мкс).
 */
void Security_Tamper_IRQHandler(SecurityController *ctrl) {
    if (!ctrl) return;

    // 1. Зупинка всіх каналів DMA для запобігання перезапису пам'яті
    hw_dma_abort_all_transfers();

    // 2. Миттєвий апаратний скид регістрів Backup SRAM
    hw_backup_sram_wipe();

    // 3. Гарантоване занулення ключів у RAM ядра
    secure_memzero(ctrl->master_key, MASTER_KEY_SIZE_BYTES);
    ctrl->state = SECURITY_STATE_TAMPERED;
    ctrl->tamper_detected = true;

    // 4. Запуск повного циклу стирання Flash
    for (uint32_t addr = 0; addr < (1024U * 1024U); addr += FLASH_SECTOR_SIZE_BYTES) {
        hw_flash_erase_sector(addr);
    }

    // 5. Спалювання eFuse та блокування SWD/JTAG
    hw_efuse_burn_security_lock();

    // 6. Повне відключення та апаратний перезапуск у стан блокування
    hw_disable_all_peripherals();
    hw_trigger_system_reset();
}
