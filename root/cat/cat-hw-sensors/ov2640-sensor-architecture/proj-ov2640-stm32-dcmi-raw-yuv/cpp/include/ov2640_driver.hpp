#ifndef OV2640_DRIVER_HPP
#define OV2640_DRIVER_HPP

#include "sccb_bus.hpp"
#include "dcmi_dma_buffer.hpp"
#include <cstdint>
#include <functional>

namespace ov2640 {

/// Перелік підтримуваних кадрових роздільностей
enum class FrameResolution {
    UXGA_1600x1200,
    SVGA_800x600,
    CIF_352x288
};

/// Перелік підтримуваних форматів вихідного потоку пікселів
enum class PixelFormat {
    JPEG,
    RGB565,
    YUV422
};

/// Спеціальні графічні ефекти матриці
enum class SpecialEffect {
    Normal = 0,
    Negative,
    Grayscale,
    Sepia
};

/**
 * @brief Головний C++ клас-фасад драйвера камери OV2640.
 * Інтегрує роботу шини SCCB та відеопам'яті DCMI/DMA, надаючи високорівневий інтерфейс
 * для налаштування зображення, формату та контролю захоплення кадрів.
 */
class Ov2640Driver {
public:
    Ov2640Driver(SccbBus& sccb, DcmiDmaBuffer& dcmi_dma);
    ~Ov2640Driver();

    Ov2640Driver(const Ov2640Driver&) = delete;
    Ov2640Driver& operator=(const Ov2640Driver&) = delete;

    /// Апаратна та програмна ініціалізація сенсора камери
    bool init();

    /// Виконанння програмного скидання внутрішніх регістрів OV2640
    bool reset();

    /// Встановлення роздільної здатності кадру
    bool setResolution(FrameResolution res);

    /// Встановлення вихідного формату даних (JPEG / RGB565 / YUV422)
    bool setPixelFormat(PixelFormat format);

    /// Встановлення коефіцієнта стиснення JPEG (1..63, де менше значення відповідає вищій якості)
    bool setJpegQuality(uint8_t quality);

    /// Налаштування яскравості зображення (-2..+2)
    bool setBrightness(int8_t level);

    /// Налаштування контрастності зображення (-2..+2)
    bool setContrast(int8_t level);

    /// Встановлення спец-ефектів (Нормальний, Ч/Б, Негатив, Сепія)
    bool setSpecialEffect(SpecialEffect effect);

    /// Запуск безперервного захоплення відеопотоку з асинхронним сповіщенням
    bool startStreaming(DcmiDmaBuffer::FrameReadyCallback callback);

    /// Зупинка захоплення відеопотоку
    void stopStreaming();

    /// Симуляційний крок обробника подій (викликається в головному циклі)
    void process();

    /// Отримання поточної роздільності
    FrameResolution resolution() const { return current_resolution_; }

    /// Отримання поточного формату пікселів
    PixelFormat pixelFormat() const { return current_format_; }

private:
    SccbBus& sccb_;
    DcmiDmaBuffer& dcmi_dma_;

    FrameResolution current_resolution_{FrameResolution::SVGA_800x600};
    PixelFormat current_format_{PixelFormat::JPEG};
    uint8_t jpeg_quality_{12};
    bool is_streaming_{false};

    bool loadInitTable();
    bool configureResolution(FrameResolution res);
};

} // namespace ov2640

#endif // OV2640_DRIVER_HPP
