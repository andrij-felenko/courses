// Низькорівневе зчитування кадру бітів із 74HC165
uint16_t thumbwheel_read_raw_shift_reg(thumbwheel_driver_t *drv) {
    uint16_t raw_data = 0;
    
    // 1. Строб завантаження PL (активний низький)
    gpio_write(drv->config.pin_pl, 0);
    delay_ns(20);
    gpio_write(drv->config.pin_pl, 1);
    
    // 2. Послідовне висування бітів через CLK
    for (int i = 0; i < (drv->config.decades_count * 4); i++) {
        raw_data <<= 1;
        if (gpio_read(drv->config.pin_data)) {
            raw_data |= 0x0001;
        }
        gpio_write(drv->config.pin_clk, 1);
        delay_ns(50);
        gpio_write(drv->config.pin_clk, 0);
        delay_ns(50);
    }
    
    // Інверсія бітів у разі схеми з заземленим COM та pull-up підтяжкою
    if (drv->config.active_low_logic) {
        raw_data = ~raw_data;
    }
    
    return raw_data;
}
