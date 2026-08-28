/* Ініціалізація неперекривного статусного бару в LVGL (C) */
void init_sticky_status_bar(void) {
    /* Створюємо контейнер на системному верхньому шарі */
    lv_obj_t *status_bar = lv_obj_create(lv_layer_top());
    lv_obj_set_size(status_bar, LV_PCT(100), STATUS_BAR_HEIGHT);
    lv_obj_set_pos(status_bar, 0, 0);
    
    /* Забороняємо перехоплення подій кліків фоном (кліки проходять крізь порожні зони) */
    lv_obj_clear_flag(status_bar, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    
    /* Фіксований чорний напівпрозорий фон для максимального контрасту */
    lv_obj_set_style_bg_color(status_bar, lv_color_hex(0x101418), 0);
    lv_obj_set_style_bg_opa(status_bar, LV_OPA_90, 0);
    lv_obj_set_style_border_side(status_bar, LV_BORDER_SIDE_BOTTOM, 0);
    lv_obj_set_style_border_width(status_bar, 2, 0);
    lv_obj_set_style_border_color(status_bar, lv_color_hex(0x27ae60), 0);
}
