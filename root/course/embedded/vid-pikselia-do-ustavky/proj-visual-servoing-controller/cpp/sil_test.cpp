#include <chrono>
#include <cmath>
#include <cstdint>
#include <deque>
#include <print>
#include <random>

#include "controller.hpp"

/* SIL-перевірка замкненого контуру на синтетичній сходинці.
 *
 * Ціль стрибком з'являється під кутом +15°, апарат стоїть нерухомо. Камера
 * знімає на 30 Гц, кадр доходить до контролера через 100 мс (черга затримки
 * N = T_delay/dt = 10 кроків контуру), контур крутиться на 100 Гц, динаміка
 * апарата рахується з кроком 1 мс. */

namespace {

using namespace servo;
using namespace std::chrono_literals;

constexpr auto kSimStep = 1ms;
constexpr auto kControlPeriod = 10ms;
constexpr auto kFramePeriod = std::chrono::microseconds{33333};   /* 30 кадрів/с */
constexpr auto kCameraDelay = 100ms;
constexpr auto kSimTime = 3s;

constexpr float kStepRad = 0.2618f;                    /* +15° */
constexpr float kSettleBand = 0.05f * kStepRad;        /* коридор ±5% */
constexpr float kLimitCycleBand = 0.01f * kStepRad;

/* Динаміка апарата за рисканням: внутрішній контур відпрацьовує уставку
 * кутової швидкості моментом, аеродинаміка гальмує. */
struct AirframeYaw {
    float inertia{0.02f};      /* момент інерції, кг·м² */
    float inner_gain{8.0f};    /* коефіцієнт внутрішнього контуру, 1/с */
    float drag{0.8f};          /* аеродинамічне демпфування, 1/с */
    float angle{0.0f};
    float rate{0.0f};

    void step(float commanded_rate, Seconds dt) {
        const float h = dt.count();
        const float torque = inertia * inner_gain * (commanded_rate - rate);
        rate += (torque / inertia - drag * rate) * h;
        angle += rate * h;
    }
};

}  // namespace

int main() {
    const CameraIntrinsics camera{};
    VisualServoingController controller{camera};

    /* Черга затримки: кадр стає видимим контролеру лише коли настав його час. */
    std::deque<std::pair<TimePoint, TargetDetection>> delay_line;

    /* Детермінований шум детектора: той самий прогін дає те саме число. */
    std::mt19937 rng{12345};
    std::normal_distribution<float> pixel_noise{0.0f, 1.2f};

    AirframeYaw airframe{};
    const float target_bearing = kStepRad;
    const TimePoint start{1s};       /* нульова мітка часу вважалася б «немає мітки» */

    float commanded_rate = 0.0f;
    auto next_frame = start;
    float settle_time = -1.0f;
    float max_angle = 0.0f;
    float tail_min = 1e9f;
    float tail_max = -1e9f;
    unsigned frames_sent = 0;

    const int steps = static_cast<int>(kSimTime / kSimStep);
    for (int step = 0; step < steps; ++step) {
        const auto now = start + step * kSimStep;
        const float t_s = Seconds(now - start).count();
        const float los = target_bearing - airframe.angle;

        /* Експозиція кадру: піксель рахуємо за тією самою моделлю камери,
         * що й контролер, але від ІСТИННОГО кута плюс шум. */
        if (now >= next_frame) {
            next_frame += kFramePeriod;
            const float u = camera.cx + camera.fx * std::tan(los) + pixel_noise(rng);
            const float v = camera.cy + pixel_noise(rng);
            if (u >= 0.0f && u <= camera.img_width) {
                delay_line.emplace_back(now + kCameraDelay,
                                        TargetDetection{.u = u, .v = v,
                                                        .width = 80.0f, .height = 80.0f,
                                                        .captured = now});
                ++frames_sent;
            }
            /* Виїзд цілі за край кадру — легітимна відмова детектора:
             * контролер має дожити до таймаута, а не зламатися. */
        }

        while (!delay_line.empty() && delay_line.front().first <= now) {
            controller.on_detection(delay_line.front().second);
            delay_line.pop_front();
        }

        if (step % (kControlPeriod / kSimStep) == 0) {
            /* Гіроскоп бачить власну кутову швидкість апарата. */
            const auto result = controller.update(now, BodyRates{.yaw = airframe.rate});
            commanded_rate = result ? result->yaw_rate_rad_s : 0.0f;
        }

        airframe.step(commanded_rate, Seconds(kSimStep));

        max_angle = std::max(max_angle, airframe.angle);
        if (std::abs(los) > kSettleBand) {
            settle_time = -1.0f;        /* вибили з коридору — відлік наново */
        } else if (settle_time < 0.0f) {
            settle_time = t_s;
        }
        if (t_s > Seconds(kSimTime).count() - 1.0f) {   /* стаціонарний режим */
            tail_min = std::min(tail_min, airframe.angle);
            tail_max = std::max(tail_max, airframe.angle);
        }
    }

    const float overshoot = 100.0f * (max_angle - target_bearing) / target_bearing;
    const float peak_to_peak = tail_max - tail_min;

    const bool ok_settle = settle_time >= 0.0f && settle_time < 0.75f;
    const bool ok_overshoot = overshoot < 12.0f;
    const bool ok_limit = peak_to_peak < kLimitCycleBand;

    std::println("кадрів віддано:   {} (використано {}, відкинуто {})",
                 frames_sent, controller.frames_used(), controller.frames_rejected());
    std::println("час установлення: {:.3f} с   (норма < 0.75)  {}",
                 settle_time, ok_settle ? "ГАРАЗД" : "ЗАВАЛЕНО");
    std::println("перерегулювання:  {:.2f} %    (норма < 12)    {}",
                 overshoot, ok_overshoot ? "ГАРАЗД" : "ЗАВАЛЕНО");
    std::println("розмах у кінці:   {:.5f} рад (норма < {:.5f}) {}",
                 peak_to_peak, kLimitCycleBand, ok_limit ? "ГАРАЗД" : "АВТОКОЛИВАННЯ");

    return (ok_settle && ok_overshoot && ok_limit) ? 0 : 1;
}
