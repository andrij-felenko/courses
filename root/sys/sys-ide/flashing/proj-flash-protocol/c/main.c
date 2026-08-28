#include <stdint.h>
#include <stddef.h>

#define SLIP_END     0xC0   // межа кадру
#define SLIP_ESC     0xDB   // початок екран-послідовності
#define SLIP_ESC_END 0xDC   // пара 0xDB 0xDC означає байт даних 0xC0
#define SLIP_ESC_ESC 0xDD   // пара 0xDB 0xDD означає байт даних 0xDB

// Обгорнути payload у SLIP-кадр. Буфер out мусить мати запас на 2*len + 2
// байти (кожен байт у гіршому разі подвоюється, плюс дві межі).
// Повертає фактичну довжину готового кадру.
size_t slip_encode(const uint8_t *payload, size_t len, uint8_t *out) {
    uint8_t *p = out;
    *p++ = SLIP_END;                     // відкриваємо кадр
    for (size_t i = 0; i < len; i++) {
        switch (payload[i]) {
            case SLIP_END:               // 0xC0 у даних →
                *p++ = SLIP_ESC;         //   0xDB
                *p++ = SLIP_ESC_END;     //   0xDC
                break;
            case SLIP_ESC:               // 0xDB у даних →
                *p++ = SLIP_ESC;         //   0xDB
                *p++ = SLIP_ESC_ESC;     //   0xDD
                break;
            default:
                *p++ = payload[i];       // звичайний байт — як є
        }
    }
    *p++ = SLIP_END;                     // закриваємо кадр
    return (size_t)(p - out);
}
