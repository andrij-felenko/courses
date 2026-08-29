/* Драйвер крипточипа ATECC608A/B: пробудження, підпис ECDSA P-256, сон.
 * Апаратний рівень схований за трьома зворотними викликами — запис, читання,
 * затримка, — тож той самий код працює і на мікроконтролері, і на Linux. */
#ifndef ATECC608_H
#define ATECC608_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* 7-бітна адреса за замовчуванням; на шині дає байт запису 0xC0 і читання 0xC1.
 * Заводські партії трапляються і з 0x58 — адреса живе в зоні конфігурації. */
#define ATECC_ADDR_DEFAULT 0x60u

/* Довжини, зафіксовані форматом команди Sign над зовнішнім дайджестом. */
#define ATECC_DIGEST_LEN    32u
#define ATECC_SIGNATURE_LEN 64u

typedef enum {
    ATECC_OK = 0,
    ATECC_ERR_IO,         /* шина не віддала/не прийняла байти */
    ATECC_ERR_CRC,        /* CRC16 відповіді не збіглася */
    ATECC_ERR_TIMEOUT,    /* чип не відповів у межах часу виконання */
    ATECC_ERR_PROTOCOL,   /* довжина пакета не та, що обіцяє формат */
    ATECC_ERR_DEVICE,     /* чип повернув статус-пакет із кодом помилки */
    ATECC_ERR_NOT_LOCKED, /* зони пам'яті ще не заблоковані на виробництві */
    ATECC_ERR_ARG
} atecc_err;

/* Апаратний рівень. Усі три виклики синхронні; write/read повертають false,
 * коли пристрій не підтвердив адресу (NACK) — для драйвера це не завжди
 * помилка: саме так чип каже «обчислення ще триває». */
typedef struct {
    bool (*write)(void *ctx, uint8_t addr7, const uint8_t *buf, size_t len);
    bool (*read)(void *ctx, uint8_t addr7, uint8_t *buf, size_t len);
    void (*delay_ms)(void *ctx, uint32_t ms);
    void *ctx;
} atecc_hal;

typedef struct {
    atecc_hal hal;
    uint8_t addr7;
    bool awake;    /* чи ми в межах вікна сторожового таймера (1.7 с) */
    uint8_t status; /* останній статус-байт від чипа */
} atecc_dev;

void atecc_init(atecc_dev *dev, const atecc_hal *hal, uint8_t addr7);

/* Імпульс пробудження + перевірка 4-байтового слова готовності 04 11 33 43. */
atecc_err atecc_wake(atecc_dev *dev);

/* Переведення в глибокий сон (менше 150 нА). Викликати обов'язково: інакше
 * чип тримає генератор увімкненим до спрацювання сторожового таймера. */
void atecc_sleep(atecc_dev *dev);

/* Підпис зовнішнього 32-байтового дайджеста ключем зі слота slot (0..15).
 * Повертає 64 байти: 32 байти R, далі 32 байти S. */
atecc_err atecc_sign_digest(atecc_dev *dev, uint8_t slot,
                            const uint8_t digest[ATECC_DIGEST_LEN],
                            uint8_t signature[ATECC_SIGNATURE_LEN]);

/* Стан блокування зон: доки конфігурація не заблокована, чип відхиляє Sign. */
atecc_err atecc_lock_state(atecc_dev *dev, bool *config_locked, bool *data_locked);

const char *atecc_strerror(atecc_err err);
const char *atecc_status_str(uint8_t status);

/* CRC16-CCITT із поліномом 0x8005 і нульовим початковим значенням —
 * той самий розрахунок, що й усередині чипа. Винесено в заголовок,
 * бо ним же перевіряють слово пробудження. */
uint16_t atecc_crc16(const uint8_t *data, size_t len);

#endif /* ATECC608_H */
