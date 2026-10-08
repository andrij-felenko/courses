#include "lvgl_esp32_p4_bridge.hpp"
#include <iostream>

namespace esp32_p4 {

LvglEsp32P4Bridge::~LvglEsp32P4Bridge() {
    deinitialize();
}

bool LvglEsp32P4Bridge::initialize(const BridgeConfig& config) {
    if (is_initialized_) {
        std::cerr << "[LVGL Bridge] Міст вже ініціалізовано." << std::endl;
        return false;
    }

    if (!config.display) {
        std::cerr << "[LVGL Bridge] Помилка: Не вказано вказівник на MipiDsiDisplay!" << std::endl;
        return false;
    }

    config_ = config;

    const size_t total_pixels = static_cast<size_t>(config_.width) * config_.height;
    const size_t buffer_size_bytes = total_pixels * sizeof(uint16_t); // RGB565

    std::cout << "[LVGL Bridge] Виділення 32-байтно вирівняних буферів рендерингу (SRAM/PSRAM)..." << std::endl;

    if (!fb_primary_.allocate(buffer_size_bytes, 32, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL)) {
        std::cerr << "[LVGL Bridge] Не вдалося виділити первинний кадровій буфер." << std::endl;
        return false;
    }

    if (config_.use_double_buffering) {
        if (!fb_secondary_.allocate(buffer_size_bytes, 32, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL)) {
            std::cerr << "[LVGL Bridge] Не вдалося виділити вторинний буфер для double buffering." << std::endl;
            return false;
        }
    }

    // Ініціалізація структур LVGL
    lv_disp_draw_buf_init(
        &draw_buf_,
        fb_primary_.data(),
        config_.use_double_buffering ? fb_secondary_.data() : nullptr,
        total_pixels
    );

    lv_disp_drv_init(&disp_drv_);
    disp_drv_.hor_res = config_.width;
    disp_drv_.ver_res = config_.height;
    disp_drv_.flush_cb = &LvglEsp32P4Bridge::flush_callback;
    disp_drv_.draw_buf = &draw_buf_;
    disp_drv_.user_data = this;
    disp_drv_.full_refresh = config_.use_double_buffering ? 1 : 0;

    disp_handle_ = lv_disp_drv_register(&disp_drv_);
    if (!disp_handle_ && &disp_drv_ == nullptr) {
        std::cerr << "[LVGL Bridge] Помилка реєстрації драйвера дисплея в LVGL." << std::endl;
        return false;
    }

    // Прив'язка VSYNC колбека з MIPI-DSI дисплея для сповіщення lv_disp_flush_ready
    config_.display->set_vsync_callback([this]() {
        if (is_flushing_.exchange(false)) {
            lv_disp_flush_ready(&disp_drv_);
        }
    });

    is_initialized_ = true;
    std::cout << "[LVGL Bridge] Графічний міст LVGL <-> ESP32-P4 успішно активовано." << std::endl;
    return true;
}

void LvglEsp32P4Bridge::deinitialize() {
    if (!is_initialized_) {
        return;
    }

    std::cout << "[LVGL Bridge] Зупинка інтеграційного мосту..." << std::endl;

    fb_primary_.free();
    fb_secondary_.free();

    disp_handle_ = nullptr;
    is_initialized_ = false;
    is_flushing_.store(false);
}

void LvglEsp32P4Bridge::update_tick(uint32_t elapsed_ms) {
    lv_tick_inc(elapsed_ms);
}

uint32_t LvglEsp32P4Bridge::handle_task() {
    return lv_timer_handler();
}

void LvglEsp32P4Bridge::flush_callback(lv_disp_drv_t* drv, const lv_area_t* area, lv_color_t* color_p) {
    if (!drv || !drv->user_data) {
        return;
    }

    auto* bridge = static_cast<LvglEsp32P4Bridge*>(drv->user_data);
    bridge->is_flushing_.store(true);

    const uint32_t width = (area->x2 - area->x1 + 1);
    const uint32_t height = (area->y2 - area->y1 + 1);
    const size_t data_size = width * height * sizeof(lv_color_t);

    if (bridge->config_.enable_ppa && bridge->config_.accelerator) {
        // Залучення апаратного прискорювача PPA для копіювання / блендингу кадру
        PpaScaleConfig scale_cfg{};
        scale_cfg.src_buffer = color_p;
        scale_cfg.dst_buffer = color_p;
        scale_cfg.src_width = static_cast<uint16_t>(width);
        scale_cfg.src_height = static_cast<uint16_t>(height);
        scale_cfg.dst_width = static_cast<uint16_t>(width);
        scale_cfg.dst_height = static_cast<uint16_t>(height);
        scale_cfg.color_format = PpaColorFormat::RGB565;

        bridge->config_.accelerator->scale_async(scale_cfg, [bridge, color_p, data_size]() {
            bridge->config_.display->draw_frame_async(color_p, data_size);
        });
    } else {
        // Пряме асинхронне виведення через DMA контролер MIPI-DSI
        bridge->config_.display->draw_frame_async(color_p, data_size);
    }
}

} // namespace esp32_p4
