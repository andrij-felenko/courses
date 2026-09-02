#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

namespace ew {

using Millis = std::chrono::milliseconds;

enum class Threat : std::uint8_t {
    None = 0,        // ефір робочий
    WeakSignal,      // далеко або затінення корпусом: RSSI і SNR просіли РАЗОМ
    SpotJamming,     // прицільна завада на нашому каналі
    BarrageBlocking, // загороджувальна: вхідний тракт у насиченні
    PulseJamming,    // імпульсна завада
    GnssSpoofing     // підміна супутникового сигналу
};

[[nodiscard]] std::string_view name(Threat threat) noexcept;

// Одна вибірка телеметрії радіотракту. Тільки цілі числа: модуль мусить
// рахуватися на Cortex-M0+ без FPU.
struct RfSample {
    Millis       timestamp{};
    std::int16_t rssi_dbm{0};    // рівень ефіру, дБм
    std::int8_t  snr_db{0};      // сигнал/шум останнього кадру, дБ
    std::uint8_t agc_gain{255};  // 0 - мінімум/атенюатор, 255 - максимум LNA
    std::uint8_t throttle_pct{0};// сумарний газ двигунів, для відсіву завад ESC
    bool         preamble{false};
    bool         crc_error{false};
};

struct GnssSat {
    std::uint8_t  prn{0};
    std::uint16_t cnr_x10{0};       // CNR у десятих дБ-Гц (425 = 42.5)
    std::int16_t  doppler_hz{0};
    std::uint8_t  elevation_deg{0};
};

// Кадр сузір'я приходить чужим буфером — тримаємо на нього span, копіювати
// дванадцять структур на кожному циклі немає потреби.
struct GnssFrame {
    std::span<const GnssSat> sats{};
    bool clock_jump{false};
    bool position_jump_without_imu{false};
};

// Зведення по вікну: на ньому працює матриця правил, воно ж іде в телеметрію.
struct RfStats {
    std::uint8_t  samples{0};
    std::int16_t  avg_rssi_dbm{0};
    std::int8_t   avg_snr_db{0};
    std::uint8_t  avg_agc{0};
    std::uint8_t  per_pct{0};       // частка кадрів із помилкою CRC
    std::uint8_t  sync_hits{0};
    std::uint32_t rssi_variance{0}; // дБ²
    std::uint8_t  max_step_db{0};   // найбільший стрибок між СУСІДНІМИ вибірками
};

struct Verdict {
    Threat threat{Threat::None};
    Millis held{}; // скільки вердикт уже тримається без змін
};

class Detector {
public:
    static constexpr std::size_t kWindow = 16;  // ≈1.6 с за опитування 10 Гц
    static constexpr std::size_t kMinFill = 4;  // менше — вікно ще не прогріте

    void push(const RfSample& sample) noexcept;

    // gnss може бути порожнім, коли супутникового кадру цього циклу немає.
    [[nodiscard]] Verdict evaluate(const std::optional<GnssFrame>& gnss, Millis now) noexcept;

    // Порожньо, поки вікно не набрало kMinFill вибірок.
    [[nodiscard]] std::optional<RfStats> stats() const noexcept;

private:
    // k = 0 — найстаріша вибірка вікна. Порядок важливий: стрибок RSSI шукаємо
    // між сусідніми в ЧАСІ вибірками, а не між сусідніми клітинками масиву.
    [[nodiscard]] const RfSample& at(std::size_t k) const noexcept;
    [[nodiscard]] bool escNoiseSuspected() const noexcept;
    [[nodiscard]] Threat classify(const RfStats& stats) const noexcept;
    [[nodiscard]] static bool spoofed(const GnssFrame& gnss) noexcept;

    std::array<RfSample, kWindow> m_window{};
    std::size_t m_head{0};
    std::size_t m_count{0};
    Threat      m_threat{Threat::None};
    Millis      m_since{};
};

} // namespace ew
