#ifndef AUTH_FRAME_H
#define AUTH_FRAME_H

#include <stddef.h>
#include "auth_protocol.h"

/* Заголовок на дроті — 20 байтів; корисне навантаження арбітражу коротке,
   найбільша структура — msg_stick_check_t (9 байтів). Запас на 64 байти. */
#define AUTH_HEADER_SIZE  20u
#define AUTH_MAX_PAYLOAD  64u
#define AUTH_MAX_FRAME    (AUTH_HEADER_SIZE + AUTH_MAX_PAYLOAD)

/* CRC16-CCITT, поліном 0x1021. seed дозволяє рахувати суму двома шматками:
   спершу заголовок без поля crc, далі корисне навантаження. */
uint16_t auth_crc16_ccitt(const uint8_t *data, size_t len, uint16_t seed);

/* Складає кадр у out. magic, version, payload_len і crc16 виставляє сама
   функція; решту полів бере з hdr. Повертає довжину кадру або -1. */
int auth_frame_encode(uint8_t *out, size_t cap,
                      const auth_header_t *hdr,
                      const void *payload, size_t payload_len);

/* Розбирає кадр: перевіряє магію, версію, узгодженість довжин і CRC.
   *payload вказує всередину frame — живе рівно стільки, скільки буфер. */
auth_status_code_t auth_frame_decode(const uint8_t *frame, size_t len,
                                     auth_header_t *out, const uint8_t **payload);

/* Пошук межі кадру в потоці послідовного порту: зміщення першого байта,
   з якого може починатися кадр, або -1. */
long auth_frame_sync(const uint8_t *buf, size_t len);

/* Сурогат підпису командирського кадру: детермінована згортка спільного
   ключа з полями, які неможливо повторити (seq і час відправника).
   У бойовій системі тут HMAC-SHA256 за схемою підпису MAVLink v2. */
uint32_t auth_sign_override(uint32_t key, uint8_t src, uint16_t seq, uint32_t ts);

#endif /* AUTH_FRAME_H */
