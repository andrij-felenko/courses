#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HW_EFUSE_SECURE_BOOT_MASK   (1U << 0)
#define HW_EFUSE_JTAG_DISABLE_MASK  (1U << 1)
#define EOL_UNLOCK_MAGIC            0x554E4C4BU /* 'UNLK' */

typedef enum {
    BOOT_MODE_FACTORY_LOCKED,
    BOOT_MODE_COMMUNITY_UNLOCKED,
    BOOT_MODE_AUTH_FAILURE
} boot_mode_t;

typedef struct {
    uint32_t magic;
    uint32_t device_uid[4];
    uint8_t  signature_token[64];
    uint32_t flags;
} eol_unlock_token_t;

typedef struct {
    uint32_t efuse_register_val;
    uint32_t device_uid[4];
    bool     fit_signature_enforce;
    bool     allow_external_storage_boot;
} boot_controller_t;

static bool verify_token_authenticity(const eol_unlock_token_t *token, const uint32_t expected_uid[4]) {
    if (token->magic != EOL_UNLOCK_MAGIC) {
        return false;
    }
    for (int i = 0; i < 4; ++i) {
        if (token->device_uid[i] != expected_uid[i]) {
            return false;
        }
    }
    /* Імітація криптографічної перевірки підпису RSA-2048/ECDSA через апаратний криптомодуль */
    return (token->signature_token[0] != 0x00);
}

void boot_controller_init(boot_controller_t *ctrl, uint32_t efuse_val, const uint32_t uid[4]) {
    ctrl->efuse_register_val = efuse_val;
    for (int i = 0; i < 4; ++i) {
        ctrl->device_uid[i] = uid[i];
    }
    ctrl->fit_signature_enforce = (efuse_val & HW_EFUSE_SECURE_BOOT_MASK) != 0;
    ctrl->allow_external_storage_boot = !ctrl->fit_signature_enforce;
}

boot_mode_t boot_controller_process_eol(boot_controller_t *ctrl, const eol_unlock_token_t *token) {
    if (!(ctrl->efuse_register_val & HW_EFUSE_SECURE_BOOT_MASK)) {
        /* Пристрій не був заблокований на заводі */
        ctrl->fit_signature_enforce = false;
        ctrl->allow_external_storage_boot = true;
        return BOOT_MODE_COMMUNITY_UNLOCKED;
    }

    if (token != NULL && verify_token_authenticity(token, ctrl->device_uid)) {
        /* Отримано валідний офіційний токен розблокування EOL */
        ctrl->fit_signature_enforce = false;
        ctrl->allow_external_storage_boot = true;
        printf("[BOOT] Авторизоване розблокування EOL успішне. Захист FIT деактивовано.\n");
        return BOOT_MODE_COMMUNITY_UNLOCKED;
    }

    printf("[BOOT] Апаратний Secure Boot активний. Потрібен дійсний підпис вендора.\n");
    return BOOT_MODE_FACTORY_LOCKED;
}
