disp_status_t panel_start(const init_cmd_t *tab, uint32_t n, int tries) {
    for (int t = 0; t < tries; t++) {
        hw_reset();
        if (run_init_table_checked(tab, n) == DISP_OK) {
            return DISP_OK;
        }
        delay_ms(50);
    }
    return DISP_ERR_BUS;
}

// ST7789:
panel_start(st7789_table, sizeof(st7789_table)/sizeof(st7789_table[0]), 3);
// ILI9341 — той самий виклик, інша таблиця:
panel_start(ili9341_table, sizeof(ili9341_table)/sizeof(ili9341_table[0]), 3);
