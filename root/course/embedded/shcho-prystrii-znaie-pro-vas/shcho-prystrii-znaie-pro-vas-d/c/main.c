#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SECURE_KEY_BYTES        32U
#define FLASH_SECTOR_SIZE_BYTES 4096U

typedef enum {
    TAMPER_STATUS_SAFE = 0,
    TAMPER_STATUS_TRIGGERED,
    TAMPER_STATUS_ZEROIZED
} TamperStatus;

typedef struct {
    uint8_t master_key[SECURE_KEY_BYTES];
    TamperStatus status;
    volatile bool is_compromised;
} SecureVault;

// Низькорівневі апаратні виклики до периферії МК
extern void bsp_wipe_backup_registers(void);
extern void bsp_flash_erase_sector(uint32_t address);
extern void bsp_efuse_burn_permanent_lock(void);
extern void bsp_system_hard_reset(void);

/**
 * Гарантоване затирання пам'яті, захищене від dead store elimination.
 */
void secure_zeroize_memory(void *dest, size_t len) {
    if (dest == NULL || len == 0) {
        return;
    }
    volatile uint8_t *vptr = (volatile uint8_t *)dest;
    while (len--) {
        *vptr++ = 0x00U;
    }
    // Інструкційний бар'єр: компілятор не має права переставляти операції
    __asm__ __volatile__("" : : "r"(dest) : "memory");
}

void secure_vault_init(SecureVault *vault) {
    if (!vault) return;
    vault->status = TAMPER_STATUS_SAFE;
    vault->is_compromised = false;
    secure_zeroize_memory(vault->master_key, SECURE_KEY_BYTES);
}

bool secure_vault_set_key(SecureVault *vault, const uint8_t *key_data, size_t key_len) {
    if (!vault || !key_data || key_len != SECURE_KEY_BYTES) {
        return false;
    }
    if (vault->status != TAMPER_STATUS_SAFE || vault->is_compromised) {
        return false;
    }

    for (size_t i = 0; i < SECURE_KEY_BYTES; ++i) {
        vault->master_key[i] = key_data[i];
    }
    return true;
}

/**
 * Асинхронний обробник переривання Tamper ISR.
 * Виконується з нульовим пріоритетом (найвищий у системі).
 */
void Tamper_Hardware_IRQHandler(SecureVault *vault) {
    if (!vault) return;

    // 1. Апаратне занулення Backup SRAM за один такт
    bsp_wipe_backup_registers();

    // 2. Гарантоване занулення ключів у RAM ядра
    secure_zeroize_memory(vault->master_key, SECURE_KEY_BYTES);
    vault->status = TAMPER_STATUS_TRIGGERED;
    vault->is_compromised = true;

    // 3. Затирання секторів Flash-пам'яті
    for (uint32_t addr = 0x08040000U; addr < 0x08080000U; addr += FLASH_SECTOR_SIZE_BYTES) {
        bsp_flash_erase_sector(addr);
    }

    // 4. Незворотне спалювання eFuse
    bsp_efuse_burn_permanent_lock();

    // 5. Перезапуск у безпечний стан блокування
    bsp_system_hard_reset();
}
