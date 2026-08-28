#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Визначення чотирьох стандартних режимів Motorola SPI */
typedef enum {
    SPI_MODE_0 = 0, /* CPOL = 0, CPHA = 0 */
    SPI_MODE_1 = 1, /* CPOL = 0, CPHA = 1 */
    SPI_MODE_2 = 2, /* CPOL = 1, CPHA = 0 */
    SPI_MODE_3 = 3  /* CPOL = 1, CPHA = 1 */
} spi_bb_mode_t;

/* Структура конфігурації та апаратних функцій зворотного виклику */
typedef struct {
    void (*set_sclk)(bool level);
    void (*set_mosi)(bool level);
    bool (*get_miso)(void);
    void (*set_cs)(bool level);
    void (*delay_ns)(uint32_t ns);
    spi_bb_mode_t mode;
    uint32_t half_period_ns;
} spi_bitbang_t;

/* Ініціалізація виводів у стан спокою відповідно до обраного режиму */
void spi_bb_init(const spi_bitbang_t *bus) {
    bool cpol = (bus->mode == SPI_MODE_2 || bus->mode == SPI_MODE_3);
    bus->set_cs(true);          /* Неактивний рівень Chip Select (HIGH) */
    bus->set_sclk(cpol);        /* Рівень спокою SCLK згідно з CPOL */
    bus->set_mosi(false);
}

/* Повний дуплексний обмін одним байтом */
uint8_t spi_bb_transfer_byte(const spi_bitbang_t *bus, uint8_t byte_out) {
    bool cpol = (bus->mode == SPI_MODE_2 || bus->mode == SPI_MODE_3);
    bool cpha = (bus->mode == SPI_MODE_1 || bus->mode == SPI_MODE_3);
    uint8_t byte_in = 0;

    for (uint8_t bit = 0; bit < 8; ++bit) {
        bool out_bit = (byte_out & (1 << (7 - bit))) != 0;

        if (!cpha) {
            /* CPHA = 0: встановлення біта ПЕРЕД 1-м фронтом */
            bus->set_mosi(out_bit);
            bus->delay_ns(bus->half_period_ns);

            /* 1-й фронт: перехід у стан !CPOL (строб вибірки) */
            bus->set_sclk(!cpol);
            bus->delay_ns(bus->half_period_ns);

            /* Зчитування стабільного біта на 1-му фронті */
            if (bus->get_miso()) {
                byte_in |= (1 << (7 - bit));
            }

            /* 2-й фронт: повернення у стан CPOL (підготовка наступного біта) */
            bus->set_sclk(cpol);
        } else {
            /* CPHA = 1: 1-й фронт такту змінює стан лінії */
            bus->set_sclk(!cpol);
            bus->set_mosi(out_bit);
            bus->delay_ns(bus->half_period_ns);

            /* 2-й фронт: повернення у стан CPOL (строб вибірки) */
            bus->set_sclk(cpol);
            bus->delay_ns(bus->half_period_ns);

            /* Зчитування стабільного біта на 2-му фронті */
            if (bus->get_miso()) {
                byte_in |= (1 << (7 - bit));
            }
        }
    }

    return byte_in;
}

/* Потокова передача масиву байтів із контролем лінії /CS */
void spi_bb_transfer_buffer(const spi_bitbang_t *bus, 
                            const uint8_t *tx_buf, 
                            uint8_t *rx_buf, 
                            size_t length) {
    bus->set_cs(false); /* Активація веденого (LOW) */
    bus->delay_ns(bus->half_period_ns); /* Захисний інтервал t_CSS */

    for (size_t i = 0; i < length; ++i) {
        uint8_t out_val = tx_buf ? tx_buf[i] : 0xFF;
        uint8_t in_val = spi_bb_transfer_byte(bus, out_val);
        if (rx_buf) {
            rx_buf[i] = in_val;
        }
    }

    bus->delay_ns(bus->half_period_ns); /* Захисний інтервал t_CSH */
    bus->set_cs(true);  /* Деактивація веденого (HIGH) */
}
