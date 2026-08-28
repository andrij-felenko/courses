#include <stdint.h>
#include <stdbool.h>

/* Стан програмного веденого вузла */
typedef struct {
    uint8_t tx_byte;
    uint8_t rx_byte;
    uint8_t bit_index;
    bool cpol;
    bool cpha;
    void (*set_miso)(bool level);
    bool (*get_mosi)(void);
} spi_slave_bb_t;

/* Обробник спадного перепаду лінії /CS */
void spi_slave_cs_fall_isr(spi_slave_bb_t *slave) {
    slave->bit_index = 0;
    slave->rx_byte = 0;

    /* Для CPHA=0 виставляємо старший біт D7 одразу по спаду CS */
    if (!slave->cpha) {
        bool out_bit = (slave->tx_byte & (1 << 7)) != 0;
        slave->set_miso(out_bit);
    }
}

/* Обробник тактового фронту SCLK */
void spi_slave_sclk_edge_isr(spi_slave_bb_t *slave, bool is_leading_edge) {
    if (!slave->cpha) {
        if (is_leading_edge) {
            /* 1-й фронт: вибірка з лінії MOSI */
            if (slave->get_mosi()) {
                slave->rx_byte |= (1 << (7 - slave->bit_index));
            }
        } else {
            /* 2-й фронт: виставлення наступного біта */
            slave->bit_index++;
            if (slave->bit_index < 8) {
                bool out_bit = (slave->tx_byte & (1 << (7 - slave->bit_index))) != 0;
                slave->set_miso(out_bit);
            }
        }
    } else {
        if (is_leading_edge) {
            /* 1-й фронт: виставлення чергового біта */
            bool out_bit = (slave->tx_byte & (1 << (7 - slave->bit_index))) != 0;
            slave->set_miso(out_bit);
        } else {
            /* 2-й фронт: вибірка з лінії MOSI */
            if (slave->get_mosi()) {
                slave->rx_byte |= (1 << (7 - slave->bit_index));
            }
            slave->bit_index++;
        }
    }
}
