#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Коди повернення модуля депровізіонування */
typedef enum {
    DECOM_OK                    =  0,
    DECOM_ERR_INVALID_PARAM     = -1,
    DECOM_ERR_FLASH_ERASE_FAIL  = -2,
    DECOM_ERR_FLASH_VERIFY_FAIL = -3,
    DECOM_ERR_EFUSE_BLOW_FAIL   = -4,
    DECOM_ERR_SE_COMM_FAIL      = -5
} decom_status_t;

/* Опис цільового розділу Flash для затирання */
typedef struct {
    uint32_t start_address;
    uint32_t size_bytes;
    const char *partition_label;
} flash_partition_target_t;

/* Апаратні абстракції периферії */
extern int hal_flash_erase_sector(uint32_t sector_addr);
extern int hal_flash_write(uint32_t addr, const uint8_t *data, size_t len);
extern int hal_flash_read(uint32_t addr, uint8_t *data, size_t len);
extern int hal_efuse_burn_bit(uint32_t block, uint32_t bit_index);
extern bool hal_efuse_read_bit(uint32_t block, uint32_t bit_index);
extern int hal_sha256_calculate(const uint8_t *data, size_t len, uint8_t out_hash[32]);

#define FLASH_SECTOR_SIZE       4096
#define EFUSE_BLOCK_SECURITY    0
#define EFUSE_BIT_JTAG_DISABLE  3
#define EFUSE_BIT_BOOT_DISABLE  4
#define EFUSE_BIT_LIFECYCLE_END 7

/**
 * @brief Криптографічно безпечне затирання пам'яті.
 *        Гарантує захист від оптимізації Dead Store Elimination.
 */
static void secure_zero_memory(void *ptr, size_t size) {
    if (ptr == NULL || size == 0) {
        return;
    }
    volatile uint8_t *vptr = (volatile uint8_t *)ptr;
    while (size--) {
        *vptr++ = 0x00;
    }
    /* Бар'єр пам'яті для компілятора */
    __asm__ __volatile__("" : : "r"(ptr) : "memory");
}

/**
 * @brief Багатопрохідне затирання та секторне стирання розділу Flash.
 *        Прохід 1: Запис нулями (0x00)
 *        Прохід 2: Запис інвертованим шаблоном (0xAA)
 *        Прохід 3: Апаратний Flash Erase (усі біти -> 0xFF)
 *        Прохід 4: Верифікація чистоти секторів
 */
static decom_status_t wipe_flash_partition(const flash_partition_target_t *part) {
    if (part == NULL || part->size_bytes == 0 || (part->size_bytes % FLASH_SECTOR_SIZE) != 0) {
        return DECOM_ERR_INVALID_PARAM;
    }

    uint8_t buffer[256];
    uint32_t num_sectors = part->size_bytes / FLASH_SECTOR_SIZE;

    for (uint32_t s = 0; s < num_sectors; ++s) {
        uint32_t sector_addr = part->start_address + (s * FLASH_SECTOR_SIZE);

        /* Прохід 1: Запис нулями */
        memset(buffer, 0x00, sizeof(buffer));
        for (uint32_t off = 0; off < FLASH_SECTOR_SIZE; off += sizeof(buffer)) {
            if (hal_flash_write(sector_addr + off, buffer, sizeof(buffer)) != 0) {
                return DECOM_ERR_FLASH_ERASE_FAIL;
            }
        }

        /* Прохід 2: Запис патерном 0xAA */
        memset(buffer, 0xAA, sizeof(buffer));
        for (uint32_t off = 0; off < FLASH_SECTOR_SIZE; off += sizeof(buffer)) {
            if (hal_flash_write(sector_addr + off, buffer, sizeof(buffer)) != 0) {
                return DECOM_ERR_FLASH_ERASE_FAIL;
            }
        }

        /* Прохід 3: Апаратне високовольтне стирання сектора в 0xFF */
        if (hal_flash_erase_sector(sector_addr) != 0) {
            return DECOM_ERR_FLASH_ERASE_FAIL;
        }

        /* Прохід 4: Контрольна верифікація (усі байти мають бути 0xFF) */
        for (uint32_t off = 0; off < FLASH_SECTOR_SIZE; off += sizeof(buffer)) {
            if (hal_flash_read(sector_addr + off, buffer, sizeof(buffer)) != 0) {
                return DECOM_ERR_FLASH_ERASE_FAIL;
            }
            for (size_t b = 0; b < sizeof(buffer); ++b) {
                if (buffer[b] != 0xFF) {
                    secure_zero_memory(buffer, sizeof(buffer));
                    return DECOM_ERR_FLASH_VERIFY_FAIL;
                }
            }
        }
    }

    secure_zero_memory(buffer, sizeof(buffer));
    return DECOM_OK;
}

/**
 * @brief Апаратне блокування чипа через eFuses (термінальне списання).
 */
static decom_status_t blow_lockdown_fuses(bool permanent_destruction) {
    if (!permanent_destruction) {
        return DECOM_OK;
    }

    /* 1. Блокування інтерфейсу JTAG/SWD */
    if (hal_efuse_burn_bit(EFUSE_BLOCK_SECURITY, EFUSE_BIT_JTAG_DISABLE) != 0) {
        return DECOM_ERR_EFUSE_BLOW_FAIL;
    }

    /* 2. Блокування UART-завантажувача */
    if (hal_efuse_burn_bit(EFUSE_BLOCK_SECURITY, EFUSE_BIT_BOOT_DISABLE) != 0) {
        return DECOM_ERR_EFUSE_BLOW_FAIL;
    }

    /* 3. Фінальний термінальний перехід життєвого циклу */
    if (hal_efuse_burn_bit(EFUSE_BLOCK_SECURITY, EFUSE_BIT_LIFECYCLE_END) != 0) {
        return DECOM_ERR_EFUSE_BLOW_FAIL;
    }

    /* Верифікація спаленого стану */
    if (!hal_efuse_read_bit(EFUSE_BLOCK_SECURITY, EFUSE_BIT_LIFECYCLE_END)) {
        return DECOM_ERR_EFUSE_BLOW_FAIL;
    }

    return DECOM_OK;
}

/**
 * @brief Головна процедура виведення пристрою з ладу.
 */
decom_status_t device_execute_decommission(const flash_partition_target_t *targets,
                                           size_t target_count,
                                           bool permanent_hardware_lock,
                                           uint8_t out_audit_receipt[32]) {
    if (targets == NULL || target_count == 0 || out_audit_receipt == NULL) {
        return DECOM_ERR_INVALID_PARAM;
    }

    /* 1. Послідовне гарантоване затирання всіх конфіденційних розділів */
    for (size_t i = 0; i < target_count; ++i) {
        decom_status_t st = wipe_flash_partition(&targets[i]);
        if (st != DECOM_OK) {
            return st;
        }
    }

    /* 2. Апаратне блокування eFuses (якщо обрано режим списання на брухт) */
    decom_status_t fuse_st = blow_lockdown_fuses(permanent_hardware_lock);
    if (fuse_st != DECOM_OK) {
        return fuse_st;
    }

    /* 3. Генерація фінального криптографічного чека аудиту */
    uint8_t audit_entropy[64];
    memset(audit_entropy, 0xA5, sizeof(audit_entropy));
    audit_entropy[0] = permanent_hardware_lock ? 0x01 : 0x00;
    audit_entropy[1] = (uint8_t)target_count;

    hal_sha256_calculate(audit_entropy, sizeof(audit_entropy), out_audit_receipt);
    secure_zero_memory(audit_entropy, sizeof(audit_entropy));

    return DECOM_OK;
}
