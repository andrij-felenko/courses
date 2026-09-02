// Демонстраційний стенд арбітра: 100-герцовий цикл, модель апарата,
// планувальник на 5 Гц із вікном мовчання і далекомір із шумом та збоєм.

#include "safety_arbiter.hpp"

#include <cmath>
#include <format>
#include <iostream>
#include <random>

namespace {

using nav::safety::BodyVec;
using nav::safety::OdomVec;

constexpr int kSimTicks = 600;
constexpr float kCruise = 6.0f;          // м/с
constexpr float kYawRad = 0.60f;         // курс апарата відносно odom
constexpr float kSensorMaxRange = 30.0f; // м
constexpr float kSensorNoise = 0.05f;    // м
constexpr float kObstacleX = 25.0f;
constexpr float kObstacleY = 0.0f;
constexpr float kObstacleRadius = 0.5f;
constexpr int kPlannerEveryTicks = 20;   // 5 Гц
constexpr int kPlannerMuteFrom = 60;
constexpr int kPlannerMuteTo = 120;
constexpr int kSensorFaultFrom = 180;
constexpr int kSensorFaultTo = 186;

// Поздовжній ПІ-регулятор швидкості — саме він страждає від windup.
class SpeedPi {
public:
    float step(float target, float actual, bool resetIntegral, float aMax, float dt) noexcept
    {
        if (resetIntegral) {
            // На вході в ESTOP інтеграл обнуляється: поки апарат стоїть,
            // сума помилки росла б, і на виході з аварії дала б ривок.
            integral_ = 0.0f;
        }
        const float err = target - actual;
        integral_ = std::clamp(integral_ + kKi * err * dt, -aMax, aMax);
        return std::clamp(kKp * err + integral_, -aMax, aMax);
    }

private:
    static constexpr float kKp = 8.0f;
    static constexpr float kKi = 4.0f;
    float integral_{0.0f};
};

}  // namespace

int main()
{
    using namespace nav::safety;

    const Config cfg{};  // типовий ровер: 2.5 м/с², план 5 Гц, такт 10 мс
    auto created = Arbiter::create(cfg);
    if (!created) {
        std::cerr << "Arbiter::create: " << describe(created.error()) << '\n';
        return 1;
    }
    Arbiter arbiter = std::move(*created);
    const float dt = arbiter.tickSeconds();

    OdomVec pos{0.0f, 0.0f};
    OdomVec vel{kCruise, 0.0f};
    OdomVec heading{1.0f, 0.0f};  // напрямок, який тримаємо при нульовій уставці
    SpeedPi speedPi;
    Zone prevZone = Zone::Observation;

    // Фіксоване зерно: демо має відтворюватися від запуску до запуску.
    std::mt19937 rng{20260830u};
    std::uniform_real_distribution<float> noise{-kSensorNoise, kSensorNoise};

    std::cout << "тік   t,с   зазор  R_stop R_warn  зона        alpha  |v_cmd|  швидк.  прапорці\n";

    for (int tick = 0; tick < kSimTicks; ++tick) {
        // --- Планувальник: 5 Гц у глобальному фреймі, з вікном мовчання ---
        const bool muted = (tick >= kPlannerMuteFrom && tick <= kPlannerMuteTo);
        if (!muted && tick % kPlannerEveryTicks == 0) {
            arbiter.submitPlan(toBody(OdomVec{kCruise, 0.0f}, kYawRad));
        }

        // --- Далекомір ---
        const OdomVec relOdom{kObstacleX - pos.x, kObstacleY - pos.y};
        const float gap = std::max(0.0f, relOdom.length() - kObstacleRadius);
        const bool sensorFault = (tick >= kSensorFaultFrom && tick <= kSensorFaultTo);
        // Немає відлуння — у межах дальності чисто; це не те саме, що збій давача,
        // і різниця виражена типом: nullopt означає саме «даних немає».
        Sensing sensing{};
        if (!sensorFault) {
            sensing.minRange = (gap > kSensorMaxRange) ? kSensorMaxRange
                                                       : std::max(0.0f, gap + noise(rng));
        }
        sensing.speed = vel.length();

        // --- Рефлекс: обхід перешкоди по лівій нормалі, у body-фреймі ---
        const BodyVec relBody = toBody(relOdom, kYawRad);
        const float relLen = relBody.length();
        BodyVec react{};
        if (relLen > 1e-3f) {
            // Сторона обходу фіксована навмисно: коли перешкода строго по курсу,
            // вибір боку — підкидання монети, а рефлекс не має права
            // передумувати щотакту, інакше апарат затанцює на місці.
            react = BodyVec{-relBody.y / relLen, relBody.x / relLen} * kCruise;
        }

        const Decision decision = arbiter.update(react, sensing);

        // --- Виконавчий рівень: уставка з body назад в odom ---
        const OdomVec cmdOdom = toOdom(decision.command, kYawRad);
        const float cmdLen = cmdOdom.length();
        if (cmdLen > 1e-3f) {
            heading = OdomVec{cmdOdom.x / cmdLen, cmdOdom.y / cmdLen};
        }
        const float accel = speedPi.step(cmdLen, sensing.speed, decision.overrideActive,
                                         cfg.maxDecel, dt);
        const float newSpeed = std::max(0.0f, sensing.speed + accel * dt);
        // Модель голономна: справжній ровер довертався б кермом, тут напрямок
        // міняється миттєво — для демонстрації арбітражу цього досить.
        vel = heading * newSpeed;
        pos = pos + vel * dt;

        if (tick % 10 == 0 || decision.zone != prevZone) {
            std::cout << std::format(
                "{:4} {:5.2f} {:7.2f} {:6.2f} {:6.2f}  {:<11} {:5.2f} {:8.2f} {:7.2f}  {}{}{}\n",
                tick, static_cast<float>(tick) * dt, gap, decision.rStop, decision.rWarn,
                zoneName(decision.zone), decision.alpha, cmdLen, newSpeed,
                decision.overrideActive ? "OVERRIDE " : "",
                decision.plannerStale ? "PLAN-STALE " : "",
                sensorFault ? "SENSOR-FAULT" : "");
        }
        prevZone = decision.zone;
    }

    std::cout << std::format("\nфініш: x={:.2f} м, y={:.2f} м, швидкість {:.2f} м/с\n",
                             pos.x, pos.y, vel.length());
    return 0;
}
