/*
 * Формат образу Secure Boot з боку пристрою.
 * Числа мусять збігатися з py/release/image.py — розійдуться, і завантажувач
 * відкине справний реліз.
 */
#ifndef RELEASE_IMAGE_HEADER_H
#define RELEASE_IMAGE_HEADER_H

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

#define RELEASE_MAGIC            0x53424F54u /* "SBOT" у little-endian */
#define RELEASE_HEADER_SIZE      128u
#define RELEASE_SIGNED_PREFIX    52u  /* байти заголовка, що входять у підпис */
#define RELEASE_DIGEST_SIZE      32u
#define RELEASE_SIGNATURE_SIZE   64u

/* Маска саме цієї плати. Проставляється збіркою (-DFW_HW_MASK). */
#ifndef RELEASE_CURRENT_HW_MASK
#define RELEASE_CURRENT_HW_MASK  0x0002u
#endif

typedef struct {
    uint32_t magic;
    uint32_t version_packed;   /* major<<24 | minor<<16 | patch<<8 */
    uint32_t security_counter;
    uint32_t hw_mask;
    uint32_t payload_size;
    uint8_t  payload_sha256[RELEASE_DIGEST_SIZE];
    uint8_t  signature[RELEASE_SIGNATURE_SIZE];
    uint8_t  reserved[12];
} release_header_t;

/* Поля підібрано так, щоб компілятор не додав жодного байта вирівнювання:
   packed тут не потрібен, а структура лишається придатною для читання
   на місці, без копії. */
static_assert(sizeof(release_header_t) == RELEASE_HEADER_SIZE,
              "заголовок образу мусить бути рівно 128 байтів");

typedef enum {
    RELEASE_OK = 0,
    RELEASE_ERR_TRUNCATED,   /* буфер коротший за заголовок або за тіло */
    RELEASE_ERR_ALIGNMENT,   /* буфер не на 4-байтній межі */
    RELEASE_ERR_MAGIC,       /* не наш образ або переплутано порядок байтів */
    RELEASE_ERR_HARDWARE,    /* прошивка не для цієї ревізії плати */
    RELEASE_ERR_ROLLBACK,    /* спроба відкату на вразливу версію */
    RELEASE_ERR_SIZE,        /* тіло не влазить у слот застосунку */
    RELEASE_ERR_DIGEST,      /* хеш тіла не збігся */
    RELEASE_ERR_SIGNATURE,   /* підпис не від кореня довіри */
    RELEASE_ERR_CRYPTO       /* збій самої криптобібліотеки */
} release_status_t;

const char *release_status_text(release_status_t status);

/* Розбирає версію в трійку {major, minor, patch}. */
void release_version_unpack(uint32_t packed, uint8_t out[3]);

/*
 * Структурні ворота: магія, сумісність, відкат, розміри. Динамічної пам'яті
 * не чіпає, вміст образу не копіює — повертає покажчик усередину буфера.
 * max_payload — розмір слота застосунку в байтах.
 */
release_status_t release_header_parse(const uint8_t *image,
                                      size_t image_len,
                                      uint32_t active_counter,
                                      uint32_t max_payload,
                                      const release_header_t **out_header);

#endif /* RELEASE_IMAGE_HEADER_H */
