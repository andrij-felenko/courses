#include <cstdint>

/* Стан приймача одного байта. Таймер зводить isr() ×16 на біт. */
static struct {
    std::uint8_t  active;      /* чи всередині кадру */
    std::uint8_t  tick;        /* лічильник тіків 0..15 у межах біта */
    std::uint8_t  bit_no;      /* скільки бітів даних уже зібрано */
    std::uint8_t  shifter;     /* тут накопичується байт */
} rx;

extern std::uint8_t line_read();   /* уже після Шмітта й синхронізатора: 0/1 */
extern std::uint8_t majority3(std::uint8_t, std::uint8_t, std::uint8_t);
extern void byte_ready(std::uint8_t);

/* Викликається локальним таймером 16 разів на кожен біт */
void rx_isr() {
    std::uint8_t s = line_read();

    if (!rx.active) {                 /* чекаємо старт-фронт у спокої */
        if (s == 0) {                 /* лінія впала — можливий старт */
            rx.active = 1;
            rx.tick   = 0;
            rx.bit_no = 0;
        }
        return;
    }

    rx.tick++;
    if (rx.tick == 8 && rx.bit_no == 0) {   /* центр старт-біта */
        if (line_read() != 0) {             /* насправді не 0 → хибний старт */
            rx.active = 0;                  /* скинути, чекати знову */
        }
        return;
    }

    if (rx.tick >= 16) {              /* дійшли центру чергового біта даних */
        rx.tick = 0;
        /* голос по центру: три сусідні знімки */
        std::uint8_t b = majority3(line_read(), line_read(), line_read());
        rx.shifter = (rx.shifter >> 1) | (b << 7);   /* молодший біт уперед */
        if (++rx.bit_no == 8) {      /* байт зібрано */
            byte_ready(rx.shifter);  /* віддати користувачеві */
            rx.active = 0;           /* (стоп-біт і перевірку — окремо) */
        }
    }
}
