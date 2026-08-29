#ifndef ATT_REASSEMBLY_H
#define ATT_REASSEMBLY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Збирання довгих записів ATT.
 *
 * Базовий MTU — 23 байти, з них 3 з'їдає заголовок (Opcode + Attribute Handle),
 * тож на корисне навантаження лишається 20. Ключ X25519 — уже 32 байти, пакет
 * конфігурації — 80–120. Два виходи, і потрібні обидва: узгодити більший MTU,
 * а коли клієнт цього не вміє — зібрати значення з Prepare Write Request.
 */

#define ATT_MTU_DEFAULT     23
#define ATT_MTU_MAX         256
#define ATT_HEADER_SIZE     3
#define ATT_REASM_CAPACITY  256

/* Коди помилок ATT (Bluetooth Core, Vol 3, Part F, 3.4.1.1). */
#define ATT_ERR_NONE                  0x00
#define ATT_ERR_INVALID_OFFSET        0x07
#define ATT_ERR_PREPARE_QUEUE_FULL    0x09
#define ATT_ERR_INVALID_ATTR_LEN      0x0D
#define ATT_ERR_UNLIKELY              0x0E

typedef struct {
    uint8_t  buffer[ATT_REASM_CAPACITY];
    uint16_t length;
    uint16_t char_uuid;   /* атрибут, для якого відкрито чергу */
    bool     active;
} att_reasm_t;

/* Відповідь на ATT_EXCHANGE_MTU_REQ: беремо менше з двох стель. */
uint16_t att_mtu_negotiate(uint16_t client_mtu);

/* Скільки байтів корисного навантаження влазить у кадр. */
uint16_t att_mtu_payload(uint16_t mtu);

void att_reasm_cancel(att_reasm_t *r);

/* Черговий Prepare Write Request. Повертає код помилки ATT (0 — прийнято). */
uint8_t att_reasm_prepare(att_reasm_t *r, uint16_t char_uuid, uint16_t offset,
                          const uint8_t *value, size_t len);

/*
 * Execute Write Request. commit == false — клієнт скасував чергу.
 * За успіху віддає зібране значення; воно живе в буфері до наступного prepare.
 */
uint8_t att_reasm_execute(att_reasm_t *r, bool commit,
                          uint16_t *out_uuid, const uint8_t **out_value, size_t *out_len);

#endif /* ATT_REASSEMBLY_H */
