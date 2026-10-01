#include "A3144Tachometer.hpp"
#include <chrono>
#include <utility>

// Ініціалізація статичного вказівника
A3144Tachometer* A3144Tachometer::s_instance = nullptr;

/**
 * @brief Допоміжна функція отримання системного часу в мікросекундах
 */
static uint64_t getSystemMicros() noexcept {
    using namespace std::chrono;
    return static_cast<uint64_t>(duration_cast<microseconds>(
        steady_clock::now().time_since_epoch()).count());
}

A3144Tachometer::A3144Tachometer(const TachometerConfig& config)
    : config_(config)
{
    if (config_.magnets_per_revolution == 0) {
        config_.magnets_per_revolution = 1;
    }
}

A3144Tachometer::~A3144Tachometer() {
    stop();
}

bool A3144Tachometer::begin() {
    if (s_instance != nullptr && s_instance != this) {
        return false;
    }

    s_instance = this;
    reset();

    // На мікроконтролері (Arduino/ESP32/STM32) тут виконується:
    // pinMode(config_.gpio_pin, INPUT_PULLUP);
    // attachInterrupt(digitalPinToInterrupt(config_.gpio_pin), A3144Tachometer::handleInterruptBridge, FALLING);

    is_initialized_ = true;
    return true;
}

void A3144Tachometer::stop() {
    if (s_instance == this) {
        // detachInterrupt(digitalPinToInterrupt(config_.gpio_pin));
        s_instance = nullptr;
    }
    is_initialized_ = false;
}

void A3144Tachometer::handleInterruptBridge() {
    if (s_instance != nullptr) {
        s_instance->handleInterrupt(getSystemMicros());
    }
}

void A3144Tachometer::simulatePulse(uint64_t timestamp_us) {
    handleInterrupt(timestamp_us);
}

void A3144Tachometer::handleInterrupt(uint64_t timestamp_us) {
    const uint64_t previous_time = last_pulse_time_us_.load(std::memory_order_relaxed);

    if (previous_time != 0) {
        const uint64_t dt = timestamp_us - previous_time;

        // Придушення брязкоту контактів: відфільтровуємо імпульси з інтервалом меншим за debounce_interval_us
        if (dt < config_.debounce_interval_us) {
            return;
        }

        last_interval_us_.store(static_cast<uint32_t>(dt), std::memory_order_relaxed);
    }

    last_pulse_time_us_.store(timestamp_us, std::memory_order_relaxed);
    total_pulses_.fetch_add(1, std::memory_order_relaxed);
    new_pulse_flag_.store(true, std::memory_order_release);
}

void A3144Tachometer::update() {
    if (!is_initialized_) {
        return;
    }

    const uint64_t now_us = getSystemMicros();
    const uint64_t last_pulse = last_pulse_time_us_.load(std::memory_order_relaxed);
    const bool has_new_pulse = new_pulse_flag_.exchange(false, std::memory_order_acquire);

    // Відстеження таймауту відсутності обертання вала
    if (last_pulse != 0 && (now_us - last_pulse) > config_.timeout_us) {
        current_rpm_ = 0.0f;
    } else if (has_new_pulse) {
        const uint32_t dt_us = last_interval_us_.load(std::memory_order_relaxed);

        if (dt_us > 0 && config_.magnets_per_revolution > 0) {
            // Формула розрахунку RPM:
            // 60 000 000 мікросекунд в 1 хвилині
            // RPM = 60 000 000 / (dt_us * magnets_per_revolution)
            const float us_per_minute = 60000000.0f;
            current_rpm_ = us_per_minute / (static_cast<float>(dt_us) * config_.magnets_per_revolution);
        }

        if (user_callback_) {
            user_callback_(current_rpm_, total_pulses_.load(std::memory_order_relaxed));
        }
    }
}

void A3144Tachometer::registerCallback(TachometerCallback callback) {
    user_callback_ = std::move(callback);
}

float A3144Tachometer::getRPM() const noexcept {
    const uint64_t now_us = getSystemMicros();
    const uint64_t last_pulse = last_pulse_time_us_.load(std::memory_order_relaxed);

    if (last_pulse != 0 && (now_us - last_pulse) > config_.timeout_us) {
        return 0.0f;
    }
    return current_rpm_;
}

uint32_t A3144Tachometer::getPulseCount() const noexcept {
    return total_pulses_.load(std::memory_order_relaxed);
}

void A3144Tachometer::reset() noexcept {
    last_pulse_time_us_.store(0, std::memory_order_relaxed);
    last_interval_us_.store(0, std::memory_order_relaxed);
    total_pulses_.store(0, std::memory_order_relaxed);
    new_pulse_flag_.store(false, std::memory_order_relaxed);
    current_rpm_ = 0.0f;
}

void A3144Tachometer::setMagnetsPerRevolution(uint8_t count) noexcept {
    config_.magnets_per_revolution = (count > 0) ? count : 1;
}
