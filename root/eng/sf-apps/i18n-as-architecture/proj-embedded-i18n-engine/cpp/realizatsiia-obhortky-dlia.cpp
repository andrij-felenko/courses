// Приклад прив'язки Engine до віджетів LVGL на C++20
#include "lvgl.h"
#include "emb_i18n.hpp"

void ui_update_labels_cpp(lv_obj_t *screen, const embedded::i18n::Engine &engine) {
    std::string_view save_text = engine.get("btn.save");
    lv_label_set_text(ui_btn_save_label, save_text.data());
    
    embedded::i18n::StaticBuffer<64> buf;
    int file_count = 5;
    std::string_view fmt = engine.get_plural("storage.deleted", file_count);
    buf.format_1i(fmt, file_count);
    lv_label_set_text(ui_status_label, buf.c_str());
    
    if (engine.is_rtl()) {
        lv_obj_set_style_base_dir(screen, LV_BASE_DIR_RTL, 0);
    } else {
        lv_obj_set_style_base_dir(screen, LV_BASE_DIR_LTR, 0);
    }
}
