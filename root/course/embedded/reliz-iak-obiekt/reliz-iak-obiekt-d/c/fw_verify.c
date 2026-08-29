#include "fw_verify.h"

#include "bsp.h"
#include "sha256.h"

/* Ed25519 бере Monocypher 4.x: crypto_ed25519_check() повертає 0, коли підпис
   дійсний, і -1 інакше. Арифметику кривої Edwards25519 у проєкт не тягнемо —
   це окрема тема, а не предмет завантажувача. */
#include "monocypher-ed25519.h"

/* Порівняння за сталий час: підсумовуємо різницю всіх байтів і лише потім
   дивимось на результат. Ранній вихід на першому розбіжному байті зливає
   зловмиснику, скільки байтів гешу він уже вгадав. */
static int equal_ct(const uint8_t *a, const uint8_t *b, size_t len)
{
    uint8_t diff = 0u;
    for (size_t i = 0; i < len; i++) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    return diff == 0u;
}

/* Потокове обчислення гешу тіла: читаємо Flash шматками по 256 байтів.
   Тіло буває на сотні кілобайтів — цілком у RAM воно не поміститься ніколи. */
static fw_verify_t hash_payload(uint32_t address, uint32_t size, uint8_t out[32])
{
    sha256_t ctx;
    uint8_t chunk[256];
    uint32_t done = 0u;

    sha256_init(&ctx);
    while (done < size) {
        uint32_t take = size - done;
        if (take > sizeof chunk) {
            take = (uint32_t)sizeof chunk;
        }
        if (bsp_flash_read(address + done, chunk, take) != 0) {
            return FW_ERR_FLASH_IO;
        }
        sha256_update(&ctx, chunk, take);
        done += take;
    }
    sha256_final(&ctx, out);
    return FW_OK;
}

fw_verify_t fw_verify_release(const fw_header_t *hdr, uint32_t payload_addr)
{
    uint8_t calculated[FW_SHA256_LEN];
    const uint8_t *root_key;
    uint8_t pcb_rev;
    fw_verify_t rc;

    /* 1. Магічне число й версія формату. Стерта Flash — це 0xFFFFFFFF,
          і саме тут вона відсікається, ще до будь-якої математики. */
    if (hdr->magic_word != FW_HEADER_MAGIC ||
        hdr->format_version != FW_HEADER_FORMAT_VERSION) {
        return FW_ERR_BAD_MAGIC;
    }

    /* 2. Сумісність із залізом: спершу виріб, потім ревізія плати. */
    if (hdr->target_hw_id != bsp_hw_platform_id()) {
        return FW_ERR_HW_INCOMPATIBLE;
    }
    pcb_rev = bsp_pcb_revision();
    if (pcb_rev < hdr->hw_rev_min || pcb_rev > hdr->hw_rev_max) {
        return FW_ERR_HW_INCOMPATIBLE;
    }

    /* 3. Anti-rollback. Підпис старого релізу бездоганний — і саме тому
          порівняння з апаратним лічильником іде ДО перевірки підпису:
          відкликану версію ми не приймаємо навіть дійсно підписану. */
    if (hdr->security_version < bsp_security_counter()) {
        return FW_ERR_ROLLBACK;
    }

    /* 4. Підпис над першими 64 байтами заголовка. Ключ беремо з OTP;
          його там може не бути — тоді перевіряти нема чим. */
    root_key = bsp_root_public_key();
    if (root_key == 0) {
        return FW_ERR_NO_ROOT_KEY;
    }
    if (crypto_ed25519_check(hdr->signature, root_key,
                             (const uint8_t *)hdr, FW_HEADER_SIGNED_BYTES) != 0) {
        return FW_ERR_BAD_SIGNATURE;
    }

    /* Геометрія. Поля вже засвідчені підписом, але перш ніж читати
       payload_size байтів, переконуємось, що вони лежать там, де ми їх
       чекаємо: образ під іншу карту пам'яті впаде в HardFault на першій же
       абсолютній адресації. */
    if (hdr->load_address != payload_addr ||
        hdr->payload_size == 0u ||
        hdr->payload_size > BSP_APP_MAX_PAYLOAD) {
        return FW_ERR_BAD_GEOMETRY;
    }

    /* 5. Геш тіла. Підпис засвідчив поле payload_sha256; тепер лишилось
          довести, що байти у Flash йому відповідають. */
    rc = hash_payload(payload_addr, hdr->payload_size, calculated);
    if (rc != FW_OK) {
        return rc;
    }
    if (!equal_ct(calculated, hdr->payload_sha256, FW_SHA256_LEN)) {
        return FW_ERR_HASH_MISMATCH;
    }

    return FW_OK;
}

const char *fw_verify_message(fw_verify_t code)
{
    switch (code) {
    case FW_OK:                  return "OK";
    case FW_ERR_BAD_MAGIC:       return "ERR_FW_BAD_MAGIC";
    case FW_ERR_HW_INCOMPATIBLE: return "ERR_FW_HW_INCOMPATIBLE";
    case FW_ERR_ROLLBACK:        return "ERR_FW_ROLLBACK_DETECTED";
    case FW_ERR_BAD_GEOMETRY:    return "ERR_FW_BAD_GEOMETRY";
    case FW_ERR_NO_ROOT_KEY:     return "ERR_FW_NO_ROOT_KEY";
    case FW_ERR_BAD_SIGNATURE:   return "ERR_FW_INVALID_SIGNATURE";
    case FW_ERR_HASH_MISMATCH:   return "ERR_FW_HASH_MISMATCH";
    case FW_ERR_FLASH_IO:        return "ERR_FW_FLASH_IO";
    default:                     return "ERR_FW_UNKNOWN";
    }
}
