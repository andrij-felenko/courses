#include "unlock.h"

#include <string.h>

#include "frame.h"
#include "log.h"

/*
 * Верифікацію підпису дає TweetNaCl (tweetnacl.c/tweetnacl.h кладемо в проєкт):
 *   int crypto_sign_open(u8 *m, u64 *mlen, const u8 *sm, u64 n, const u8 *pk);
 * Це Ed25519 за RFC 8032; приймає лише "приєднаний" підпис sm = sig || msg.
 */
#include "tweetnacl.h"

/* Відкритий кореневий ключ розблокування виробника (зашитий у Mask ROM) */
static const uint8_t EOL_ROOT_PUBLIC_KEY[PUBLIC_KEY_LEN] = {
    0x3b, 0x6a, 0x27, 0xbc, 0xce, 0xb6, 0xa4, 0x2d,
    0x68, 0x7a, 0xa5, 0x65, 0x84, 0x88, 0xdd, 0x4d,
    0x9c, 0x86, 0x45, 0x40, 0x07, 0x69, 0x66, 0x04,
    0x69, 0x62, 0x0d, 0xa4, 0x63, 0xa5, 0x72, 0x8b
};

typedef struct {
    uint8_t  msg[CHALLENGE_MSG_LEN]; /* Nonce || Chip_UUID, лише в SRAM */
    uint32_t started_ms;
    bool     active;
} session_t;

static session_t g_session;

/*
 * Стирання через volatile: звичайний memset оптимізатор викидає як мертвий запис,
 * і ключі лишаються лежати в SRAM після виходу з функції.
 */
static void secure_memzero(void *buf, size_t len)
{
    volatile uint8_t *p = (volatile uint8_t *)buf;
    while (len-- != 0) {
        *p++ = 0x00;
    }
}

static void session_forget(void)
{
    secure_memzero(&g_session, sizeof g_session);
    g_session.active = false;
}

static bool session_expired(uint32_t now_ms)
{
    /* Різниця беззнакових цілих коректна й на переповненні лічильника тіків */
    return (uint32_t)(now_ms - g_session.started_ms) > UNLOCK_SESSION_TIMEOUT_MS;
}

void unlock_create_challenge(uint8_t out_msg[CHALLENGE_MSG_LEN])
{
    hal_trng_fill(g_session.msg, CHALLENGE_NONCE_LEN);
    hal_get_chip_uuid(&g_session.msg[CHALLENGE_NONCE_LEN]);

    g_session.started_ms = hal_get_tick_ms();
    g_session.active = true;

    memcpy(out_msg, g_session.msg, CHALLENGE_MSG_LEN);
}

void unlock_tick(uint32_t now_ms)
{
    if (g_session.active && session_expired(now_ms)) {
        session_forget();
        log_line("Challenge session expired. Nonce discarded.");
    }
}

static bool verify_signature(const uint8_t *signature, const uint8_t *msg)
{
    uint8_t attached[SIGNATURE_LEN + CHALLENGE_MSG_LEN];
    uint8_t opened[SIGNATURE_LEN + CHALLENGE_MSG_LEN];
    unsigned long long opened_len = 0;

    memcpy(attached, signature, SIGNATURE_LEN);
    memcpy(&attached[SIGNATURE_LEN], msg, CHALLENGE_MSG_LEN);

    const int rc = crypto_sign_open(opened, &opened_len, attached, sizeof attached,
                                    EOL_ROOT_PUBLIC_KEY);

    secure_memzero(opened, sizeof opened);
    secure_memzero(attached, sizeof attached);

    return rc == 0 && opened_len == CHALLENGE_MSG_LEN;
}

/*
 * Стирання переводить біти в 0xFF — залишковий заряд у зношених комірках
 * плаваючого затвора з нього ще відновлюють. Тому другим проходом пишемо нулі
 * і читаємо назад: мовчазна відмова запису не має видатися успіхом.
 */
static bool zeroize_sector(uint32_t addr)
{
    static const uint8_t zeros[128] = { 0 };
    uint8_t check[128];

    log_addr("Erasing NVS sector 0x", addr, "...");
    if (!hal_flash_erase_sector(addr)) {
        return false;
    }

    for (uint32_t off = 0; off < NVS_SECTOR_SIZE; off += sizeof zeros) {
        if (!hal_flash_write(addr + off, zeros, sizeof zeros)) {
            return false;
        }
    }

    for (uint32_t off = 0; off < NVS_SECTOR_SIZE; off += sizeof check) {
        if (!hal_flash_read(addr + off, check, sizeof check)) {
            return false;
        }
        for (size_t i = 0; i < sizeof check; i++) {
            if (check[i] != 0x00) {
                return false;
            }
        }
    }

    log_line("[OK] Overwriting zeros... [OK]");
    return true;
}

static bool zeroize_user_data(void)
{
    for (uint32_t i = 0; i < NVS_SECTORS_NUM; i++) {
        if (!zeroize_sector(NVS_BASE_ADDR + i * NVS_SECTOR_SIZE)) {
            return false;
        }
    }

    log_u32("Zeroization completed (", (NVS_SECTORS_NUM * NVS_SECTOR_SIZE) / 1024u,
            " KB sanitized).");
    return true;
}

unlock_status_t unlock_execute(const uint8_t signature[SIGNATURE_LEN])
{
    if (hal_efuse_read_unlocked()) {
        return UNLOCK_ERR_ALREADY;
    }
    if (!g_session.active) {
        return UNLOCK_ERR_NO_SESSION;
    }
    if (session_expired(hal_get_tick_ms())) {
        session_forget();
        return UNLOCK_ERR_TIMEOUT;
    }

    log_line("Verifying Ed25519 signature against ROM EOL_ROOT_PUBLIC_KEY...");
    const bool valid = verify_signature(signature, g_session.msg);

    /* Nonce одноразовий: після спроби він більше не дійсний ні за яких умов */
    session_forget();

    if (!valid) {
        return UNLOCK_ERR_BAD_SIG;
    }

    log_line("Signature OK. Proceeding to Secure Zeroization.");
    if (!zeroize_user_data()) {
        /* Секрети могли вціліти наполовину — eFuse не чіпаємо */
        return UNLOCK_ERR_FLASH;
    }

    log_line("Burning UNLOCKED eFuse bit...");
    if (!hal_efuse_burn_unlocked()) {
        return UNLOCK_ERR_EFUSE;
    }

    return UNLOCK_OK;
}

const char *unlock_status_text(unlock_status_t status)
{
    switch (status) {
    case UNLOCK_OK:             return "System status changed: UNLOCKED_DEV_MODE.";
    case UNLOCK_ERR_ALREADY:    return "Rejected: device is already unlocked.";
    case UNLOCK_ERR_NO_SESSION: return "Rejected: no active challenge.";
    case UNLOCK_ERR_TIMEOUT:    return "Rejected: challenge session timed out.";
    case UNLOCK_ERR_BAD_SIG:    return "Rejected: signature verification failed.";
    case UNLOCK_ERR_FLASH:      return "Aborted: NVS zeroization failed, device stays locked.";
    case UNLOCK_ERR_EFUSE:      return "Aborted: eFuse burn failed after zeroization.";
    default:                    return "Rejected: unknown error.";
    }
}
