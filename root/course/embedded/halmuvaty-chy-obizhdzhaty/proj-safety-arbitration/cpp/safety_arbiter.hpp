#pragma once

#include <chrono>
#include <cmath>
#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

namespace nav::safety {

/* Фрейм — частина ТИПУ вектора. Тоді змішування odom із body не компілюється,
   а не проявляється в полі як повільне обертання машини навколо своєї осі. */
enum class Frame : std::uint8_t { Odom, Body };

template <Frame F>
struct Vec2 {
    float x{0.0f};
    float y{0.0f};

    [[nodiscard]] constexpr Vec2 operator+(Vec2 other) const noexcept
    {
        return { x + other.x, y + other.y };
    }

    [[nodiscard]] constexpr Vec2 operator*(float scale) const noexcept
    {
        return { x * scale, y * scale };
    }

    [[nodiscard]] float length() const noexcept { return std::hypot(x, y); }

    [[nodiscard]] bool finite() const noexcept
    {
        return std::isfinite(x) && std::isfinite(y);
    }
};

using OdomVec = Vec2<Frame::Odom>;
using BodyVec = Vec2<Frame::Body>;

[[nodiscard]] BodyVec toBody(OdomVec v, float yawRad) noexcept;
[[nodiscard]] OdomVec toOdom(BodyVec v, float yawRad) noexcept;

enum class Zone : std::uint8_t { Observation = 0, Warning, EmergencyStop };

[[nodiscard]] std::string_view zoneName(Zone zone) noexcept;

/* Часові величини — у chrono, а не в «кількості тактів»: період такту й
   період планувальника перерахуються в такти один раз, при створенні. */
struct Config {
    float maxDecel{2.5f};                          // гарантоване сповільнення, м/с²
    float stopMargin{0.40f};                       // геометричний зазор зупинки, м
    float warnBuffer{0.80f};                       // простір на бічний маневр, м
    float hystDistance{0.30f};                     // просторовий гістерезис, м
    std::chrono::milliseconds tick{10};            // період такту арбітра
    std::chrono::milliseconds reactionTime{50};    // затримка силового тракту
    std::chrono::milliseconds plannerPeriod{200};  // очікуваний період планувальника
    std::chrono::milliseconds holdTime{200};       // витримка перед деескалацією
};

enum class ConfigError : std::uint8_t {
    NonPositiveDeceleration,
    NegativeMargin,
    BadTiming
};

[[nodiscard]] std::string_view describe(ConfigError error) noexcept;

/* Дані давачів такту. nullopt — це не «вільно», а «валідних даних немає». */
struct Sensing {
    std::optional<float> minRange;
    float speed{0.0f};
};

struct Decision {
    BodyVec command{};
    Zone zone{Zone::EmergencyStop};
    float alpha{1.0f};
    float rStop{0.0f};
    float rWarn{0.0f};
    float vSafe{0.0f};
    bool overrideActive{true};  // сигнал низовому ПІ скинути інтеграл
    bool plannerStale{true};
};

class Arbiter {
public:
    /* Конструктор не може повернути помилку, тому фабрика: на борту без
       винятків єдиний чесний спосіб відмовитися від негодящого конфіга. */
    [[nodiscard]] static std::expected<Arbiter, ConfigError> create(const Config& cfg) noexcept;

    /* Свіжий план від бортового комп'ютера; заразом скидає сторожа. */
    void submitPlan(BodyVec planBody) noexcept;

    [[nodiscard]] Decision update(BodyVec reactBody, const Sensing& sensing) noexcept;

    [[nodiscard]] Zone zone() const noexcept { return zone_; }
    [[nodiscard]] float tickSeconds() const noexcept;

private:
    Arbiter(const Config& cfg, std::uint32_t holdTicks, std::uint32_t watchdogTicks) noexcept;

    void stepStateMachine(Zone instant, float dist, float rStop, float rWarn) noexcept;

    Config cfg_;
    std::uint32_t holdTicks_;
    std::uint32_t watchdogTicks_;
    std::uint32_t holdCounter_;
    std::uint32_t sinceLastPlan_{0};
    Zone zone_{Zone::Observation};
    BodyVec plan_{};
    bool plannerStale_{false};
};

}  // namespace nav::safety
