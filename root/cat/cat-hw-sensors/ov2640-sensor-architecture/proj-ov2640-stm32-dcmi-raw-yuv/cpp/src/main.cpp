#include "sccb_bus.hpp"
#include "dcmi_dma_buffer.hpp"
#include "ov2640_driver.hpp"

#include <iostream>
#include <iomanip>
#include <thread>
#include <chrono>

int main() {
    std::cout << "========================================================\n";
    std::cout << " Драйвер камери OV2640 (SCCB + DCMI / DMA Interface)   \n";
    std::cout << "========================================================\n\n";

    // 1. Створення об'єкта шини SCCB (адреса камери 0x30)
    ov2640::SccbBus sccb_bus(0x30);

    // 2. Створення менеджера кадрової пам'яті DCMI/DMA (2 буфери по 64 КБ кожен)
    ov2640::DcmiDmaBuffer dcmi_dma(2, 64 * 1024);

    // 3. Ініціалізація головного драйвера камери
    ov2640::Ov2640Driver camera(sccb_bus, dcmi_dma);

    std::cout << "[INFO] Ініціалізація апаратних систем та перевірка PID/VER...\n";
    if (!camera.init()) {
        std::cerr << "[ERROR] Помилка ініціалізації камери OV2640 на шині SCCB!\n";
        return 1;
    }
    std::cout << "[OK] Сенсор OV2640 успішно виявлено та ініціалізовано.\n\n";

    // 4. Конфігурація параметрів кадру та вихідного формату
    std::cout << "[INFO] Налаштування режиму JPEG SVGA (800x600)...\n";
    camera.setResolution(ov2640::FrameResolution::SVGA_800x600);
    camera.setPixelFormat(ov2640::PixelFormat::JPEG);
    camera.setJpegQuality(12);
    camera.setBrightness(0);
    camera.setContrast(1);

    // 5. Реєстрація обробника готових кадрів (callback)
    auto on_frame_ready = [](const ov2640::FrameBuffer& frame) {
        std::cout << "[FRAME] Отримано кадр #" << frame.sequence_number
                  << " | Довжина: " << frame.length << " байт"
                  << " | Часова позначка: " << frame.timestamp_us << " us"
                  << " | SOI: 0x" << std::hex << (int)frame.data[0] << (int)frame.data[1]
                  << " EOI: 0x" << (int)frame.data[frame.length - 2] << (int)frame.data[frame.length - 1]
                  << std::dec << "\n";
    };

    // 6. Запуск захоплення відеопотоку
    std::cout << "[INFO] Запуск безперервного захоплення відеопотоку DMA...\n\n";
    if (!camera.startStreaming(on_frame_ready)) {
        std::cerr << "[ERROR] Не вдалося запустити захоплення DCMI DMA!\n";
        return 1;
    }

    // 7. Імітація роботи обробки кадрів у головному циклі реального часу
    for (int i = 0; i < 5; ++i) {
        camera.process();
        std::this_thread::sleep_for(std::chrono::milliseconds(30));
    }

    // 8. Завершення роботи
    std::cout << "\n[INFO] Зупинка відеопотоку та звільнення ресурсів...\n";
    camera.stopStreaming();

    std::cout << "[OK] Драйвер OV2640 завершив роботу успішно.\n";
    return 0;
}
