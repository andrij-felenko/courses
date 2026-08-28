#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define IMAGE_MAGIC                 0x96f3b83dU
#define IMAGE_TLV_PROT_INFO_MAGIC   0x6908U
#define IMAGE_TLV_INFO_MAGIC        0x6907U

#define IMAGE_TLV_KEYHASH           0x0001U
#define IMAGE_TLV_SHA256            0x0010U
#define IMAGE_TLV_ECDSA256          0x0022U
#define IMAGE_TLV_ED25519           0x0024U
#define IMAGE_TLV_SEC_CNT           0x0050U

/* Заголовок образу MCUboot (32 байти) */
typedef struct __attribute__((packed)) {
    uint32_t ih_magic;
    uint32_t ih_load_addr;
    uint16_t ih_hdr_size;
    uint16_t ih_protect_tlv_size;
    uint32_t ih_img_size;
    uint32_t ih_flags;
    uint8_t  ver_major;
    uint8_t  ver_minor;
    uint16_t ver_revision;
    uint32_t ver_build_num;
    uint32_t _pad1;
} image_header_t;

/* Заголовок блоку TLV метаданих (4 байти) */
typedef struct __attribute__((packed)) {
    uint16_t it_magic;
    uint16_t it_tlv_tot;
} image_tlv_info_t;

/* Запис окремого TLV елемента (4 байти + дані) */
typedef struct __attribute__((packed)) {
    uint16_t it_type;
    uint16_t it_len;
} image_tlv_t;

typedef enum {
    VERIFY_OK = 0,
    ERR_INVALID_MAGIC,
    ERR_IMAGE_TOO_LARGE,
    ERR_TLV_CORRUPTED,
    ERR_SEC_COUNTER_DOWNGRADE,
    ERR_HASH_MISMATCH,
    ERR_SIGNATURE_INVALID,
    ERR_KEY_NOT_FOUND
} verify_status_t;

/* Зовнішні криптографічні інтерфейси платформи */
extern void sha256_init(void *ctx);
extern void sha256_update(void *ctx, const uint8_t *data, size_t len);
extern void sha256_final(void *ctx, uint8_t out_hash[32]);

extern bool crypto_verify_signature(uint16_t sig_type,
                                   const uint8_t *pubkey, size_t pubkey_len,
                                   const uint8_t hash[32],
                                   const uint8_t *sig, size_t sig_len);

extern uint32_t hw_efuse_read_sec_counter(void);
extern bool hw_efuse_burn_sec_counter(uint32_t new_val);

