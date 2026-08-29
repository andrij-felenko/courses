#ifndef BOOT_STATUS_H
#define BOOT_STATUS_H

/*
 * Єдиний набір кодів помилок завантажувача.
 * Нуль — успіх; будь-яке інше значення означає, що образ виконувати НЕ можна.
 */
typedef enum {
    BOOT_OK = 0,

    /* Розбір маніфесту */
    BOOT_ERR_MAGIC,              /* немає "SFWM" або не збігся CRC-32 заголовка */
    BOOT_ERR_INVALID_SLOT,       /* індекс слота ключа поза 0..3 */
    BOOT_ERR_FLASH_READ,         /* образ не вміщується у розділ, порожній розділ */

    /* Ланцюг довіри */
    BOOT_ERR_KEY_REVOKED,        /* біт відкликання цього слота вже спалено */
    BOOT_ERR_ROOT_MISMATCH,      /* хеш ключа не збігся з еталоном у eFuse */
    BOOT_ERR_ROLLBACK_DETECTED,  /* версія нижча за апаратний лічильник */
    BOOT_ERR_SIGNATURE_INVALID,  /* підпис не пройшов математичну перевірку */
    BOOT_ERR_CRYPTO_ENGINE,      /* сам крипторушій повернув помилку */

    /* Драйвер eFuse */
    BOOT_ERR_EFUSE_BROWNOUT,     /* напруга просіла — палити перемичку не можна */
    BOOT_ERR_EFUSE_TIMEOUT,      /* контролер не зняв BUSY */
    BOOT_ERR_EFUSE_MARGINAL,     /* комірка не підтвердилась у режимі Marginal Read */
    BOOT_ERR_EFUSE_RANGE,        /* лічильник вичерпав розрядність рядка */

    /* Запис стану завантаження */
    BOOT_ERR_STATE_WRITE,        /* сторінка стану не записалась */
    BOOT_ERR_NOT_TESTING         /* підтвердження прийшло не з пробного запуску */
} boot_status_t;

static inline const char *boot_status_str(boot_status_t status)
{
    switch (status) {
    case BOOT_OK:                     return "OK";
    case BOOT_ERR_MAGIC:              return "MAGIC/CRC";
    case BOOT_ERR_INVALID_SLOT:       return "INVALID_SLOT";
    case BOOT_ERR_FLASH_READ:         return "FLASH_READ";
    case BOOT_ERR_KEY_REVOKED:        return "KEY_REVOKED";
    case BOOT_ERR_ROOT_MISMATCH:      return "ROOT_MISMATCH";
    case BOOT_ERR_ROLLBACK_DETECTED:  return "ROLLBACK";
    case BOOT_ERR_SIGNATURE_INVALID:  return "SIGNATURE";
    case BOOT_ERR_CRYPTO_ENGINE:      return "CRYPTO_ENGINE";
    case BOOT_ERR_EFUSE_BROWNOUT:     return "EFUSE_BROWNOUT";
    case BOOT_ERR_EFUSE_TIMEOUT:      return "EFUSE_TIMEOUT";
    case BOOT_ERR_EFUSE_MARGINAL:     return "EFUSE_MARGINAL";
    case BOOT_ERR_EFUSE_RANGE:        return "EFUSE_RANGE";
    case BOOT_ERR_STATE_WRITE:        return "STATE_WRITE";
    case BOOT_ERR_NOT_TESTING:        return "NOT_TESTING";
    default:                          return "UNKNOWN";
    }
}

#endif /* BOOT_STATUS_H */
