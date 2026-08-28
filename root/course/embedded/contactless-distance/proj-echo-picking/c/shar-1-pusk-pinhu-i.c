#include <stdint.h>

#define PING_CYCLES   8        // скільки періодів 40 кГц ударити в пластину
#define BLANK_US      500      // перечекати власний дзвін (сліпа зона ~8 см)

// Ударити пластину пачкою імпульсів 40 кГц (генерує сам таймер/ШІМ).
extern void      drive_transducer(uint8_t cycles);
extern uint32_t  micros(void);      // мікросекундний лічильник
extern uint16_t  adc_read(void);    // миттєва амплітуда обвідної, 0..4095

// Пустити пінг і повернути мить t0 — від неї рахуємо весь час польоту.
static uint32_t send_ping(void) {
    drive_transducer(PING_CYCLES);
    uint32_t t0 = micros();               // нуль відліку часу польоту
    while ((micros() - t0) < BLANK_US) {
        /* глуха зона: пластина ще дзвенить, слухати марно */
    }
    return t0;
}
