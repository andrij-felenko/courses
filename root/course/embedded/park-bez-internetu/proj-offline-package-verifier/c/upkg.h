#ifndef UPKG_H
#define UPKG_H

/* Формат офлайн-контейнера прошивки .upkg і потоковий верифікатор для MCU.
 *
 * Пристрій у полі не має мережі: перевірити відкликання сертифіката ніде,
 * запитати одноразовий токен ніде. Усе, що потрібне для рішення "прошивати
 * чи ні", лежить усередині файла на флешці техніка.
 *
 * Розкладка контейнера (усі числа Little-Endian, як у Cortex-M):
 *   [0   .. 127]  заголовок метаданих, рівно 128 байтів
 *   [128 .. 191]  Ed25519-підпис ключем випуску РІВНО над цими 128 байтами
 *   [192 .. ...]  таблиця хешів: chunk_count записів по 32 байти
 *   далі          потік чанків по 4096 байтів (останній може бути коротшим)
 *   далі, з вирівнюванням на 4096 — сектор квитанції аудиту
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "sha256.h"

#define UPKG_MAGIC          0x47504B55u  /* "UPKG" у Little-Endian */
#define UPKG_RECEIPT_MAGIC  0x50435255u  /* "URCP" — квитанція */
#define UPKG_FORMAT_VER     1u

#define UPKG_HEADER_SIZE    128u
#define UPKG_SIG_SIZE       64u
#define UPKG_HASH_SIZE      32u
#define UPKG_PUBKEY_SIZE    32u
#define UPKG_CHUNK_SIZE     4096u  /* сектор NOR-флеш і водночас крок таблиці */

/* Стеля образу — 16 МБ. Потрібна не заради ліміту, а щоб множення
 * chunk_count * 4096 гарантовано не переповнило 32-бітний лічильник
 * зміщення на підробленому заголовку. */
#define UPKG_MAX_CHUNKS     4096u

#define UPKG_BOOT_RETRIES   3u     /* скільки спроб дається новій прошивці */

typedef enum {
    UPKG_OK = 0,
    UPKG_ERR_IO,                   /* носій відвалився: флешку висмикнули */
    UPKG_ERR_INVALID_MAGIC,
    UPKG_ERR_FORMAT,               /* поля заголовка суперечать одне одному */
    UPKG_ERR_HW_MISMATCH,
    UPKG_ERR_ROLLBACK_DETECTED,
    UPKG_ERR_SIGNATURE_INVALID,
    UPKG_ERR_TABLE_HASH_MISMATCH,
    UPKG_ERR_CHUNK_HASH_MISMATCH,
    UPKG_ERR_FINAL_HASH_MISMATCH,
    UPKG_ERR_FLASH_ERASE,
    UPKG_ERR_FLASH_WRITE,
    UPKG_ERR_CRYPTO,               /* криптоблок не віддав підпис квитанції */
    UPKG_ERR_NVS_WRITE
} upkg_status_t;

const char *upkg_strstatus(upkg_status_t status);

/* Заголовок читається з носія байт-у-байт, тому пакований і фіксованого
 * розміру: будь-яка вставка поля ламає підпис усіх випущених пакетів. */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t format_version;
    uint16_t target_hw_id;         /* звіряється з OTP/eFuse плати */
    uint32_t version_monotonic;    /* монотонний номер випуску */
    uint32_t payload_size;         /* байтів корисного навантаження */
    uint32_t chunk_count;
    uint32_t chunk_size;           /* завжди 4096; поле — щоб зловити чужий формат */
    uint8_t  final_sha256[UPKG_HASH_SIZE];  /* хеш усього образу */
    uint8_t  table_sha256[UPKG_HASH_SIZE];  /* хеш таблиці хешів чанків */
    uint8_t  reserved[36];
} upkg_header_t;

_Static_assert(sizeof(upkg_header_t) == UPKG_HEADER_SIZE,
               "заголовок мусить лишатися рівно 128 байтів");

/* Носій із пакетом: FatFS на USB-флешці техніка або буфер потокового
 * шлюзу. Верифікатору байдуже, звідки байти, — він лише просить діапазон. */
