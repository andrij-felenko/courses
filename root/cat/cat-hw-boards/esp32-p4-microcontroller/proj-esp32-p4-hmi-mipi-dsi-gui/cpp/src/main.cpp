#include "mipi_dsi_display.hpp"
#include "ppa_accelerator.hpp"
#include "lvgl_esp32_p4_bridge.hpp"

#include <iostream>
#include <thread>
#include <chrono>

using namespace esp32_p4;

int main() {
    std::cout << "==========================================================" << std::endl;
    std::cout << "  Графічний пайплайн ESP32-P4: MIPI-DSI + PPA + LVGL C++  " << std::endl;
    std::cout << "==========================================================" << std::endl;

    // 1. Конфігурація та ініціалізація MIPI-DSI Дисплея
    DisplayConfig dsi_cfg{};
    dsi_cfg.width = 800;
    dsi_cfg.height = 480;
    dsi_cfg.lane_num = 2;
    dsi_cfg.phy_clk_mhz = 500;
    dsi_cfg.refresh_rate_hz = 60;
    dsi_cfg.color_format = DsiColorFormat::RGB565;

    MipiDsiDisplay display;
    if (!display.initialize(dsi_cfg)) {
        std::cerr << "Помилка ініціалізації MIPI-DSI дисплея!" << std::endl;
        return -1;
    }

    // 2. Ініціалізація апаратного 2D-прискорювача PPA (Pixel Processing Accelerator)
    PpaAccelerator accelerator;
    if (!accelerator.initialize()) {
        std::cerr << "Помилка ініціалізації прискорювача PPA!" << std::endl;
        return -1;
    }

    // 3. Конфігурація мосту інтеграції LVGL
    BridgeConfig bridge_cfg{};
    bridge_cfg.display = &display;
    bridge_cfg.accelerator = &accelerator;
    bridge_cfg.width = 800;
    bridge_cfg.height = 480;
    bridge_cfg.enable_ppa = true;
    bridge_cfg.use_double_buffering = true;

    LvglEsp32P4Bridge bridge;
    if (!bridge.initialize(bridge_cfg)) {
        std::cerr << "Помилка ініціалізації мосту LVGL!" << std::endl;
        return -1;
    }

    std::cout << "\n[Основний цикл] Запуск візуального пайплайну (60 FPS)..." << std::endl;

    // Симуляція декількох кадрів графічного циклу
    for (int frame = 1; frame <= 5; ++frame) {
        std::cout << "\n--- Рендеринг кадру #" << frame << " ---" << std::endl;

        // Симуляція плину часу LVGL
        bridge.update_tick(16);

        // Обробка графічних задач LVGL
        uint32_t delay = bridge.handle_task();
        (void)delay;

        // Очікування вертикальної синхронізації VSYNC для уникнення tearing
        display.wait_vsync(50);

        std::this_thread::sleep_for(std::chrono::milliseconds(16));
    }

    std::cout << "\n[Завершення] Графічний пайплайн опрацьовано успішно." << std::endl;
    return 0;
}
