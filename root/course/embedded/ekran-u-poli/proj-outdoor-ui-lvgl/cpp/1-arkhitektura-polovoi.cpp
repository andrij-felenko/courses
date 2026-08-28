#include "lvgl.h"
#include <cstdint>
#include <array>
#include <memory>

namespace field_ui {

enum class ColorMode : uint8_t {
    DayHighContrast = 0,
    NightRed
};

struct Palette {
    lv_color_t background;
    lv_color_t surface;
    lv_color_t text;
    lv_color_t border;
    lv_color_t accent;
    lv_color_t alert;
    lv_color_t safe;
};

class FieldTheme {
public:
    static FieldTheme& instance() {
        static FieldTheme theme;
        return theme;
    }

    void setup(lv_display_t* disp, ColorMode mode = ColorMode::DayHighContrast) {
        display_ = disp;
        setMode(mode);

        lv_theme_set_apply_cb(&theme_, &FieldTheme::applyCallbackThunk);
        lv_theme_set_display(&theme_, disp);
        lv_display_set_theme(disp, &theme_);
    }

    void setMode(ColorMode mode) {
        current_mode_ = mode;
        const auto& p = palettes_[static_cast<size_t>(mode)];

        lv_style_reset(&style_screen_);
        lv_style_init(&style_screen_);
        lv_style_set_bg_color(&style_screen_, p.background);
        lv_style_set_bg_opa(&style_screen_, LV_OPA_COVER);

        lv_style_reset(&style_btn_base_);
        lv_style_init(&style_btn_base_);
        lv_style_set_min_width(&style_btn_base_, 95);
        lv_style_set_min_height(&style_btn_base_, 95);
        lv_style_set_bg_color(&style_btn_base_, p.surface);
        lv_style_set_bg_opa(&style_btn_base_, LV_OPA_COVER);
        lv_style_set_border_color(&style_btn_base_, p.border);
        lv_style_set_border_width(&style_btn_base_, 3);
        lv_style_set_radius(&style_btn_base_, 8);
        lv_style_set_text_color(&style_btn_base_, p.text);
        lv_style_set_pad_all(&style_btn_base_, 14);

        lv_style_reset(&style_btn_focus_);
        lv_style_init(&style_btn_focus_);
        lv_style_set_border_color(&style_btn_focus_, p.accent);
        lv_style_set_border_width(&style_btn_focus_, 6);

        lv_style_reset(&style_btn_press_);
        lv_style_init(&style_btn_press_);
        lv_style_set_bg_color(&style_btn_press_, p.accent);
        lv_style_set_text_color(&style_btn_press_, p.background);

        if (display_) {
            lv_obj_report_style_change(&style_screen_);
            lv_obj_report_style_change(&style_btn_base_);
        }
    }

    [[nodiscard]] const Palette& currentPalette() const noexcept {
        return palettes_[static_cast<size_t>(current_mode_)];
    }

private:
    FieldTheme() = default;

    static void applyCallbackThunk(lv_theme_t* th, lv_obj_t* obj) {
        auto& self = instance();
        if (lv_obj_check_type(obj, &lv_btn_class)) {
            lv_obj_add_style(obj, &self.style_btn_base_, LV_STATE_DEFAULT);
            lv_obj_add_style(obj, &self.style_btn_focus_, LV_STATE_FOCUSED);
            lv_obj_add_style(obj, &self.style_btn_press_, LV_STATE_PRESSED);
        } else if (lv_obj_check_type(obj, &lv_screen_class) || lv_obj_get_parent(obj) == nullptr) {
            lv_obj_add_style(obj, &self.style_screen_, LV_STATE_DEFAULT);
        }
    }

    lv_display_t* display_{nullptr};
    ColorMode current_mode_{ColorMode::DayHighContrast};
    lv_theme_t theme_{};

    lv_style_t style_screen_{};
    lv_style_t style_btn_base_{};
    lv_style_t style_btn_focus_{};
    lv_style_t style_btn_press_{};

    static constexpr std::array<Palette, 2> palettes_{{
        // Day High Contrast
        Palette{
            .background = { .blue = 0x00, .green = 0x00, .red = 0x00 },
            .surface    = { .blue = 0x1E, .green = 0x1C, .red = 0x1C },
            .text       = { .blue = 0xFF, .green = 0xFF, .red = 0xFF },
            .border     = { .blue = 0xFF, .green = 0xFF, .red = 0xFF },
            .accent     = { .blue = 0x00, .green = 0xD7, .red = 0xFF },
            .alert      = { .blue = 0x55, .green = 0x2D, .red = 0xFF },
            .safe       = { .blue = 0x59, .green = 0xC7, .red = 0x34 }
        },
        // Night Red
        Palette{
            .background = { .blue = 0x00, .green = 0x00, .red = 0x00 },
            .surface    = { .blue = 0x00, .green = 0x00, .red = 0x20 },
            .text       = { .blue = 0x30, .green = 0x3B, .red = 0xFF },
            .border     = { .blue = 0x00, .green = 0x00, .red = 0x8B },
            .accent     = { .blue = 0x3A, .green = 0x45, .red = 0xFF },
            .alert      = { .blue = 0x00, .green = 0x00, .red = 0xFF },
            .safe       = { .blue = 0x1B, .green = 0x1B, .red = 0x99 }
        }
    }};
};

} // namespace field_ui
