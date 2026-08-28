/* Ініціалізація неперекривного статусного бару в LVGL (C++ RAII-обгортка) */
namespace gcs::ui {

class StickyStatusBarWidget {
public:
    explicit StickyStatusBarWidget(int32_t height = 28) noexcept {
        container_ = lv_obj_create(lv_layer_top());
        if (!container_) return;

        lv_obj_set_size(container_, LV_PCT(100), height);
        lv_obj_set_pos(container_, 0, 0);
        lv_obj_clear_flag(container_, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);

        lv_obj_set_style_bg_color(container_, lv_color_hex(0x101418), 0);
        lv_obj_set_style_bg_opa(container_, LV_OPA_90, 0);
        lv_obj_set_style_border_side(container_, LV_BORDER_SIDE_BOTTOM, 0);
        lv_obj_set_style_border_width(container_, 2, 0);
        lv_obj_set_style_border_color(container_, lv_color_hex(0x27ae60), 0);
    }

    ~StickyStatusBarWidget() noexcept {
        if (container_) {
            lv_obj_del(container_);
            container_ = nullptr;
        }
    }

    StickyStatusBarWidget(const StickyStatusBarWidget&) = delete;
    StickyStatusBarWidget& operator=(const StickyStatusBarWidget&) = delete;

    StickyStatusBarWidget(StickyStatusBarWidget&& other) noexcept : container_(other.container_) {
        other.container_ = nullptr;
    }

    StickyStatusBarWidget& operator=(StickyStatusBarWidget&& other) noexcept {
        if (this != &other) {
            if (container_) lv_obj_del(container_);
            container_ = other.container_;
            other.container_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] lv_obj_t* handle() const noexcept { return container_; }

private:
    lv_obj_t* container_{nullptr};
};

} // namespace gcs::ui
