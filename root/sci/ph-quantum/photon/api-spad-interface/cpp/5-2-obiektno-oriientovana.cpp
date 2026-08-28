#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <stdexcept>
#include <memory>

class SpadDevice {
public:
    explicit SpadDevice(int dev_idx) {
        spad_status_t st = spad_init(dev_idx, &handle_);
        if (st != SPAD_OK) {
            throw std::runtime_error("Не вдалося ініціалізувати SPAD пристрій! Код помилки: " + std::to_string(st));
        }
    }

    ~SpadDevice() noexcept {
        if (handle_) {
            spad_enable_high_voltage(handle_, false);
            spad_close(handle_);
            handle_ = nullptr;
        }
    }

    // Заборона копіювання для запобігання подвійному закриттю хендла
    SpadDevice(const SpadDevice&) = delete;
    SpadDevice& operator=(const SpadDevice&) = delete;

    // Дозвіл переміщення (Move Semantics)
    SpadDevice(SpadDevice&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    SpadDevice& operator=(SpadDevice&& other) noexcept {
        if (this != &other) {
            if (handle_) {
                spad_enable_high_voltage(handle_, false);
                spad_close(handle_);
            }
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }

    void setup(float bias_v, float thresh_mv, uint32_t dead_ns, float temp_c = -20.0f) {
        spad_config_t cfg{};
        cfg.bias_voltage_v = bias_v;
        cfg.discriminator_mv = thresh_mv;
        cfg.dead_time_ns = dead_ns;
        cfg.target_temp_c = temp_c;
        cfg.enable_gating = false;
        cfg.coinc_window_ps = 1000; // 1 ns вікно збігів

        spad_status_t st = spad_configure(handle_, &cfg);
        if (st != SPAD_OK) {
            throw std::runtime_error("Помилка конфігурації SPAD! Код: " + std::to_string(st));
        }
    }

    void start_high_voltage() {
        spad_status_t st = spad_enable_high_voltage(handle_, true);
        if (st != SPAD_OK) {
            throw std::runtime_error("Помилка увімкнення високої напруги! Код: " + std::to_string(st));
        }
    }

    void stop_high_voltage() {
        spad_status_t st = spad_enable_high_voltage(handle_, false);
        if (st != SPAD_OK) {
            throw std::runtime_error("Помилка вимкнення високої напруги!");
        }
    }

    [[nodiscard]] spad_metrics_t get_metrics() const {
        spad_metrics_t m{};
        spad_status_t st = spad_read_metrics(handle_, &m);
        if (st != SPAD_OK) {
            throw std::runtime_error("Помилка зчитування метрологічних метрик!");
        }
        return m;
    }

    [[nodiscard]] std::vector<uint64_t> read_timetags(uint32_t max_count) const {
        std::vector<uint64_t> buffer(max_count);
        uint32_t actual_read = 0;
        spad_status_t st = spad_read_timetags(handle_, buffer.data(), max_count, &actual_read);
        if (st != SPAD_OK) {
            throw std::runtime_error("Помилка читання часових міток!");
        }
        buffer.resize(actual_read);
        return buffer;
    }

private:
    void* handle_ = nullptr;
};
