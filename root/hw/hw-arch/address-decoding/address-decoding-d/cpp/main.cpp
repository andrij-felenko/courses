#include <cstdint>

// «Прошитий» у дешифратор номер вікна: старші 4 біти мусять бути 1100.
// Молодші 12 бітів НЕ перевіряємо — це й є неповна дешифрація.
static inline bool cs_led_port(uint16_t addr) {
    return (addr >> 12) == 0xC;        // збіг A15..A12 == 1100
}

static volatile uint8_t led_latch;     // регістр світлодіодів (реальне залізо)

// Один такт шини: дешифрація + дія обраного пристрою.
void bus_cycle(uint16_t addr, bool is_write, uint8_t data) {
    if (cs_led_port(addr)) {           // ~CS порту активний?
        if (is_write)                  // напрям задають ~RD/~WR
            led_latch = data;          // запис у вікні -> оновити світлодіоди
    }
    // інші пристрої тут перевіряли б свої cs_*(addr) — і озвався б рівно один
}
