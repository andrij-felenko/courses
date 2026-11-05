// Допоміжна затримка на точну кількість тактів
static inline void delay_cycles(uint32_t cycles) {
    while (cycles--) {
        __asm__ volatile ("nop");
    }
}

// Початкове налаштування ліній інтерфейсу у стан спокою
bitbang_status_t bitbang_init(const bitbang_config_t *config) {
    if (!config || !config->port_bsrr || !config->port_idr) {
        return BITBANG_ERR_INVALID_ARG;
    }
    // Встановлення лінії тактування в низький стан (скидання біта)
    *(config->port_bsrr) = (1UL << (config->pin_sclk + 16));
    // Відпускання лінії даних у високий стан через підтягувальний резистор
    *(config->port_bsrr) = (1UL << config->pin_data);
    return BITBANG_OK;
}

// Повнодуплексна передача байта з прямим керуванням BSRR та зчитуванням IDR
bitbang_status_t bitbang_transfer_byte(const bitbang_config_t *config, uint8_t tx_byte, uint8_t *rx_byte) {
    if (!config || !rx_byte) {
        return BITBANG_ERR_INVALID_ARG;
    }
    uint8_t received = 0;
    const uint32_t sclk_set = (1UL << config->pin_sclk);
    const uint32_t sclk_clr = (1UL << (config->pin_sclk + 16));
    const uint32_t data_set = (1UL << config->pin_data);
    const uint32_t data_clr = (1UL << (config->pin_data + 16));

    for (int i = 7; i >= 0; --i) {
        // 1. Виставлення біта даних: старший біт (MSB) передається першим
        if (tx_byte & (1 << i)) {
            *(config->port_bsrr) = data_set;
        } else {
            *(config->port_bsrr) = data_clr;
        }
        delay_cycles(config->delay_setup);

        // 2. Формування наростаючого фронту такту (перехід 0 -> 1)
        *(config->port_bsrr) = sclk_set;
        delay_cycles(config->delay_half_clk / 2);

        // 3. Стробування вхідного біта на середині тактового імпульсу
        received <<= 1;
        if (*(config->port_idr) & data_set) {
            received |= 1;
        }
        delay_cycles(config->delay_half_clk / 2);

        // 4. Формування спадного фронту такту (перехід 1 -> 0)
        *(config->port_bsrr) = sclk_clr;
        delay_cycles(config->delay_hold);
    }

    *rx_byte = received;
    return BITBANG_OK;
}
