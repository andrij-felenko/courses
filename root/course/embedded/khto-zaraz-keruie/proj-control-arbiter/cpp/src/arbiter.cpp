#include "arbiter.hpp"

#include "diag_pin.hpp"

#include <algorithm>
#include <cmath>

namespace flight::control {
namespace {

constexpr float kTiltLimit = 1.0f;         // повний хід кутових каналів
constexpr float kSafeDescentThrust = 0.25f;// тяга керованого зниження без джерел
constexpr float kNominalDt = 0.0025f;      // 400 Гц — крок першого такту
constexpr float kMaxDt = 0.1f;             // довша пауза = цикл прострочив

/* Норма Чебишова: max(|roll|, |pitch|, |yaw|). Без sqrt — кілька тактів FPU
   (VABS.F32 + VMAXNM.F32), і чутливість осі не залежить від сусідніх. */
[[nodiscard]] float stick_deflection(const Setpoint& sp) noexcept {
    return std::max({std::abs(sp[Axis::Roll]),
                     std::abs(sp[Axis::Pitch]),
                     std::abs(sp[Axis::Yaw])});
}

/* NaN у каналі — не «дивне число», а вбитий процес джерела: у лімітері він за
   один такт отруїть вихід назавжди, бо всі порівняння з NaN хибні. */
[[nodiscard]] SubmitResult validate(const Setpoint& sp) noexcept {
    if (std::ranges::any_of(sp.ch, [](float v) { return !std::isfinite(v); }))
        return SubmitResult::NotFinite;
    for (auto axis : {Axis::Roll, Axis::Pitch, Axis::Yaw}) {
        if (std::abs(sp[axis]) > kTiltLimit)
            return SubmitResult::OutOfRange;
    }
    if (sp[Axis::Thrust] < 0.0f || sp[Axis::Thrust] > 1.0f)
        return SubmitResult::OutOfRange;
    return SubmitResult::Ok;
}

}  // namespace

ControlArbiter::ControlArbiter() noexcept {
    using namespace std::chrono_literals;
    /* Таймаути різні, бо різні темпи джерел: пульт шле 150 Гц, комп'ютер зору
       40 Гц, місія з наземної станції — раз на секунду. Запас щонайменше на три
       періоди: інакше джитер планувальника Linux на компаньйоні (сплеск
       завантаження, збирання сміття) вимикав би справне джерело. */
    slot(SourceId::Failsafe).config.timeout   = 1000ms;
    slot(SourceId::RcPilot).config.timeout    = 200ms;
    slot(SourceId::Offboard).config.timeout   = 100ms;
    slot(SourceId::GcsMission).config.timeout = 2000ms;
}

SubmitResult ControlArbiter::submit(SourceId id, const Setpoint& sp, Timestamp now) noexcept {
    if (static_cast<std::size_t>(id) >= kSourceCount)
        return SubmitResult::UnknownSource;

    if (const auto result = validate(sp); result != SubmitResult::Ok) {
        ++rejects_;
        return result;
    }

    auto& s = slot(id);
    /* Кадри йдуть різними каналами (UART, 4G) і легко переставляються місцями;
       старіший за вже прийнятий повернув би стару уставку. */
    if (s.has_data && sp.stamp < s.sp.stamp) {
        ++rejects_;
        return SubmitResult::StaleFrame;
    }

    s.sp = sp;
    // Серце б'ємо моментом ПРИЙОМУ, не міткою відправника: годинники бортів не синхронні.
    s.heartbeat = now;
    s.has_data = true;
    s.timed_out = false;
    return SubmitResult::Ok;
}

void ControlArbiter::raise_failsafe(float descent_thrust, Timestamp now) noexcept {
    auto& s = slot(SourceId::Failsafe);
    s.sp.stamp = now;
    s.sp[Axis::Roll] = 0.0f;   // горизонт
    s.sp[Axis::Pitch] = 0.0f;
    s.sp[Axis::Yaw] = 0.0f;
    s.sp[Axis::Thrust] = std::clamp(descent_thrust, 0.0f, 1.0f);
    s.heartbeat = now;
    s.has_data = true;
    s.timed_out = false;
    /* Засувка: аварія не має «розсмоктатися» від того, що монітор батареї
       замовк. Знімає її лише явний виклик — після посадки й розброєння. */
    failsafe_latched_ = true;
}

void ControlArbiter::clear_failsafe() noexcept {
    failsafe_latched_ = false;
    slot(SourceId::Failsafe).has_data = false;
    slot(SourceId::Failsafe).timed_out = true;
}

void ControlArbiter::update_watchdog(Timestamp now) noexcept {
    for (auto& s : slots_) {
        if (!s.has_data)
            continue;
        /* Годинник борту монотонний; якщо він усе-таки стрибнув назад, вважаємо
           кадр свіжим — краще зайвий такт довіри, ніж хибний таймаут. */
        const auto elapsed = (now > s.heartbeat) ? (now - s.heartbeat) : Timestamp{0};
        // Прапорець рахуємо щотакту наново: джерело, що ожило, повертається саме.
        s.timed_out = elapsed > s.config.timeout;
    }
}

bool ControlArbiter::is_live(SourceId id) const noexcept {
    if (static_cast<std::size_t>(id) >= kSourceCount)
        return false;
    const auto& s = slot(id);
    return s.has_data && !s.timed_out;
}

std::optional<SourceId> ControlArbiter::select() noexcept {
    // 1. Аварія — безумовно й поза чергою, стіків не питаємо.
    if (failsafe_latched_ && slot(SourceId::Failsafe).has_data)
        return SourceId::Failsafe;

    // 2. Пульт витісняє автономію лише коли пілот СПРАВДІ ворухнув ручку.
    if (is_live(SourceId::RcPilot)) {
        const auto& rc = slot(SourceId::RcPilot);
        deflection_ = stick_deflection(rc.sp);
        /* Гістерезис: увійшли на 0.08, тримаємося до 0.05. Без нього арбітр
           тремтів би на межі, перекидаючи авторитет туди-сюди щотакту. */
        const float threshold = override_latched_ ? rc.config.stick_deadband_exit
                                                  : rc.config.stick_deadband;
        const bool moved = deflection_ > threshold;
        if (moved && !override_latched_)
            diag_pin().raise();  // фронт для аналізатора: намір пілота помічено
        override_latched_ = moved;
        if (moved)
            return SourceId::RcPilot;
    } else {
        /* Пульт зник — засувку знімаємо, інакше після повернення зв'язку апарат
           лишився б у ручному режимі з невідомим положенням ручок. */
        deflection_ = 0.0f;
        override_latched_ = false;
    }

    // 3. Автономія за спаданням авторитету.
    if (is_live(SourceId::Offboard))
        return SourceId::Offboard;
    if (is_live(SourceId::GcsMission))
        return SourceId::GcsMission;

    // 4. Автономні мовчать — пульт бере керування навіть із центрованими ручками.
    if (is_live(SourceId::RcPilot))
        return SourceId::RcPilot;

    return std::nullopt;
}

ControlArbiter::Decision ControlArbiter::evaluate(Timestamp now) noexcept {
    update_watchdog(now);

    const auto selected = select();
    if (selected != active_) {
        active_ = selected;
        ++switches_;
    }

    float dt = kNominalDt;
    if (last_eval_.count() != 0 && now > last_eval_)
        dt = std::min(std::chrono::duration<float>(now - last_eval_).count(), kMaxDt);
    last_eval_ = now;

    std::array<float, kAxisCount> target{};
    const std::array<float, kAxisCount>* rate = nullptr;

    if (selected) {
        const auto& s = slot(*selected);
        target = s.sp.ch;
        rate = &s.config.max_slew_rate;
        output_valid_ = true;
    } else {
        /* Живих джерел не лишилося. Горизонтуємо апарат, а тягу ТІЛЬКИ
           зменшуємо до керованого зниження: обнулити її — вільне падіння,
           збільшити — розкрутити мотори на землі під час наладки. */
        target = {0.0f, 0.0f, 0.0f,
                  std::min(output_[Axis::Thrust], kSafeDescentThrust)};
        rate = &slot(SourceId::Failsafe).config.max_slew_rate;
        output_valid_ = false;
    }

    /* Лімітер похідної: |du| <= max_slew_rate * dt на кожному каналі. Саме він
       перетворює стрибок уставки при зміні джерела на плавний перехід і знімає
       ударний струм із мостів моторів та ривок із інтегральних ланок ПІД. */
    for (std::size_t i = 0; i < kAxisCount; ++i) {
        const float max_delta = (*rate)[i] * dt;
        const float delta = std::clamp(target[i] - output_.ch[i], -max_delta, max_delta);
        output_.ch[i] += delta;
    }
    output_[Axis::Thrust] = std::clamp(output_[Axis::Thrust], 0.0f, 1.0f);
    output_.stamp = now;

    return Decision{.source = selected,
                    .output = output_,
                    .valid = output_valid_,
                    .deflection = deflection_};
}

}  // namespace flight::control
