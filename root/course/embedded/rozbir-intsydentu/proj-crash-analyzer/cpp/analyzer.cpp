#include "analyzer.hpp"

#include <algorithm>
#include <cmath>
#include <deque>

namespace postmortem {
namespace {

// --- Пороги. Це фізика апарата, а не смак. ---

constexpr std::size_t kMinFrames = 30;
constexpr std::uint64_t kWindowSpanUs = 300'000; // 300 мс

constexpr float kMotorSatHigh = 0.98f;
constexpr float kMotorSatLow = 0.05f;
constexpr float kRollErrDeg = 20.0f;
constexpr std::size_t kMotorStreak = 15;         // ~150 мс при 100 Гц
constexpr float kShockAlphaRads2 = 150.0f;       // прискорення, яке дає лише удар
constexpr std::uint64_t kImpactLeadUs = 20'000;  // 20 мс випередження

constexpr float kMagInnovLimit = 0.45f;
constexpr float kMagCurrentA = 30.0f;
constexpr float kMagCurrentStepA = 8.0f;
constexpr float kYawErrDeg = 15.0f;
constexpr std::size_t kMagStreak = 20;

constexpr float kSagVoltageV = 13.2f;
constexpr float kSagSlopeVps = -4.0f;
constexpr float kSagCurrentA = 25.0f;
constexpr float kSagMinSpanS = 0.05f;

constexpr std::size_t kFreezeFrames = 25;
constexpr float kFlyingOutput = 0.15f;

// Рухоме вікно живе за ЧАСОМ, а не за кількістю кадрів: у зведеному журналі
// частота плаває, і 30 кадрів можуть накрити і 200 мс, і півсекунди.
using Window = std::deque<Frame>;

struct Detection {
    Fault fault;
    std::uint64_t timestamp_us;
    float confidence;
    std::string_view description;
};

// Контекст: те, що детектори відкинули, але мусять переказати нагору.
struct Context {
    std::optional<std::uint64_t> impact;
    std::optional<std::uint64_t> environment;
    std::optional<std::uint64_t> depletion;
};

// Кутова помилка з коректним переходом через ±180°: інакше курс 359° проти 1°
// дасть «розходження 358°», і кожен політ на північ читатиметься як відмова.
[[nodiscard]] float angle_error(float desired, float actual) noexcept
{
    float e = std::fmod(desired - actual, 360.0f);
    if (e > 180.0f) {
        e -= 360.0f;
    } else if (e < -180.0f) {
        e += 360.0f;
    }
    return std::abs(e);
}

// Пам'ять про різкий поштовх: живе рівно одне вікно.
class ShockTracker {
public:
    void feed(const Frame& now, const Frame& prev)
    {
        const float dt = static_cast<float>(now.timestamp_us - prev.timestamp_us) * 1e-6f;
        const float alpha = (now.gyro_x_rads - prev.gyro_x_rads) / dt;
        if (std::abs(alpha) > kShockAlphaRads2) {
            shock_us_ = now.timestamp_us;
        } else if (shock_us_ && now.timestamp_us - *shock_us_ > kWindowSpanUs) {
            shock_us_.reset();
        }
    }

