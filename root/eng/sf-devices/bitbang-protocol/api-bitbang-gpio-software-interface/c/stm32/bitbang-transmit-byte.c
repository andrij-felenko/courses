void bitbang_transmit_byte(BitBangContext* ctx, uint8_t data) {
    for (int i = 0; i < 8; i++) {
        // Виставляємо біт даних (починаючи зі старшого)
        if (data & (1 << (7 - i))) {
            ctx->sda_port->BSRR = ctx->sda_pin; // Встановити в 1
        } else {
            ctx->sda_port->BRR = ctx->sda_pin;  // Скинути в 0
        }
        
        // Формуємо тактовий імпульс
        bitbang_delay_us(ctx->delay_half_period);
        ctx->scl_port->BSRR = ctx->scl_pin; // SCL = 1
        bitbang_delay_us(ctx->delay_half_period);
        ctx->scl_port->BRR = ctx->scl_pin;  // SCL = 0
    }
}
