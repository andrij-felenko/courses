#ifndef LINK_H
#define LINK_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Формат кадру в лінії:
//
//   COBS( [seq:1] [payload:0..LINK_MAX_PAYLOAD] [CRC-16:2, старший байт перший] ) [0x00]
//
// Байт 0x00 не трапляється всередині COBS-тіла, тож він і тільки він означає межу кадру.
// Квитанція (ACK) — це кадр із ПОРОЖНІМ навантаженням: поле seq несе номер, який квитують.

#define LINK_MAX_PAYLOAD 64U
#define LINK_SEQ_SIZE    1U
#define LINK_CRC_SIZE    2U
#define LINK_MAX_FRAME   (LINK_SEQ_SIZE + LINK_MAX_PAYLOAD + LINK_CRC_SIZE)

// COBS додає один байт на кожні 254 байти плюс стартовий код; ще один байт — роздільник.
#define LINK_MAX_WIRE  (LINK_MAX_FRAME + LINK_MAX_FRAME / 254U + 2U)
#define LINK_DELIMITER 0x00U

// Простір номерів 8-бітний, S = 256. Для Selective Repeat потрібно S >= 2*W,
// а для індексації слотів через (seq % LINK_WINDOW) — щоб S ділилося на W націло.
#define LINK_WINDOW 8U

typedef enum {
    LINK_OK = 0,
    LINK_PENDING,           // кадр ще не зібрано, чекаємо байтів
    LINK_ERR_TOO_LONG,      // навантаження більше за LINK_MAX_PAYLOAD
    LINK_ERR_NO_SPACE,      // не влізло у виданий буфер
    LINK_ERR_COBS,          // структурно пошкоджене COBS-тіло
    LINK_ERR_CRC,           // остача CRC ненульова — кадр побив шум
    LINK_ERR_SHORT_FRAME,   // кадр коротший за службовий мінімум
    LINK_ERR_OVERFLOW,      // роздільник не прийшов, буфер прийому переповнено
    LINK_ERR_WINDOW_FULL,   // усі неквитовані слоти зайняті
    LINK_ERR_LINK_DOWN      // вичерпано ліміт повторів
} link_status_t;

// Віддає готові байти у фізичний інтерфейс (UART, RS-485, радіомодуль).
typedef void (*link_write_fn)(const uint8_t *bytes, size_t len, void *ctx);

// Різниця номерів у кільцевому просторі 0..255.
static inline uint8_t link_seq_diff(uint8_t a, uint8_t b) {
    return (uint8_t)(a - b);
}

// Чи номер a попереду b (у межах півкола простору номерів).
static inline bool link_seq_after(uint8_t a, uint8_t b) {
    uint8_t d = link_seq_diff(a, b);
    return d != 0U && d < 128U;
}

static inline const char *link_status_str(link_status_t st) {
    switch (st) {
        case LINK_OK:               return "ок";
        case LINK_PENDING:          return "кадр не зібрано";
        case LINK_ERR_TOO_LONG:     return "навантаження задовге";
        case LINK_ERR_NO_SPACE:     return "малий буфер";
        case LINK_ERR_COBS:         return "пошкоджений COBS";
        case LINK_ERR_CRC:          return "не збіглася CRC";
        case LINK_ERR_SHORT_FRAME:  return "надто короткий кадр";
        case LINK_ERR_OVERFLOW:     return "переповнення прийому";
        case LINK_ERR_WINDOW_FULL:  return "вікно заповнене";
        case LINK_ERR_LINK_DOWN:    return "лінія розірвана";
        default:                    return "невідомо";
    }
}

#endif // LINK_H
