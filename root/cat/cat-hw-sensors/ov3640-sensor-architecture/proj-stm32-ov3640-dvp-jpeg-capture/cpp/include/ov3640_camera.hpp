#pragma once

#include "sccb_bus.hpp"
#include "dcmi_dma_manager.hpp"
#include "jpeg_stream_parser.hpp"
#include "ov3640_registers.hpp"
#include <functional>

namespace camera {

// Тип обробника події готовності нового зображення
using OnFrameReadyHandler = std::function<void(const FrameBuffer& frame)>;

// Клас-фасад Ov3640Camera об'єднує шину SCCB, DCMI/DMA менеджер та JPEG парсер.
class Ov3640Camera {
public:
    explicit Ov3640Camera(uint8_t sccb_address = 0x3C);
    ~Ov3640Camera();

    // Ініціалізація апаратури камери та перевірка PID/VER
    bool init();

    // Вибір роздільної здатності камери
    bool set_resolution(Resolution res);

    // Вибір вихідного формату (YUV422 / JPEG)
    bool set_format(ImageFormat fmt);

    // Налаштування авто-експозиції, підсилення та балансу білого
    bool set_auto_exposure(bool enable);
    bool set_auto_gain(bool enable);
    bool set_auto_white_balance(bool enable);

    // Запуск та зупинка потокового захоплення
    bool start();
    bool stop();

    // Реєстрація прикладного обробника кадрів
    void on_frame_ready(OnFrameReadyHandler handler);

    // Симуляція порції DMA даних (для тестування без фізичного МК)
    void inject_dma_data(const uint8_t* data, size_t size, uint8_t buffer_index);

private:
    SccbBus sccb_bus_;
    DcmiDmaManager dcmi_dma_;
    JpegStreamParser jpeg_parser_;

    Resolution current_resolution_{Resolution::FHD_1920x1080};
    ImageFormat current_format_{ImageFormat::JPEG};
    OnFrameReadyHandler frame_handler_{nullptr};
    bool streaming_{false};

    void handle_dma_buffer(const uint8_t* buffer, size_t size, uint8_t buffer_index);
    bool apply_register_settings(const std::vector<RegisterSetting>& settings);
};

} // namespace camera
