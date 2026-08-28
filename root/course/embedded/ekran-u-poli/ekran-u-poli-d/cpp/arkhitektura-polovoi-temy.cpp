#include "lvgl.h"
#include <cstdint>
#include <concepts>

namespace field_ui {

/* Типобезпечні константи польової палітри */
struct Palette {
    static constexpr lv_color_t Background = { .blue = 0x00, .green = 0x00, .red = 0x00 };
    static constexpr lv_color_t Foreground = { .blue = 0xFF, .green = 0xFF, .red = 0xFF };
    static constexpr lv_color_t Accent     = { .blue = 0x00, .green = 0xD7, .red = 0xFF }; // #FFD700
    static constexpr lv_color_t Alert      = { .blue = 0x00, .green = 0x00, .red = 0xFF };
    static constexpr lv_color_t Safe       = { .blue = 0x00, .green = 0xFF, .red = 0x00 };
};

/* Метрики елементів керування за стандартом тактильної ергономіки */
struct Metrics {
    static constexpr int32_t MinTargetWidth  = 95; // 15 мм при 160 DPI
    static constexpr int32_t MinTargetHeight = 95; // 15 мм при 160 DPI
    static constexpr int32_t SeparationGap   = 25; // 4 мм захисний зазор
    static constexpr int32_t BorderThickness = 3;
    static constexpr int32_t FocusBorder     = 5;
    static constexpr int32_t CornerRadius    = 8;
};

class ThemeEngine {
public:
    static ThemeEngine& instance() {
        static ThemeEngine engine;
        return engine;
    }

    void initialize() {
        if (initialized_) return;

        lv_style_init(&base_btn_style_);
        lv_style_set_min_width(&base_btn_style_, Metrics::MinTargetWidth);
        lv_style_set_min_height(&base_btn_style_, Metrics::MinTargetHeight);
        lv_style_set_bg_color(&base_btn_style_, lv_color_hex(0x1A1A1A));
        lv_style_set_bg_opa(&base_btn_style_, LV_OPA_COVER);
        lv_style_set_border_color(&base_btn_style_, Palette::Foreground);
        lv_style_set_border_width(&base_btn_style_, Metrics::BorderThickness);
        lv_style_set_radius(&base_btn_style_, Metrics::CornerRadius);
        lv_style_set_text_color(&base_btn_style_, Palette::Foreground);
        lv_style_set_pad_all(&base_btn_style_, 12);

        lv_style_init(&focused_style_);
        lv_style_set_border_color(&focused_style_, Palette::Accent);
        lv_style_set_border_width(&focused_style_, Metrics::FocusBorder);

        lv_style_init(&pressed_style_);
        lv_style_set_bg_color(&pressed_style_, Palette::Accent);
        lv_style_set_text_color(&pressed_style_, Palette::Background);

        initialized_ = true;
    }

    void styleButton(lv_obj_t* btn) const {
        lv_obj_add_style(btn, &base_btn_style_, LV_STATE_DEFAULT);
        lv_obj_add_style(btn, &focused_style_, LV_STATE_FOCUSED);
        lv_obj_add_style(btn, &pressed_style_, LV_STATE_PRESSED);
    }

private:
    ThemeEngine() = default;
    bool initialized_{false};
    lv_style_t base_btn_style_{};
    lv_style_t focused_style_{};
    lv_style_t pressed_style_{};
};

} // namespace field_ui
