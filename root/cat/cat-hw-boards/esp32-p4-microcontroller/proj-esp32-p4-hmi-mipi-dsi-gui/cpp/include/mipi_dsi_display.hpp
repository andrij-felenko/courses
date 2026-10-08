#ifndef MIPI_DSI_DISPLAY_HPP
#define MIPI_DSI_DISPLAY_HPP

#include <cstdint>
#include <cstddef>
#include <functional>
#include <atomic>
#include <utility>

// Симуляція або підключення заголовків ESP-IDF для роботи з MIPI-DSI Host та FreeRTOS
#if __has_include("esp_lcd_mipi_dsi.h")
    #include "esp_lcd_mipi_dsi.h"
    #include "freertos/FreeRTOS.h"
    #include "freertos/semphr.h"
#else
    // Абстракційні визначення для підтримки автономного аналізу та компіляції
    typedef void* esp_lcd_panel_handle_t;
    typedef void* esp_lcd_dsi_bus_handle_t;
    typedef void* SemaphoreHandle_t;
    typedef int esp_err_t;
    #define ESP_OK 0
    #define ESP_FAIL -1
    #define ESP_ERR_NO_MEM 0x101
    #define ESP_ERR_INVALID_ARG 0x102
#endif

namespace esp32_p4 {

/// Колірний формат дисплея MIPI-DSI
enum class DsiColorFormat : uint8_t {
    RGB565 = 0,
    RGB888 = 1,
    ARGB8888 = 2
};

/// Стан роботи периферійного контролера MIPI-DSI
enum class DisplayState : uint8_t {
    Uninitialized,
    Ready,
    Transmitting,
    Error
};

/// Низькорівневі таймінги сигналів дисплея та конфігурація MIPI D-PHY
struct DisplayConfig {
    uint16_t width{800};                   // Ширина екрана в пікселях
    uint16_t height{480};                  // Висота екрана в пікселях
    uint8_t lane_num{2};                   // Кількість ліній даних D-PHY (1 або 2)
    uint32_t phy_clk_mhz{500};             // Частота D-PHY в МГц
    uint32_t refresh_rate_hz{60};          // Бажана частота оновлення кадрів (Гц)
    DsiColorFormat color_format{DsiColorFormat::RGB565};

    // Горизонтальні таймінги (H-Porch & HSYNC)
    uint16_t hsync_pulse_width{10};
    uint16_t hsync_back_porch{40};
    uint16_t hsync_front_porch{40};

    // Вертикальні таймінги (V-Porch & VSYNC)
    uint16_t vsync_pulse_width{4};
    uint16_t vsync_back_porch{29};
    uint16_t vsync_front_porch{13};
};

/**
 * @brief Клас для інкапсуляції периферійного драйвера MIPI-DSI Host ESP32-P4.
 *
 * Відповідає за ініціалізацію шини MIPI-DSI Host, D-PHY фізичного рівня,
 * реєстрацію переривань VSYNC, асинхронне виведення кадрів через DMA
 * та синхронізацію подвійного буферизування.
 */
class MipiDsiDisplay {
public:
    MipiDsiDisplay() noexcept = default;
    ~MipiDsiDisplay();

    // Заборона копіювання (RAII інкапсуляція апаратних ресурсів)
    MipiDsiDisplay(const MipiDsiDisplay&) = delete;
    MipiDsiDisplay& operator=(const MipiDsiDisplay&) = delete;

    // Підтримка переміщення (Move semantics)
    MipiDsiDisplay(MipiDsiDisplay&& other) noexcept;
    MipiDsiDisplay& operator=(MipiDsiDisplay&& other) noexcept;

    /**
     * @brief Ініціалізація хост-контролера MIPI-DSI та панелі.
     * @param config Параметри роздільної здатності та таймінгів D-PHY.
     * @return true у разі успішного налаштування апаратури.
     */
    bool initialize(const DisplayConfig& config);

    /**
     * @brief Зупинка контролера та звільнення апаратних ресурсів.
     */
    void deinitialize();

    /**
     * @brief Запуск асинхронної DMA-передачі буфера кадру на дисплей.
     * @param frame_data Вказівник на 32-байтно вирівняний графічний буфер.
     * @param data_size Розмір буфера в байтах.
     * @return true якщо передачу успішно ініційовано.
     */
    bool draw_frame_async(const void* frame_data, size_t data_size);

    /**
     * @brief Реєстрація користувацького зворотного виклику (callback) на подій VSYNC.
     * @param callback Функція, яка викликатиметься з ISR / обробника синхронізації.
     */
    void set_vsync_callback(std::function<void()> callback);

    /**
     * @brief Очікування сигналу вертикальної синхронізації VSYNC (блокуючий виклик).
     * @param timeout_ms Максимальний час очікування в мілісекундах.
     * @return true якщо сигнал VSYNC отримано до завершення таймауту.
     */
    bool wait_vsync(uint32_t timeout_ms = 100);

    /// Отримати поточну конфігурацію дисплея
    [[nodiscard]] DisplayConfig get_config() const noexcept { return config_; }

    /// Отримати поточний стан драйвера
    [[nodiscard]] DisplayState get_state() const noexcept { return state_.load(std::memory_order_relaxed); }

    /// Отримати розмір кадрового буфера в байтах для поточної конфігурації
    [[nodiscard]] size_t get_frame_buffer_size() const noexcept;

    /// Апаратний переривальний зворотний виклик VSYNC (викликається шиною/драйвером)
    void notify_vsync_from_isr();

private:
    DisplayConfig config_{};
    std::atomic<DisplayState> state_{DisplayState::Uninitialized};
    std::function<void()> vsync_callback_{nullptr};

    esp_lcd_dsi_bus_handle_t bus_handle_{nullptr};
    esp_lcd_panel_handle_t panel_handle_{nullptr};
    SemaphoreHandle_t vsync_sem_{nullptr};

    uint8_t active_buffer_idx_{0};
    const void* pending_frame_ptr_{nullptr};
};

} // namespace esp32_p4

#endif // MIPI_DSI_DISPLAY_HPP
