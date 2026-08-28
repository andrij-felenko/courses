/* Приклад прив'язки emb_i18n до віджетів LVGL на C99 */
#include "lvgl.h"
#include "emb_i18n.h"

static emb_i18n_ctx_t g_current_locale_ctx;

void ui_update_labels(lv_obj_t *screen) {
    /* Оновлення тексту кнопки збереження */
    const char *save_text = emb_i18n_get(&g_current_locale_ctx, "btn.save");
    lv_label_set_text(ui_btn_save_label, save_text);
    
    /* Форматування та оновлення динамічного лічильника */
    char buf[64];
    int file_count = 5;
    const char *fmt = emb_i18n_get_plural(&g_current_locale_ctx, "storage.deleted", file_count);
    emb_i18n_format_1i(buf, sizeof(buf), fmt, file_count);
    lv_label_set_text(ui_status_label, buf);
    
    /* Автоматичне дзеркалювання для арабської мови / івриту (RTL) */
    if (g_current_locale_ctx.is_rtl) {
        lv_obj_set_style_base_dir(screen, LV_BASE_DIR_RTL, 0);
    } else {
        lv_obj_set_style_base_dir(screen, LV_BASE_DIR_LTR, 0);
    }
}
