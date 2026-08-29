/* Розбір кадру протоколу — робота НИЖНЬОЇ половини.
 *
 * Формат кадру: 0x7E | довжина (1 байт, 1..64) | тіло | CRC-8.
 * Парсер побайтовий і без стану поза структурою, тож фонове завдання
 * годує його рівно тим, що встиг накидати в кільце обробник.
 */
#ifndef FRAME_PARSER_H
#define FRAME_PARSER_H

#include <stdbool.h>
#include <stdint.h>

#define FRAME_SOF 0x7Eu
#define FRAME_MAX_PAYLOAD 64u

typedef enum {
    FRAME_WAIT_SOF = 0,
    FRAME_WAIT_LEN,
    FRAME_WAIT_BODY,
    FRAME_WAIT_CRC
} frame_state_t;

typedef struct {
    frame_state_t state;
    uint8_t payload[FRAME_MAX_PAYLOAD];
    uint8_t expected; /* скільки байтів тіла ще чекаємо */
    uint8_t filled;   /* скільки байтів тіла вже лежить */
    uint8_t crc;      /* CRC, накопичена по довжині й тілу */

    /* Діагностика: чому кадри не доходять */
    uint32_t frames_ok;
    uint32_t crc_errors;
    uint32_t length_errors;
} frame_parser_t;

void frame_parser_init(frame_parser_t *p);

/* Згодовує один байт. Повертає true, коли щойно зібрано цілий кадр:
 * тіло лежить у p->payload, довжина — у *out_len. */
bool frame_parser_feed(frame_parser_t *p, uint8_t byte, uint8_t *out_len);

#endif /* FRAME_PARSER_H */
