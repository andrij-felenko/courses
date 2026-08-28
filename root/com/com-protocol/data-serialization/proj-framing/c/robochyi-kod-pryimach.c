#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define FLAG   0x7E     // межа кадру (прапорець HDLC/PPP)
#define ESC    0x7D     // байт екранування
#define XOR    0x20     // маска перекручування екранованого байта
#define MAX_FRAME 64    // стеля тіла кадру — рівно стільки ОЗП відводимо

typedef enum { ST_WAIT, ST_DATA, ST_ESC } rx_state_t;

typedef struct {
    rx_state_t state;
    uint8_t    buf[MAX_FRAME];
    size_t     len;                 // скільки байтів уже в buf
} frame_rx_t;

void frame_rx_init(frame_rx_t *rx) {
    rx->state = ST_WAIT;
    rx->len   = 0;
}

// оголошення нижче: перевірка й видача готового кадру (реалізація — далі)
static void frame_complete(frame_rx_t *rx);

// згодувати один прийнятий байт; викликати на кожен октет з UART
void frame_rx_byte(frame_rx_t *rx, uint8_t b) {
    switch (rx->state) {

    case ST_WAIT:                          // шукаємо початок кадру
        if (b == FLAG) {                   // знайшли межу — відкриваємо кадр
            rx->len   = 0;
            rx->state = ST_DATA;
        }
        // будь-що інше — сміття, мовчки викидаємо (ресинхронізація)
        break;

    case ST_DATA:
        if (b == FLAG) {                   // межа: кадр скінчився
            frame_complete(rx);            // звірити CRC й, якщо ок, віддати
            rx->len   = 0;                 // готуємось до наступного кадру
            rx->state = ST_WAIT;
        } else if (b == ESC) {             // далі — екранований байт
            rx->state = ST_ESC;
        } else {                           // звичайний байт даних
            if (rx->len < MAX_FRAME) {
                rx->buf[rx->len++] = b;
            } else {
                rx->state = ST_WAIT;       // ПЕРЕПОВНЕННЯ: скидаємо кадр
                rx->len   = 0;             // (а не пишемо за межі buf!)
            }
        }
        break;

    case ST_ESC:                           // попередній байт був ESC
        if (b == FLAG) {                   // ESC перед межею — кадр порваний
            rx->state = ST_WAIT;           // відкидаємо, чекаємо нового
            rx->len   = 0;
        } else {
            uint8_t d = b ^ XOR;           // перекрутити назад: 0x5E→0x7E, 0x5D→0x7D
            if (rx->len < MAX_FRAME) {
                rx->buf[rx->len++] = d;
                rx->state = ST_DATA;       // повертаємось у тіло кадру
            } else {
                rx->state = ST_WAIT;       // переповнення й тут
                rx->len   = 0;
            }
        }
        break;
    }
}
