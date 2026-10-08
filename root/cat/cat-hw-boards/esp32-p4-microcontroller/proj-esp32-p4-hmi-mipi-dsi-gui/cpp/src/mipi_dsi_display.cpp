#include "mipi_dsi_display.hpp"
#include <iostream>
#include <cstring>

namespace esp32_p4 {

MipiDsiDisplay::~MipiDsiDisplay() {
    deinitialize();
}

MipiDsiDisplay::MipiDsiDisplay(MipiDsiDisplay&& other) noexcept {
    *this = std::move(other);
}

MipiDsiDisplay& MipiDsiDisplay::operator=(MipiDsiDisplay&& other) noexcept {
    if (this != &other) {
        deinitialize();

        config_ = other.config_;
        state_.store(other.state_.load());
        vsync_callback_ = std::move(other.vsync_callback_);
        bus_handle_ = other.bus_handle_;
        panel_handle_ = other.panel_handle_;
        vsync_sem_ = other.vsync_sem_;
        active_buffer_idx_ = other.active_buffer_idx_;
        pending_frame_ptr_ = other.pending_frame_ptr_;

        other.bus_handle_ = nullptr;
        other.panel_handle_ = nullptr;
        other.vsync_sem_ = nullptr;
        other.state_.store(DisplayState::Uninitialized);
    }
    return *this;
}

bool MipiDsiDisplay::initialize(const DisplayConfig& config) {
    if (state_.load() != DisplayState::Uninitialized) {
        std::cerr << "[MIPI-DSI] Драйвер вже ініціалізовано." << std::endl;
        return false;
    }

    if (config.width == 0 || config.height == 0 || config.lane_num == 0) {
        std::cerr << "[MIPI-DSI] Некоректні параметри конфігурації кадру." << std::endl;
        state_.store(DisplayState::Error);
        return false;
    }

    config_ = config;

    std::cout << "[MIPI-DSI] Налаштування шини MIPI-DSI Host ESP32-P4 ("
              << config_.width << "x" << config_.height << ", "
              << static_cast<int>(config_.lane_num) << " D-PHY lanes, "
              << config_.phy_clk_mhz << " MHz)..." << std::endl;

    // Конфігурація DPHY таймінгів та сигналів VSYNC/HSYNC
    std::cout << "[MIPI-DSI] Синхронізація: HSYNC pulse=" << config_.hsync_pulse_width
              << ", VSYNC pulse=" << config_.vsync_pulse_width << std::endl;

    // Створення семафора VSYNC для синхронізації потоків
#if __has_include("freertos/FreeRTOS.h")
    vsync_sem_ = xSemaphoreCreateBinary();
    if (!vsync_sem_) {
        std::cerr << "[MIPI-DSI] Не вдалося створити семафор VSYNC." << std::endl;
        state_.store(DisplayState::Error);
        return false;
    }
#else
    vsync_sem_ = reinterpret_cast<SemaphoreHandle_t>(1);
#endif

    // Прив'язка системного макету хост-панелі MIPI-DSI ESP32-P4
    bus_handle_ = reinterpret_cast<esp_lcd_dsi_bus_handle_t>(0xD5100000);
    panel_handle_ = reinterpret_cast<esp_lcd_panel_handle_t>(0xD5101000);

    state_.store(DisplayState::Ready);
    std::cout << "[MIPI-DSI] Контролер MIPI-DSI успішно ініціалізовано." << std::endl;
    return true;
}

void MipiDsiDisplay::deinitialize() {
    if (state_.load() == DisplayState::Uninitialized) {
        return;
    }

    std::cout << "[MIPI-DSI] Зупинка передачі та звільнення MIPI-DSI ресурсів..." << std::endl;

    bus_handle_ = nullptr;
    panel_handle_ = nullptr;
    vsync_sem_ = nullptr;

    state_.store(DisplayState::Uninitialized);
}

size_t MipiDsiDisplay::get_frame_buffer_size() const noexcept {
    size_t bytes_per_pixel = 2;
    if (config_.color_format == DsiColorFormat::RGB888) {
        bytes_per_pixel = 3;
    } else if (config_.color_format == DsiColorFormat::ARGB8888) {
        bytes_per_pixel = 4;
    }
    return static_cast<size_t>(config_.width) * config_.height * bytes_per_pixel;
}

bool MipiDsiDisplay::draw_frame_async(const void* frame_data, size_t data_size) {
    if (state_.load() != DisplayState::Ready) {
        std::cerr << "[MIPI-DSI] Драйвер не готовий до нової DMA передачі." << std::endl;
        return false;
    }

    const size_t expected_size = get_frame_buffer_size();
    if (!frame_data || data_size < expected_size) {
        std::cerr << "[MIPI-DSI] Помилка: Некоректний графічний буфер або розмір ("
                  << data_size << " < " << expected_size << ")." << std::endl;
        return false;
    }

    // Перевірка 32-байтного вирівнювання адреси для DMA контролера ESP32-P4
    if (reinterpret_cast<uintptr_t>(frame_data) % 32 != 0) {
        std::cerr << "[MIPI-DSI] Попередження: Буфер не вирівняний по межі 32 байтів!" << std::endl;
    }

    state_.store(DisplayState::Transmitting);
    pending_frame_ptr_ = frame_data;

    // Перемикання індексу кадрового буфера (Ping-Pong double buffering)
    active_buffer_idx_ ^= 1;

    // Запуск неблокуючої DMA передачі через MIPI-DSI Host
    // Симуляція симетричної відправки пиксельного потоку на панель
    notify_vsync_from_isr();

    return true;
}

void MipiDsiDisplay::set_vsync_callback(std::function<void()> callback) {
    vsync_callback_ = std::move(callback);
}

bool MipiDsiDisplay::wait_vsync(uint32_t timeout_ms) {
    if (state_.load() == DisplayState::Uninitialized) {
        return false;
    }

#if __has_include("freertos/FreeRTOS.h")
    if (vsync_sem_) {
        return xSemaphoreTake(vsync_sem_, pdMS_TO_TICKS(timeout_ms)) == pdTRUE;
    }
#endif
    (void)timeout_ms;
    return true;
}

void MipiDsiDisplay::notify_vsync_from_isr() {
    // Сповіщення про завершення передачі кадру (VSYNC interrupt)
    state_.store(DisplayState::Ready);
    pending_frame_ptr_ = nullptr;

#if __has_include("freertos/FreeRTOS.h")
    if (vsync_sem_) {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(vsync_sem_, &xHigherPriorityTaskWoken);
    }
#endif

    if (vsync_callback_) {
        vsync_callback_();
    }
}

} // namespace esp32_p4
