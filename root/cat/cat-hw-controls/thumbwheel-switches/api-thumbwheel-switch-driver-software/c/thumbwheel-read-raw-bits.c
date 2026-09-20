uint32_t thumbwheel_read_raw_bits(const thumbwheel_config_t *cfg) {
    uint32_t raw_data = 0;
    
    // 1. Защеплення паралельних даних BCD у зсувний регістр (строб PL)
    hal_gpio_write_pin(cfg->pin_pl, 0);
    hal_delay_us(1); // Гарантований такт засувки Parallel Load
    hal_gpio_write_pin(cfg->pin_pl, 1);
    
    // 2. Послідовне вичитування бітів зсувом через лінії CLK та DATA
    uint8_t total_bits = cfg->num_decades * 4;
    for (uint8_t i = 0; i < total_bits; i++) {
        // Зчитування поточного біта з виходу Q7
        uint8_t bit_val = hal_gpio_read_pin(cfg->pin_data);
        raw_data |= ((uint32_t)(bit_val & 0x01) << (total_bits - 1 - i));
        
        // Тактовий імпульс CLK (наростаючий фронт здійснює зсув на 1 біт)
        hal_gpio_write_pin(cfg->pin_clk, 1);
        hal_delay_us(1);
        hal_gpio_write_pin(cfg->pin_clk, 0);
        hal_delay_us(1);
    }
    
    return raw_data;
}