/* Головна функція повної верифікації двійкового образу */
verify_status_t verify_image_security(const uint8_t *raw_flash, size_t flash_boundary) {
    if (flash_boundary < sizeof(image_header_t)) {
        return ERR_INVALID_MAGIC;
    }

    const image_header_t *hdr = (const image_header_t *)raw_flash;
    if (hdr->ih_magic != IMAGE_MAGIC) {
        return ERR_INVALID_MAGIC;
    }

    /* Безпечна перевірка меж образу */
    uint32_t total_payload_offset = (uint32_t)hdr->ih_hdr_size + hdr->ih_img_size;
    uint32_t protected_tlv_sz = hdr->ih_protect_tlv_size;

    if (total_payload_offset + protected_tlv_sz > flash_boundary) {
        return ERR_IMAGE_TOO_LARGE;
    }

    uint32_t img_sec_counter = 0;
    bool sec_counter_present = false;

    /* 1. Обробка захищених TLV (Protected TLV), якщо вони є */
    if (protected_tlv_sz > 0) {
        if (protected_tlv_sz < sizeof(image_tlv_info_t)) {
            return ERR_TLV_CORRUPTED;
        }

        const uint8_t *p_tlv_raw = raw_flash + total_payload_offset;
        const image_tlv_info_t *p_info = (const image_tlv_info_t *)p_tlv_raw;

        if (p_info->it_magic != IMAGE_TLV_PROT_INFO_MAGIC || p_info->it_tlv_tot != protected_tlv_sz) {
            return ERR_TLV_CORRUPTED;
        }

        size_t off = sizeof(image_tlv_info_t);
        while (off + sizeof(image_tlv_t) <= protected_tlv_sz) {
            const image_tlv_t *item = (const image_tlv_t *)(p_tlv_raw + off);
            if (off + sizeof(image_tlv_t) + item->it_len > protected_tlv_sz) {
                return ERR_TLV_CORRUPTED;
            }

            if (item->it_type == IMAGE_TLV_SEC_CNT && item->it_len == sizeof(uint32_t)) {
                memcpy(&img_sec_counter, p_tlv_raw + off + sizeof(image_tlv_t), sizeof(uint32_t));
                sec_counter_present = true;
            }
            off += sizeof(image_tlv_t) + item->it_len;
        }
    }

    /* 2. Апаратна перевірка захисту від відкату (Anti-Rollback) */
    uint32_t hw_counter = hw_efuse_read_sec_counter();
    if (sec_counter_present && (img_sec_counter < hw_counter)) {
        return ERR_SEC_COUNTER_DOWNGRADE;
    }

    /* 3. Обчислення SHA-256 хешу: Header + Payload + Protected TLVs */
    uint8_t calculated_hash[32];
    uint8_t sha_ctx[256]; /* Необхідний розмір контексту криптобібліотеки */

    sha256_init(sha_ctx);
    /* Хешуємо заголовок, тіло програми та захищені метадані */
    size_t signed_area_len = total_payload_offset + protected_tlv_sz;
    sha256_update(sha_ctx, raw_flash, signed_area_len);
    sha256_final(sha_ctx, calculated_hash);

    /* 4. Розбір незахищеного трейлера підпису (Non-Protected TLV Trailer) */
    size_t trailer_offset = signed_area_len;
    if (trailer_offset + sizeof(image_tlv_info_t) > flash_boundary) {
        return ERR_TLV_CORRUPTED;
    }

    const uint8_t *trailer_raw = raw_flash + trailer_offset;
    const image_tlv_info_t *t_info = (const image_tlv_info_t *)trailer_raw;

    if (t_info->it_magic != IMAGE_TLV_INFO_MAGIC) {
        return ERR_TLV_CORRUPTED;
    }

    if (trailer_offset + t_info->it_tlv_tot > flash_boundary) {
        return ERR_IMAGE_TOO_LARGE;
    }

    const uint8_t *expected_hash = NULL;
    const uint8_t *signature = NULL;
    size_t signature_len = 0;
    uint16_t sig_type = 0;

    size_t t_off = sizeof(image_tlv_info_t);
    while (t_off + sizeof(image_tlv_t) <= t_info->it_tlv_tot) {
        const image_tlv_t *item = (const image_tlv_t *)(trailer_raw + t_off);
        if (t_off + sizeof(image_tlv_t) + item->it_len > t_info->it_tlv_tot) {
            return ERR_TLV_CORRUPTED;
        }

        const uint8_t *val = trailer_raw + t_off + sizeof(image_tlv_t);
        if (item->it_type == IMAGE_TLV_SHA256 && item->it_len == 32) {
            expected_hash = val;
        } else if (item->it_type == IMAGE_TLV_ECDSA256 || item->it_type == IMAGE_TLV_ED25519) {
            sig_type = item->it_type;
            signature = val;
            signature_len = item->it_len;
        }
        t_off += sizeof(image_tlv_t) + item->it_len;
    }

    if (!expected_hash || !signature) {
        return ERR_TLV_CORRUPTED;
    }

    /* Порівняння хешу за сталий час (Constant-Time Compare) */
    uint8_t diff = 0;
    for (size_t i = 0; i < 32; ++i) {
        diff |= (calculated_hash[i] ^ expected_hash[i]);
    }
    if (diff != 0) {
        return ERR_HASH_MISMATCH;
    }

    /* 5. Криптографічна верифікація цифрового підпису відкритим ключем */
    extern const uint8_t g_vendor_public_key[];
    extern const size_t g_vendor_public_key_len;

    if (!crypto_verify_signature(sig_type, g_vendor_public_key, g_vendor_public_key_len,
                                calculated_hash, signature, signature_len)) {
        return ERR_SIGNATURE_INVALID;
    }

    return VERIFY_OK;
}
