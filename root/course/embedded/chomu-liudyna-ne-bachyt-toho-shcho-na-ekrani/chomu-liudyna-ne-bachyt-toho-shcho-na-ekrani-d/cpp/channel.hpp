#pragma once

#include <chrono>
#include <expected>
#include <optional>
#include <string>
#include <string_view>

namespace gcs {

using Millis = std::chrono::milliseconds;

enum class Severity { Normal, Warning, Critical };

// Куди від норми лежить небезпека: напруга банки падає, температура зростає.
enum class Danger { Rising, Falling };

// Причина, з якої вибірку не взяли до фільтра.
enum class SampleError { NotFinite, TimeWentBackwards };

struct Limits {
    float warn{};
    float crit{};
    float maxDriftRate{};                       // од/с у бік небезпеки; 0 — детектор вимкнено
    float hysteresis{};                         // на стільки треба відійти, щоб знизити рівень
    Millis staleAfter{std::chrono::seconds{3}}; // мовчання джерела довше — дані застигли
};

// Один телеметричний канал: значення, згладжена похідна, прогноз і рівень тривоги.
class Channel {
public:
    // Кидає std::invalid_argument, якщо ліміти суперечать напрямку небезпеки.
    Channel(std::string name, std::string unit, Danger danger, Limits limits);

    std::expected<Severity, SampleError> update(float raw, Millis now);
    void tick(Millis now) noexcept;

    [[nodiscard]] std::string_view name() const noexcept { return name_; }
    [[nodiscard]] std::string_view unit() const noexcept { return unit_; }
    [[nodiscard]] float value() const noexcept { return value_; }
    [[nodiscard]] float driftRate() const noexcept { return driftRate_; }
    [[nodiscard]] Severity severity() const noexcept { return severity_; }
    [[nodiscard]] bool stale() const noexcept { return stale_; }
    [[nodiscard]] const Limits& limits() const noexcept { return limits_; }

    // Порожньо — тренду до ліміту немає (стоїть або йде від межі).
    [[nodiscard]] std::optional<std::chrono::duration<float>> timeToLimit() const noexcept;
    [[nodiscard]] Millis silence(Millis now) const noexcept;

    // Рівень із урахуванням застиглих даних: жива на вигляд цифра — теж аномалія.
    [[nodiscard]] Severity effectiveSeverity() const noexcept;

private:
    [[nodiscard]] bool beyond(float v, float limit) const noexcept;
    [[nodiscard]] bool released(float v, float limit) const noexcept;
    [[nodiscard]] Severity rawLevel() const noexcept;
    void applyHysteresis(Severity next) noexcept;

    std::string name_;
    std::string unit_;
    Danger danger_;
    Limits limits_;

    float value_{0.0f};
    float driftRate_{0.0f};
    std::optional<std::chrono::duration<float>> toLimit_{};
    Severity severity_{Severity::Normal};
    bool stale_{false};
    std::optional<Millis> lastUpdate_{};

    static constexpr float kEmaAlpha{0.20f};
    static constexpr float kMinDt{0.005f};
    // Горизонт прогнозу — ті самі дві хвилини, що їх мав оператор у зав'язці статті.
    static constexpr float kCritHorizonS{120.0f};
};

std::string_view severityName(Severity s) noexcept;

} // namespace gcs
