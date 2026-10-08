#ifndef SS41F_HALL_DECODER_HPP
#define SS41F_HALL_DECODER_HPP

#include <cstdint>
#include <cstddef>
#include <functional>
#include <array>
#include <utility>

namespace bldc {

/**
 * @brief Шаблонізований кільцевий буфер часових міток для розрахунку швидкості.
 * 
 * Використовується в контексті переривань (ISR) для накопичення інтервалів часу (в мкс)
 * між послідовними спрацьовуваннями датчиків Холла. Дозволяє згладжувати обчислення RPM
 * без використання затримок та плаваючої крапки.
 */
template <typename T, std::size_t Capacity>
class TimestampRingBuffer {
public:
    TimestampRingBuffer() = default;

    void push(T item) noexcept {
        buffer_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    void clear() noexcept {
        head_ = 0;
        count_ = 0;
        buffer_.fill(T{0});
    }

    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return Capacity; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] bool full() const noexcept { return count_ == Capacity; }

    [[nodiscard]] T sum() const noexcept {
        T total{0};
        for (std::size_t i = 0; i < count_; ++i) {
            total += buffer_[i];
        }
        return total;
    }

    [[nodiscard]] T average() const noexcept {
        if (count_ == 0) {
            return T{0};
        }
        return sum() / static_cast<T>(count_);
    }

private:
    std::array<T, Capacity> buffer_{};
    std::size_t head_{0};
    std::size_t count_{0};
};

/**
 * @brief Логічний стан виходів трьох датчиків Холла SS41F (3-бітний код: HallA | HallB | HallC).
 */
enum class HallState : uint8_t {
    Invalid_000 = 0b000,
    S6_001      = 0b001,
    S4_010      = 0b010,
    S5_011      = 0b011,
    S2_100      = 0b100,
    S1_101      = 0b101,
    S3_110      = 0b110,
    Invalid_111 = 0b111
};

/**
 * @brief Електричний сектор положення ротора BLDC-двигуна (1..6).
 */
enum class RotorSector : uint8_t {
    Unknown = 0,
    Sector1 = 1, // 0°   - 60°
    Sector2 = 2, // 60°  - 120°
    Sector3 = 3, // 120° - 180°
    Sector4 = 4, // 180° - 240°
    Sector5 = 5, // 240° - 300°
    Sector6 = 6  // 300° - 360°
};

/**
 * @brief Напрямок обертання ротора.
 */
enum class RotationDirection : int8_t {
    Unknown = 0,
    Forward = 1,  // Пряме обертання (за годинниковою стрілкою / CW)
    Reverse = -1  // Зворотне обертання (проти годинникової стрілки / CCW)
};

/**
 * @brief Діагностичні помилки декодера сигналів SS41F.
 */
enum class DecoderError : uint8_t {
    None = 0,
    InvalidHallState,        // Заборонена комбінація сигналів (000 або 111)
    IllegalStateTransition,  // Перескок через сектор або недозволений перехід
    SensorTimeout            // Ротор зупинився (перевищено таймаут між перериваннями)
};

/**
 * @brief Структура телеметрії ротора.
 */
struct RotorTelemetry {
    RotorSector current_sector{RotorSector::Unknown};
    RotorSector previous_sector{RotorSector::Unknown};
    RotationDirection direction{RotationDirection::Unknown};
    uint32_t speed_rpm{0};
    uint32_t state_change_count{0};
    uint32_t last_transition_us{0};
    DecoderError last_error{DecoderError::None};
    uint32_t error_count{0};
};

/**
 * @brief Клас-декодер сигналів трифазної системи цифрових датчиків Холла SS41F.
 */
class Ss41fHallDecoder {
public:
    using SectorChangeCallback = std::function<void(const RotorTelemetry&)>;
    using ErrorCallback = std::function<void(DecoderError, uint8_t raw_code)>;

    explicit Ss41fHallDecoder(uint8_t pole_pairs = 1);
    ~Ss41fHallDecoder() = default;

    Ss41fHallDecoder(const Ss41fHallDecoder&) = delete;
    Ss41fHallDecoder& operator=(const Ss41fHallDecoder&) = delete;
    Ss41fHallDecoder(Ss41fHallDecoder&&) = default;
    Ss41fHallDecoder& operator=(Ss41fHallDecoder&&) = default;

    /**
     * @brief Головний обробник події зміни стану датчиків Холла (викликається з ISR).
     * @param raw_hall_code 3-бітне значення пінів (HallA << 2 | HallB << 1 | HallC)
     * @param timestamp_us Поточна апаратна часова мітка у мікросекундах
     */
    void process_hall_change(uint8_t raw_hall_code, uint32_t timestamp_us);

    /**
     * @brief Перевірка таймауту обертання ротора (для фіксації зупинки двигуна).
     * @param current_timestamp_us Поточна часова мітка у мікросекундах
     * @param timeout_us Поріг таймауту у мікросекундах (за замовчуванням 1 сек = 1 000 000 мкс)
     */
    void check_timeout(uint32_t current_timestamp_us, uint32_t timeout_us = 1000000);

    /**
     * @brief Скидання внутрішнього стану декодера та буферів.
     */
    void reset();

    /**
     * @brief Декодування 3-бітного коду SS41F у відповідний сектор.
     */
    [[nodiscard]] RotorSector decode_sector(uint8_t raw_hall_code) const noexcept;

    /**
     * @brief Отримання поточної телеметрії ротора.
     */
    [[nodiscard]] RotorTelemetry get_telemetry() const noexcept { return telemetry_; }

    /**
     * @brief Встановлення колбека на зміну сектора.
     */
    void set_sector_change_callback(SectorChangeCallback cb) { sector_cb_ = std::move(cb); }

    /**
     * @brief Встановлення колбека на помилку декодування.
     */
    void set_error_callback(ErrorCallback cb) { error_cb_ = std::move(cb); }

    /**
     * @brief Встановлення кількості пар полюсів двигуна.
     */
    void set_pole_pairs(uint8_t pole_pairs) noexcept { pole_pairs_ = (pole_pairs > 0) ? pole_pairs : 1; }

private:
    [[nodiscard]] bool validate_transition(RotorSector prev, RotorSector curr, RotationDirection& out_dir) const noexcept;
    [[nodiscard]] uint32_t calculate_rpm(uint32_t delta_us) noexcept;

    RotorTelemetry telemetry_{};
    TimestampRingBuffer<uint32_t, 6> dt_buffer_{};
    uint8_t pole_pairs_{1};

    SectorChangeCallback sector_cb_{nullptr};
    ErrorCallback error_cb_{nullptr};
};

} // namespace bldc

#endif // SS41F_HALL_DECODER_HPP
