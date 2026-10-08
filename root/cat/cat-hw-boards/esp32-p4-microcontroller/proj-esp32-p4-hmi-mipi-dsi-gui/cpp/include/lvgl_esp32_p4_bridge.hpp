#ifndef LVGL_ESP32_P4_BRIDGE_HPP
#define LVGL_ESP32_P4_BRIDGE_HPP

#include "mipi_dsi_display.hpp"
#include "ppa_accelerator.hpp"
#include <atomic>
#include <memory>

#if __has_include("lvgl.h")
    #include "lvgl.h"
#else
    // Заглушки структур LVGL v8/v9 для автономної підтримки
    typedef struct _lv_color_t { uint16_t full; } lv_color_t;
    typedef struct _lv_area_t { int32_t x1, y1, x2, y2; } lv_area_t;
    typedef struct _lv_disp_drv_t {
        void* user_data;
        int32_t hor_res;
        int32_t ver_res;
        void* draw_buf;
        uint32_t full_refresh;
    } lv_disp_drv_t;
    typedef struct _lv_disp_draw_buf_t {} lv_disp_draw_buf_t;
    typedef struct _lv_disp_t {} lv_disp_t;

    inline void lv_disp_flush_ready(lv_disp_drv_t*) {}
    inline void lv_disp_drv_init(lv_disp_drv_t* drv) { std::memset(drv, 0, sizeof(*drv)); }
    inline void lv_disp_draw_buf_init(lv_disp_draw_buf_t*, void*, void*, uint32_t) {}
    inline lv_disp_t* lv_disp_drv_register(lv_disp_drv_t*) { return nullptr; }
    inline void lv_tick_inc(uint32_t) {}
    inline uint32_t lv_timer_handler() { return 5; }
#endif

namespace esp32_p4 {

/// Конфігурація інтеграційного мосту LVGL та ESP32-P4
struct BridgeConfig {
    MipiDsiDisplay* display{nullptr};        // Драйвер MIPI-DSI дисплея
    PpaAccelerator* accelerator{nullptr};    // 2D-прискорювач PPA
    uint16_t width{800};                     // Ширина UI
    uint16_t height{480};                    // Висота UI
    bool enable_ppa{true};                   // Прапорець використання прискорення PPA
    bool use_double_buffering{true};         // Режим подвійного буферизування
};

/**
 * @brief Міст інтеграції графічної бібліотеки LVGL з периферією ESP32-P4.
 *
 * Перенаправляє виклики рендерингу LVGL (flush_cb) на прискорювач PPA,
 * керує 32-байтно вирівняними кадровими буферами та забезпечує
 * синхронізацію кадрів VSYNC із `lv_disp_flush_ready`.
 */
class LvglEsp32P4Bridge {
public:
    LvglEsp32P4Bridge() noexcept = default;
    ~LvglEsp32P4Bridge();

    LvglEsp32P4Bridge(const LvglEsp32P4Bridge&) = delete;
    LvglEsp32P4Bridge& operator=(const LvglEsp32P4Bridge&) = delete;

    /**
     * @brief Ініціалізація буферів рендерингу та реєстрація драйвера LVGL.
     * @param config Налаштування мосту.
     * @return true у разі успішної ініціалізації.
     */
    bool initialize(const BridgeConfig& config);

    /**
     * @brief Деініціалізація та скасування реєстрації LVGL.
     */
    void deinitialize();

    /**
     * @brief Крок обробки таймера LVGL.
     * @param elapsed_ms Кількість мілісекунд, що минули з попереднього виклику.
     */
    void update_tick(uint32_t elapsed_ms);

    /**
     * @brief Запуск циклу обробки подій та анімацій LVGL.
     * @return Затримка в мілісекундах до наступного виклику.
     */
    uint32_t handle_task();

    /// Зворотний виклик оновлення екрана LVGL (flush callback)
    static void flush_callback(lv_disp_drv_t* drv, const lv_area_t* area, lv_color_t* color_p);

    /// Отримати стан ініціалізації
    [[nodiscard]] bool is_initialized() const noexcept { return is_initialized_; }

private:
    BridgeConfig config_{};
    FrameBufferGuard fb_primary_{};
    FrameBufferGuard fb_secondary_{};

    lv_disp_draw_buf_t draw_buf_{};
    lv_disp_drv_t disp_drv_{};
    lv_disp_t* disp_handle_{nullptr};

    bool is_initialized_{false};
    std::atomic<bool> is_flushing_{false};
};

} // namespace esp32_p4

#endif // LVGL_ESP32_P4_BRIDGE_HPP