    [[nodiscard]] std::optional<std::uint64_t> shock() const noexcept { return shock_us_; }

private:
    std::optional<std::uint64_t> shock_us_;
};

// --- 1. Відмова мотора або регулятора ---

class MotorDetector {
public:
    std::optional<Detection> feed(const Frame& f, std::optional<std::uint64_t> shock,
                                  Context& ctx)
    {
        // Діагональні пари квадрокоптера: виходи 1-2 і 3-4 нумерації ArduPilot.
        // Один уперся в стелю, протилежний скинуто в нуль — регулятор віддав
        // максимальний керівний момент, більше йому дати нічого.
        bool saturated = false;
        for (std::size_t a = 0; a + 1 < kMotorCount; a += 2) {
            const float hi = f.motor[a];
            const float lo = f.motor[a + 1];
            if ((hi > kMotorSatHigh && lo < kMotorSatLow) ||
                (lo > kMotorSatHigh && hi < kMotorSatLow)) {
                saturated = true;
            }
        }

        const float err = angle_error(f.roll_des_deg, f.roll_deg);
        if (!saturated || err < kRollErrDeg) {
            streak_ = 0;
            return std::nullopt;
        }

        if (streak_ == 0) {
            streak_ = 1;
            start_us_ = f.timestamp_us;
            start_err_ = err;
            prev_err_ = err;
            return std::nullopt;
        }

        // Помилка мусить рости монотонно. Просідання означає, що керування ще
        // тягне апарат назад, а насичення було різким маневром: серія рветься.
        if (err + 0.5f < prev_err_) {
            streak_ = 0;
            return std::nullopt;
        }
        prev_err_ = err;
        ++streak_;

        if (streak_ <= kMotorStreak || err <= start_err_) {
            return std::nullopt;
        }

        // Крайовий випадок: удар об перешкоду теж насичує мотори. Відрізняємо
        // за ПОРЯДКОМ подій. При ударі різкий сплеск гіроскопа передує
        // розкручуванню моторів; при відмові тяги розходження й насичення
        // народжуються разом, окремого поштовху перед ними немає.
        if (shock && *shock + kImpactLeadUs < start_us_) {
            if (!ctx.impact) {
                ctx.impact = *shock;
            }
            streak_ = 0;
            return std::nullopt;
        }

        return Detection{Fault::MotorEscLoss, start_us_, 0.98f,
                         "Відмова мотора або ESC: насичення 100%/0% на діагоналі "
                         "при кутовій помилці, що монотонно зростає"};
    }

private:
    std::size_t streak_{0};
    std::uint64_t start_us_{0};
    float start_err_{0.0f};
    float prev_err_{0.0f};
};

// --- 2. Магнітна завада силового струму ---

class MagneticDetector {
public:
    std::optional<Detection> feed(const Frame& f, const Window& win, Context& ctx)
    {
        const float yaw_err = angle_error(f.yaw_des_deg, f.yaw_deg);
        if (f.mag_innov <= kMagInnovLimit || yaw_err < kYawErrDeg) {
            streak_ = 0;
            return std::nullopt;
        }

        // Базовий струм — мінімум по вікну: сигнатура це саме СТРИБОК
        // споживання (крок газу), а не високий рівень сам по собі.
        const auto base_it = std::ranges::min_element(win, {}, &Frame::bat_current_a);
        const float base = base_it == win.end() ? f.bat_current_a : base_it->bat_current_a;

        const bool current_step = f.bat_current_a > kMagCurrentA &&
                                  f.bat_current_a - base > kMagCurrentStepA;
        if (!current_step) {
            // Крайовий випадок: нев'язка компаса росте, а власний струм — ні.
            // Значить, поле спотворює залізо ПІД апаратом (міст, дах, арматура),
            // а не силовий джгут на борту: аномалія середовища, не дефект.
            if (!ctx.environment) {
                ctx.environment = f.timestamp_us;
            }
            streak_ = 0;
            return std::nullopt;
        }

        if (streak_ == 0) {
            start_us_ = f.timestamp_us;
        }
        if (++streak_ <= kMagStreak) {
            return std::nullopt;
        }

        return Detection{Fault::MagneticInterference, start_us_, 0.92f,
                         "Розходження курсу від магнітного наведення силового струму "
                         "на компас: сплеск нев'язки збігся зі стрибком струму"};
    }

private:
    std::size_t streak_{0};
    std::uint64_t start_us_{0};
};

// --- 3. Динамічна просадка живлення ---

struct BrownoutDetector {
    std::optional<Detection> feed(const Frame& f, const Window& win, Context& ctx) const
    {
        if (win.size() < 2) {
            return std::nullopt;
        }
        const Frame& oldest = win.front();
        const float span_s =
            static_cast<float>(f.timestamp_us - oldest.timestamp_us) * 1e-6f;
        if (span_s < kSagMinSpanS) {
            return std::nullopt; // коротше вікно дає шумну похідну
        }
        const float slope = (f.bat_voltage_v - oldest.bat_voltage_v) / span_s;

        // Крайовий випадок: наприкінці польоту напруга теж опускається під поріг,
        // але зі швидкістю в десяті вольта на секунду й із попередженням про
        // заряд. Це нормальне вичерпання — позначаємо як контекст і йдемо далі.
        if (f.bat_voltage_v < kSagVoltageV && slope > kSagSlopeVps) {
            if (!ctx.depletion) {
                ctx.depletion = f.timestamp_us;
            }
            return std::nullopt;
        }

        if (slope >= kSagSlopeVps || f.bat_voltage_v >= kSagVoltageV ||
            f.bat_current_a < kSagCurrentA) {
            return std::nullopt;
        }

        // Мітка події — не мить перетину порогу, а останній кадр, на якому
        // напруга ще трималася: саме там почалося падіння.
        std::uint64_t start = f.timestamp_us;
        for (auto it = win.rbegin(); it != win.rend(); ++it) {
            if (it->bat_voltage_v >= kSagVoltageV) {
                break;
            }
            start = it->timestamp_us;
        }

        return Detection{Fault::BrownoutVoltageSag, start, 0.95f,
                         "Динамічна просадка живлення (brownout): dU/dt нижче "
                         "-4 В/с під струмовим кроком"};
    }
};

// --- 4. Зависання шини або мікросхеми давача ---

class FreezeDetector {
public:
    std::optional<Detection> feed(const Frame& f, const Frame& prev)
    {
        const bool flying = std::ranges::any_of(
            f.motor, [](float v) { return v > kFlyingOutput; });
        // На землі до армінгу апарат нерухомий, і збіг показів нічого не доводить.
        if (!flying) {
            streak_ = 0;
            return std::nullopt;
        }

        // Порівняння на точну рівність тут НАВМИСНЕ: у динаміці тепловий шум
        // MEMS-структури ворушить молодші розряди АЦП на кожному опитуванні,
        // тож побітово однакові відліки поспіль означають застиглий вихідний
        // регістр або втрату тактування шини, а не «тишу».
        if (f.gyro_x_rads != prev.gyro_x_rads) {
            streak_ = 0;
            return std::nullopt;
        }

        if (streak_ == 0) {
            start_us_ = prev.timestamp_us;
        }
        if (++streak_ < kFreezeFrames) {
            return std::nullopt;
        }

        return Detection{Fault::SensorBusLockup, start_us_, 0.90f,
                         "Застигання показів гіроскопа: 25 однакових відліків "
                         "поспіль у динамічному польоті"};
    }

private:
    std::size_t streak_{0};
    std::uint64_t start_us_{0};
};

} // namespace

Report analyze_incident(std::span<const Frame> frames)
{
    Report report;
    if (frames.size() < kMinFrames) {
        report.description = "Замало даних для формування вікна аналізу";
        return report;
    }

    Window window;
    Context ctx;
    MotorDetector motor;
    MagneticDetector magnetic;
    BrownoutDetector brownout;
    FreezeDetector freeze;
    ShockTracker shock;
    std::optional<Frame> prev;

    const auto emit = [&](const Detection& d) {
        report.fault = d.fault;
        report.timestamp_us = d.timestamp_us;
        report.confidence = d.confidence;
        report.description = d.description;
        report.impact_us = ctx.impact;
        report.environment_us = ctx.environment;
        report.depletion_us = ctx.depletion;
        return report;
    };

    for (const Frame& f : frames) {
        // Дубль кадру й стрибок часу назад після перезапуску EKF — звичайна
        // річ у сирому журналі. Такі кадри рахуємо, але не судимо.
        if (!f.finite() || (prev && f.timestamp_us <= prev->timestamp_us)) {
            ++report.frames_skipped;
            continue;
        }
        ++report.frames_used;

        window.push_back(f);
        while (window.size() > 1 &&
               f.timestamp_us - window.front().timestamp_us > kWindowSpanUs) {
            window.pop_front();
        }

        // Прапорець здоров'я — вирок самого драйвера: шина не відповіла.
        // Далі шукати нічого, решта каналів після цього недостовірна.
        if ((f.sensor_status & kImuHealthyBit) == 0) {
            return emit({Fault::SensorBusLockup, f.timestamp_us, 1.0f,
                         "Апаратна відмова шини IMU: драйвер зняв прапорець "
                         "здоров'я (таймаут I2C/SPI)"});
        }

        if (prev) {
            shock.feed(f, *prev);
        }

        if (auto d = brownout.feed(f, window, ctx)) {
            return emit(*d);
        }
        if (auto d = motor.feed(f, shock.shock(), ctx)) {
            return emit(*d);
        }
        if (auto d = magnetic.feed(f, window, ctx)) {
            return emit(*d);
        }
        if (prev) {
            if (auto d = freeze.feed(f, *prev)) {
                return emit(*d);
            }
        }

        prev = f;
    }

    report.impact_us = ctx.impact;
    report.environment_us = ctx.environment;
    report.depletion_us = ctx.depletion;
    return report;
}

} // namespace postmortem
