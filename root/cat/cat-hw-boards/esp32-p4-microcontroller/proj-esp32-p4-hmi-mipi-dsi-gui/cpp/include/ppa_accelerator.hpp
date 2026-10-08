#ifndef PPA_ACCELERATOR_HPP
#define PPA_ACCELERATOR_HPP

#include <cstdint>
#include <cstddef>
#include <functional>
#include <memory>
#include <utility>

#if __has_include("esp_heap_caps.h")
    #include "esp_heap_caps.h"
#else
    #define MALLOC_CAP_INTERNAL (1 << 3)
    #define MALLOC_CAP_DMA      (1 << 12)
    #define MALLOC_CAP_SPIRAM   (1 << 10)
#endif

namespace esp32_p4 {

/**
 * @brief RAII-обгортка для безпечного виділення та керування 32-байтно
 * вирівняною пам'яттю кадрових буферів (SRAM / PSRAM) для DMA та PPA ESP32-P4.
 */
class FrameBufferGuard {
public:
    FrameBufferGuard() noexcept = default;

    /**
     * @brief Конструктор виділення вирівняного буфера.
     * @param size Розмір буфера в байтах.
     * @param alignment Вирівнювання в байтах (за замовчуванням 32 байти для кеш-ліній ESP32-P4).
     * @param caps Прапорці пам'яті heap_caps (DMA, INTERNAL, SPIRAM).
     */
    explicit FrameBufferGuard(size_t size, size_t alignment = 32, uint32_t caps = MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);

    ~FrameBufferGuard();

    // Заборона копіювання (унікальне володіння буфером)
    FrameBufferGuard(const FrameBufferGuard&) = delete;
    FrameBufferGuard& operator=(const FrameBufferGuard&) = delete;

    // Переміщення буфера
    FrameBufferGuard(FrameBufferGuard&& other) noexcept;
    FrameBufferGuard& operator=(FrameBufferGuard&& other) noexcept;

    /// Звільнення та перевиділення пам'яті
    bool allocate(size_t size, size_t alignment = 32, uint32_t caps = MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    void free() noexcept;

    [[nodiscard]] uint8_t* data() noexcept { return buffer_; }
    [[nodiscard]] const uint8_t* data() const noexcept { return buffer_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] size_t alignment() const noexcept { return alignment_; }
    [[nodiscard]] bool is_valid() const noexcept { return buffer_ != nullptr && size_ > 0; }

    /// Очищення вмісту буфера конкретним байтом
    void clear(uint8_t value = 0) noexcept;

    /// Шаблонний доступ до даних
    template <typename T>
    [[nodiscard]] T* as() noexcept {
        return reinterpret_cast<T*>(buffer_);
    }

    template <typename T>
    [[nodiscard]] const T* as() const noexcept {
        return reinterpret_cast<const T*>(buffer_);
    }

private:
    uint8_t* buffer_{nullptr};
    size_t size_{0};
    size_t alignment_{32};
};

/// Колірний формат для прискорювача PPA
enum class PpaColorFormat : uint8_t {
    RGB565 = 0,
    RGB888,
    ARGB8888,
    XRGB8888
};

/// Апаратний кут повороту PPA
enum class PpaRotation : uint8_t {
    Degree0 = 0,
    Degree90,
    Degree180,
    Degree270
};

/// Параметри блендингу двох шарів
struct PpaBlendConfig {
    const void* fg_buffer{nullptr};        // Передній план
    const void* bg_buffer{nullptr};        // Задній план
    void* out_buffer{nullptr};             // Результат
    uint16_t width{0};
    uint16_t height{0};
    uint8_t alpha{255};                    // Глобальна прозорість (0..255)
    PpaColorFormat color_format{PpaColorFormat::RGB565};
};

/// Параметри масштабування
struct PpaScaleConfig {
    const void* src_buffer{nullptr};
    void* dst_buffer{nullptr};
    uint16_t src_width{0};
    uint16_t src_height{0};
    uint16_t dst_width{0};
    uint16_t dst_height{0};
    PpaColorFormat color_format{PpaColorFormat::RGB565};
};

/**
 * @brief Клас керування апаратним 2D-прискорювачем PPA (Pixel Processing Accelerator) ESP32-P4.
 *
 * Забезпечує високоефективні операції блендингу, масштабування, повороту
 * та конверсії колірних форматів з використанням асинхронних DMA-передач.
 */
class PpaAccelerator {
public:
    PpaAccelerator() noexcept = default;
    ~PpaAccelerator();

    PpaAccelerator(const PpaAccelerator&) = delete;
    PpaAccelerator& operator=(const PpaAccelerator&) = delete;

    PpaAccelerator(PpaAccelerator&& other) noexcept;
    PpaAccelerator& operator=(PpaAccelerator&& other) noexcept;

    /**
     * @brief Ініціалізація апаратного двигуна PPA.
     * @return true у разі успішної ініціалізації.
     */
    bool initialize();

    /**
     * @brief Деініціалізація та вимикання PPA.
     */
    void deinitialize();

    /**
     * @brief Асинхронний альфа-блендинг двох шарів.
     */
    bool blend_async(const PpaBlendConfig& config, std::function<void()> on_complete = nullptr);

    /**
     * @brief Асинхронне апаратне масштабування буфера.
     */
    bool scale_async(const PpaScaleConfig& config, std::function<void()> on_complete = nullptr);

    /**
     * @brief Асинхронний поворот зображення (0, 90, 180, 270 градусів).
     */
    bool rotate_async(const void* src, void* dst, uint16_t width, uint16_t height,
                      PpaColorFormat fmt, PpaRotation rotation, std::function<void()> on_complete = nullptr);

    /**
     * @brief Асинхронна конверсія колірного формату пікселів.
     */
    bool convert_color_async(const void* src, void* dst, uint32_t pixel_count,
                             PpaColorFormat src_fmt, PpaColorFormat dst_fmt, std::function<void()> on_complete = nullptr);

    /**
     * @brief Блокуюче очікування завершення всіх операцій PPA.
     */
    bool wait_idle(uint32_t timeout_ms = 100);

    /// Отримати стан занятості апаратного блоку PPA
    [[nodiscard]] bool is_busy() const noexcept { return is_busy_; }

private:
    bool is_initialized_{false};
    bool is_busy_{false};
    void* ppa_handle_{nullptr};
    std::function<void()> current_callback_{nullptr};

    void handle_dma_interrupt();
};

} // namespace esp32_p4

#endif // PPA_ACCELERATOR_HPP
