#include "arbiter.hpp"
#include "diag_pin.hpp"
#include "mailbox.hpp"

#include <array>
#include <cstddef>
#include <format>
#include <iostream>
#include <limits>
#include <string>
#include <string_view>

namespace {

using namespace flight::control;
using namespace std::chrono_literals;

/* Крок стенда — 25 мс: рівно з таким періодом шле уставки комп'ютер зору, і на
   такому кроці роботу лімітера видно оком. На борту evaluate() кличуть кожні
   2.5 мс (400 Гц) — логіка та сама, кроки лімітера вдесятеро дрібніші. */
constexpr auto kTick = 25ms;

class Bench {
public:
    /* Імітація обробника переривання приймача CRSF / MAVLink: кадр лягає у
       скриньку й НЕ торкається арбітра — арбітр живе тільки в польотному циклі. */
    void isr_frame(SourceId src, float roll, float pitch, float yaw,
                   float thrust, Timestamp now) noexcept {
        const Setpoint sp{.stamp = now, .ch = {roll, pitch, yaw, thrust}};
        mail_[static_cast<std::size_t>(src)].publish(sp);
    }

    // Один такт польотного циклу: забрати кадри, розсудити, віддати мікшеру.
    void flight_cycle(Timestamp now) {
        const DiagPin::ScopedLow pulse_end{diag_pin()};

        for (std::size_t i = 0; i < kSourceCount; ++i) {
            const auto frame = mail_[i].take();
            if (!frame)
                continue;
            const auto src = static_cast<SourceId>(i);
            if (const auto result = arbiter_.submit(src, *frame, now);
                result != SubmitResult::Ok) {
                std::cout << std::format("          кадр від {} відкинуто: {}\n",
                                         name(src), name(result));
            }
        }

        const auto decision = arbiter_.evaluate(now);
        // Тут уставка йде в мікшер моторів і далі в DShot-кадр.
        log_record(now, decision);
    }

    [[nodiscard]] ControlArbiter& arbiter() noexcept { return arbiter_; }
    [[nodiscard]] Mailbox<Setpoint>& mail(SourceId src) noexcept {
        return mail_[static_cast<std::size_t>(src)];
    }

private:
    /* Рядок чорної скриньки: активне джерело, відхилення стіків і стан сторожів —
       без цих трьох полів розслідувати інцидент у польоті нічим. */
    void log_record(Timestamp now, const ControlArbiter::Decision& d) {
        std::string live;
        for (std::size_t i = 0; i < kSourceCount; ++i) {
            const auto src = static_cast<SourceId>(i);
            live += std::format("{}:{} ", name(src), arbiter_.is_live(src) ? "ok" : "--");
        }
        std::cout << std::format(
            "[{:6.3f}s] {:8} defl={:.3f} | roll={:+.3f} pitch={:+.3f} yaw={:+.3f} "
            "thr={:.3f} | {}{}\n",
            std::chrono::duration<double>(now).count(),
            d.source ? name(*d.source) : std::string_view{"немає"},
            d.deflection, d.output[Axis::Roll], d.output[Axis::Pitch],
            d.output[Axis::Yaw], d.output[Axis::Thrust],
            live, d.valid ? "" : "[вихід недійсний]");
    }

    ControlArbiter arbiter_{};
    std::array<Mailbox<Setpoint>, kSourceCount> mail_{};
};

}  // namespace

int main() {
    Bench bench;
    auto now = Timestamp{1'000'000};  // 1.000 с від старту борту

    std::cout << "=== ДИСПЕТЧЕР ПРІОРИТЕТІВ ДЖЕРЕЛ КЕРУВАННЯ ===\n\n";

    std::cout << "-- 1. Автономний політ: пульт живий, ручки в центрі — керує комп'ютер зору\n";
    bench.isr_frame(SourceId::GcsMission, 0.0f, 0.05f, 0.0f, 0.50f, now);
    bench.isr_frame(SourceId::RcPilot,    0.0f, 0.00f, 0.0f, 0.50f, now);
    bench.isr_frame(SourceId::Offboard,   0.35f, 0.00f, 0.0f, 0.55f, now);
    bench.flight_cycle(now);

    std::cout << "-- 2. Процес зору впав: кадр із NaN відкинуто, серце слоту не б'ється\n";
    now += kTick;
    bench.isr_frame(SourceId::RcPilot, 0.0f, 0.0f, 0.0f, 0.50f, now);
    bench.isr_frame(SourceId::Offboard, 0.35f,
                    std::numeric_limits<float>::quiet_NaN(), 0.0f, 0.55f, now);
    bench.flight_cycle(now);

    std::cout << "-- 3. Перед апаратом трос: пілот смикає тангаж на 0.78 рад\n";
    now += kTick;
    bench.isr_frame(SourceId::RcPilot, 0.0f, 0.78f, 0.0f, 0.70f, now);
    bench.flight_cycle(now);

    std::cout << "-- 4. Безударне наростання: крок лімітера 6.0 * 0.025 = 0.15 рад\n";
    for (int step = 0; step < 4; ++step) {
        now += kTick;
        bench.isr_frame(SourceId::RcPilot, 0.0f, 0.78f, 0.0f, 0.70f, now);
        bench.flight_cycle(now);
    }

    std::cout << "-- 5. Банка просіла до 3.2 В: аварійний автомат витісняє й пілота\n";
    now += 10ms;
    bench.arbiter().raise_failsafe(0.30f, now);
    bench.isr_frame(SourceId::RcPilot, 0.0f, 0.78f, 0.0f, 0.70f, now);  // стік досі відхилено
    bench.flight_cycle(now);
    for (int step = 0; step < 3; ++step) {
        now += kTick;
        bench.isr_frame(SourceId::RcPilot, 0.0f, 0.78f, 0.0f, 0.70f, now);
        bench.flight_cycle(now);
    }

    std::cout << std::format("\nперемикань авторитету: {}, відкинутих кадрів: {}\n",
                             bench.arbiter().switch_count(),
                             bench.arbiter().reject_count());
    std::cout << std::format(
        "реакція на стік: остання {} мкс, найгірша {} мкс, імпульсів {} (бюджет такту 2500 мкс)\n",
        diag_pin().last().count(), diag_pin().worst().count(), diag_pin().pulses());
    std::cout << std::format("скринька offboard: пропущено циклом {}, рваних копій {}\n",
                             bench.mail(SourceId::Offboard).dropped(),
                             bench.mail(SourceId::Offboard).torn());
    return 0;
}
