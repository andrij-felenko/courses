// rdp_driver.c — Реалізація драйвера Option Bytes на C
#include "rdp_driver.h"

static rdp_status_t flash_wait_ready(void) {
    uint32_t timeout = 500000U;
    while ((FLASH_SR_REG & FLASH_SR_BSY_BIT) != 0U) {
        if (--timeout == 0U) {
            return RDP_STATUS_BUSY;
        }
    }
    return RDP_STATUS_OK;
}

static rdp_status_t rdp_unlock_options(void) {
    if ((FLASH_OPTCR_REG & FLASH_OPTCR_OPTLOCK) == 0U) {
        return RDP_STATUS_OK; // Вже розблоковано
    }

    // Запис магічної послідовності ключів
    FLASH_OPTKEYR_REG = FLASH_OPTKEY1;
    FLASH_OPTKEYR_REG = FLASH_OPTKEY2;

    if ((FLASH_OPTCR_REG & FLASH_OPTCR_OPTLOCK) != 0U) {
        return RDP_STATUS_UNLOCK_FAILED;
    }
    return RDP_STATUS_OK;
}

static void rdp_lock_options(void) {
    FLASH_OPTCR_REG |= FLASH_OPTCR_OPTLOCK;
}

rdp_status_t rdp_get_level(rdp_level_t *out_level) {
    if (out_level == (void *)0) {
        return RDP_STATUS_VERIFY_ERROR;
    }

    uint32_t optcr_val = FLASH_OPTCR_REG;
    uint8_t rdp_byte = (uint8_t)((optcr_val & FLASH_OPTCR_RDP_MASK) >> FLASH_OPTCR_RDP_POS);

    if (rdp_byte == (uint8_t)RDP_LEVEL_0) {
        *out_level = RDP_LEVEL_0;
    } else if (rdp_byte == (uint8_t)RDP_LEVEL_2) {
        *out_level = RDP_LEVEL_2;
    } else {
        *out_level = RDP_LEVEL_1;
    }

    return RDP_STATUS_OK;
}

rdp_status_t rdp_set_level(rdp_level_t target_level) {
    rdp_level_t current_level;
    rdp_status_t status = rdp_get_level(&current_level);
    if (status != RDP_STATUS_OK) {
        return status;
    }

    if (current_level == RDP_LEVEL_2) {
        return RDP_STATUS_ALREADY_LOCKED; // З 2-го рівня відкату немає
    }

    if (current_level == target_level) {
        return RDP_STATUS_OK; // Вже в потрібному стані
    }

    status = flash_wait_ready();
    if (status != RDP_STATUS_OK) {
        return status;
    }

    status = rdp_unlock_options();
    if (status != RDP_STATUS_OK) {
        return status;
    }

    // Формуємо нове значення OPTCR: виставляємо RDP та активуємо максимальний BOR
    uint32_t optcr = FLASH_OPTCR_REG;
    optcr &= ~FLASH_OPTCR_RDP_MASK;
    optcr &= ~(3U << 2); // Скидаємо біти BOR
    optcr |= ((uint32_t)target_level << FLASH_OPTCR_RDP_POS);
    optcr |= FLASH_OPTCR_BOR_LEV_3; // Вмикаємо апаратний захист від просадок

    FLASH_OPTCR_REG = optcr;

    // Запускаємо запис Option Bytes
    FLASH_OPTCR_REG |= FLASH_OPTCR_OPTSTRT;

    status = flash_wait_ready();
    rdp_lock_options();

    if (status != RDP_STATUS_OK) {
        return status;
    }

    // Перевірка результату запису
    rdp_level_t verified_level;
    rdp_get_level(&verified_level);
    if (verified_level != target_level) {
        return RDP_STATUS_VERIFY_ERROR;
    }

    return RDP_STATUS_OK;
}

bool rdp_is_hardened(void) {
    rdp_level_t lvl;
    if (rdp_get_level(&lvl) != RDP_STATUS_OK) {
        return false;
    }
    // Комплементарна перевірка проти глітчингу
    volatile uint32_t check_a = (lvl == RDP_LEVEL_2) ? 0x3CA5U : 0x0000U;
    volatile uint32_t check_b = (lvl != RDP_LEVEL_2) ? 0xC35AU : 0x0000U;

    return (check_a == 0x3CA5U) && (check_b == 0x0000U);
}
