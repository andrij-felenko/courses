#ifndef IIO_DEVICE_HPP
#define IIO_DEVICE_HPP

#include <iio.h>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <cstdint>
#include <cstddef>

// RAII-обгортка для автоматичного керування ресурсом iio_context
class IioContext {
public:
    explicit IioContext(const std::string& uri = "");
    ~IioContext();

    IioContext(const IioContext&) = delete;
    IioContext& operator=(const IioContext&) = delete;
    IioContext(IioContext&& other) noexcept;
    IioContext& operator=(IioContext&& other) noexcept;

    [[nodiscard]] struct iio_context* get() const noexcept { return ctx_; }
    [[nodiscard]] struct iio_device* find_device(const std::string& name_or_id) const;

private:
    struct iio_context* ctx_{nullptr};
};

// RAII-обгортка для безпечного створення та автоматичного вивільнення кільцевого буфера iio_buffer
class IioBuffer {
public:
    IioBuffer(struct iio_device* dev, std::size_t samples_count, bool cyclic = false);
    ~IioBuffer();

    IioBuffer(const IioBuffer&) = delete;
    IioBuffer& operator=(const IioBuffer&) = delete;
    IioBuffer(IioBuffer&& other) noexcept;
    IioBuffer& operator=(IioBuffer&& other) noexcept;

    [[nodiscard]] struct iio_buffer* get() const noexcept { return buf_; }
    std::ptrdiff_t refill();

private:
    struct iio_buffer* buf_{nullptr};
};

// Структура для збереження один кадр зчитаних даних інерційного давача
struct InertialSample {
    double timestamp_sec{0.0};
    int16_t accel_x{0};
    int16_t accel_y{0};
    int16_t accel_z{0};
    int16_t gyro_x{0};
    int16_t gyro_y{0};
    int16_t gyro_z{0};
};

// Управління IIO-пристроєм: ініціалізація каналів акселерометра/гіроскопа та зчитування вимірів
class IioInertialSensor {
public:
    IioInertialSensor(const std::string& device_name, const std::string& context_uri = "");
    ~IioInertialSensor() = default;

    void configure_channels();
    void create_buffer(std::size_t samples_count = 1024);
    std::vector<InertialSample> read_samples();

private:
    IioContext context_;
    struct iio_device* dev_{nullptr};
    std::unique_ptr<IioBuffer> buffer_;

    struct iio_channel* ch_accel_x_{nullptr};
    struct iio_channel* ch_accel_y_{nullptr};
    struct iio_channel* ch_accel_z_{nullptr};
    struct iio_channel* ch_gyro_x_{nullptr};
    struct iio_channel* ch_gyro_y_{nullptr};
    struct iio_channel* ch_gyro_z_{nullptr};
    struct iio_channel* ch_timestamp_{nullptr};

    struct iio_channel* enable_channel_if_exists(const std::string& ch_name);
};

// Вимірювання та оцінка реальної частоти дискретизації потоку даних у реальному часі
class FrameRateCalculator {
public:
    explicit FrameRateCalculator(std::size_t window_size = 100);

    void update(std::size_t sample_count);
    [[nodiscard]] double current_fps() const noexcept { return current_fps_; }
    [[nodiscard]] bool is_ready() const noexcept { return ready_; }

private:
    std::size_t window_size_;
    std::size_t accumulated_samples_{0};
    double current_fps_{0.0};
    bool ready_{false};
    std::chrono::steady_clock::time_point last_time_;
};

#endif // IIO_DEVICE_HPP