typedef struct {
    bool (*read)(void *ctx, uint32_t offset, uint8_t *dst, uint32_t len);
    bool (*write)(void *ctx, uint32_t offset, const uint8_t *src, uint32_t len);
    void *ctx;
} upkg_media_t;

/* Неактивний банк Slot B. Slot A з робочою прошивкою сюди не потрапляє
 * взагалі — саме тому обрив живлення нікого не вбиває. */
typedef struct {
    bool (*erase)(void *ctx, uint32_t offset, uint32_t len);
    bool (*write)(void *ctx, uint32_t offset, const uint8_t *src, uint32_t len);
    bool (*read)(void *ctx, uint32_t offset, uint8_t *dst, uint32_t len);
    void *ctx;
} upkg_flash_t;

/* Криптографія платформи: ROM-функції MCU, апаратний прискорювач або
 * Monocypher у прошивці. Верифікатор своєї арифметики кривих не має. */
typedef struct {
    bool (*verify)(const uint8_t sig[UPKG_SIG_SIZE],
                   const uint8_t pub[UPKG_PUBKEY_SIZE],
                   const uint8_t *msg, size_t len);
    bool (*sign_receipt)(const uint8_t *msg, size_t len,
                         uint8_t sig[UPKG_SIG_SIZE]);
} upkg_crypto_t;

typedef struct {
    uint16_t hw_id;          /* код моделі з OTP */
    uint32_t min_version;    /* поріг із монотонних запобіжників */
    uint32_t device_serial;
    uint8_t  root_public_key[UPKG_PUBKEY_SIZE];  /* із eFuse/Boot ROM */
} upkg_policy_t;

#define UPKG_SLOT_EMPTY          0x00u
#define UPKG_SLOT_PENDING_VERIFY 0xA5u
#define UPKG_SLOT_CONFIRMED      0x5Au

typedef struct __attribute__((packed)) {
    uint32_t staged_version;
    uint8_t  flag;           /* UPKG_SLOT_* */
    uint8_t  boot_retries;
} upkg_boot_state_t;

/* Квитанція аудиту: технік везе її назад у сервіс як доказ того, що саме
 * сталося на цьому пристрої. Підписана ключем самого пристрою. */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t device_serial;
    uint16_t hw_id;
    uint16_t status;         /* upkg_status_t результату */
    uint32_t version;
    uint8_t  image_sha256[UPKG_HASH_SIZE];
    uint8_t  boot_retries;
    uint8_t  reserved[3];
} upkg_receipt_body_t;

typedef struct __attribute__((packed)) {
    upkg_receipt_body_t body;
    uint8_t signature[UPKG_SIG_SIZE];
} upkg_receipt_t;

/* Сесія прошивки. Єдиний буфер сектора на 4 КБ — це вся ціна операції
 * в SRAM: образ на 512 КБ чи 8 МБ у пам'ять не завантажується ніколи. */
typedef struct {
    upkg_policy_t policy;
    upkg_media_t  media;
    upkg_flash_t  flash;
    upkg_crypto_t crypto;
    bool (*nvs_write_state)(void *ctx, const upkg_boot_state_t *state);
    void *nvs_ctx;
    uint8_t chunk_buf[UPKG_CHUNK_SIZE];
} upkg_session_t;

/* Фаза 1: зчитати 128 байтів заголовка і 64 байти підпису за ним. */
upkg_status_t upkg_read_header(upkg_session_t *s, upkg_header_t *hdr,
                               uint8_t sig[UPKG_SIG_SIZE]);

/* Фази 1–2: узгодженість полів, апаратна ціль, відкат, підпис випуску.
 * Flash тут не чіпається жодним байтом. */
upkg_status_t upkg_validate_header(const upkg_session_t *s,
                                   const upkg_header_t *hdr,
                                   const uint8_t sig[UPKG_SIG_SIZE]);

/* Усі чотири фази поспіль. resume == true — продовження після обриву:
 * сектори, що вже збігаються з таблицею, не переписуються.
 * Квитанція заповнюється й за невдачі — з кодом причини. */
upkg_status_t upkg_install(upkg_session_t *s, bool resume,
                           upkg_receipt_t *receipt);

#endif /* UPKG_H */
