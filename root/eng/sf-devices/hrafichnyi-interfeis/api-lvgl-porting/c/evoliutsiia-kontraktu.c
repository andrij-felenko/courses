/* Створення та налаштування дисплея в LVGL v9 */
lv_display_t *disp = lv_display_create(320, 240);

/* Встановлення буферів рендерингу та режиму */
lv_display_set_buffers(disp, buf1, buf2, sizeof(buf1), LV_DISPLAY_RENDER_MODE_PARTIAL);

/* Прив'язка функції скидання */
lv_display_set_flush_cb(disp, my_flush_cb_v9);

/* Сигнатура зворотного виклику v9 */
void my_flush_cb_v9(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    /* Запуск передачі даних */
    my_lcd_send_dma(area, px_map);

    /* Інформування рушія */
    lv_display_flush_ready(disp);
}
