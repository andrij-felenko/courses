// main.cpp — стендовий прогін Compass-Mot на моделі апарата.
//
// Замість плати тут крутиться модель стенда: газ → струм (з інерцією
// силової частини) → поле на магнітометрі (із затримкою дециматора) плюс
// шум. Істинні коефіцієнти нам відомі, тож наприкінці видно не лише те,
// що автомат відпрацював, а й наскільки точно він виміряв.
//
// На платі змінюється рівно один клас: BenchRig → драйвери шунта,
// магнітометра, ESC і EEPROM. Автомат і регресія лишаються ті самі.
#include "BenchRun.hpp"
#include "CompassMot.hpp"

#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>

using namespace compassmot;
using namespace std::chrono_literals;

namespace {

constexpr auto  kDt = 10ms;
constexpr float kDtSec = 0.010f;
constexpr float kCurrentCutoffHz = 12.0f;   // нижче зрізу — нема тонких піків
constexpr const char* kParamFile = "compass_mot.params";

class BenchRig final : public Rig {
public:
    BenchRig(Vector3 earth, Vector3 k_true, float full_current_a, float shunt_offset_a)
        : earth_{earth}, k_true_{k_true},
          full_current_a_{full_current_a}, shunt_offset_a_{shunt_offset_a} {}

    // Один такт фізики стенда.
    void tick()
    {
        // Тяга й струм ідуть за квадратом газу — звідси нелінійність по
        // газу і лінійність по струму, заради якої модель будують на I.
        const float duty = throttle_pct_ / 100.0f;
        const float target = full_current_a_ * duty * duty;

        // Інерція обертів і ємність силової шини: струм не стрибає.
        current_a_ += 0.18f * (target - current_a_);

        const Vector3 instant = earth_ + k_true_ * current_a_;
        // Магнітометр віддає усереднене за вікном дециматора значення —
        // саме тому струм теж доводиться фільтрувати.
        field_lagged_ = field_lagged_ + (instant - field_lagged_) * 0.30f;
    }

    Vector3 read_field() override
    {
        return field_lagged_ + Vector3{noise(0.35f), noise(0.35f), noise(0.35f)};
    }

    float read_current() override
    {
        return current_a_ + shunt_offset_a_ + noise(0.4f);
    }

    void set_throttle(float pct) override { throttle_pct_ = pct; }

    // Місце EEPROM/FRAM: на столі це файл, на платі — сторінка флешу.
    bool store(const Vector3& k) override
    {
        std::ofstream out{kParamFile, std::ios::trunc};
        out << std::fixed << std::setprecision(6)
            << "COMPASS_MOT_X " << k.x << '\n'
            << "COMPASS_MOT_Y " << k.y << '\n'
            << "COMPASS_MOT_Z " << k.z << '\n';
        out.close();
        // Помилка запису вилазить на закритті, а не на вставці: доти дані
        // лежать у буфері. Пропустити цю перевірку — типовий спосіб
        // «зберегти» калібрування в нікуди.
        return out.good();
    }

    [[nodiscard]] float current() const noexcept { return current_a_; }
    [[nodiscard]] const Vector3& earth() const noexcept { return earth_; }
    [[nodiscard]] const Vector3& truth() const noexcept { return k_true_; }
    void force_throttle(float pct) noexcept { throttle_pct_ = pct; }

private:
    float noise(float amplitude)
    {
        return std::uniform_real_distribution<float>{-amplitude, amplitude}(rng_);
    }

    Vector3 earth_;
    Vector3 k_true_;
    float   full_current_a_;
    float   shunt_offset_a_;
    Vector3 field_lagged_{};
    float   throttle_pct_{0.0f};
    float   current_a_{0.0f};
    std::mt19937 rng_{20260829u};
};

// Проганяємо газ ще раз і міряємо, наскільки поле лишається сталим до і
// після компенсації — це та сама горизонтальна крива з розбору логів.
void validate(BenchRig& rig, const Vector3& k)
{
    Compensator comp{k, std::chrono::duration<float>{kDtSec}, kCurrentCutoffHz, 200.0f};

    double err_raw = 0.0;
    double err_clean = 0.0;
    std::size_t n = 0;

    for (int step = 0; step <= 8; ++step) {
        rig.force_throttle(static_cast<float>(step) * 10.0f);
        for (int t = 0; t < 120; ++t) {          // 1.2 с на сходинку
            rig.tick();
            const Vector3 raw = rig.read_field();
            const float current = rig.read_current();
            const Vector3 clean = comp.compensate(raw, current);

            if (t < 40) {
                continue;                        // перехідний процес не рахуємо
            }
            const double dr = (raw - rig.earth()).norm();
            const double dc = (clean - rig.earth()).norm();
            err_raw   += dr * dr;
            err_clean += dc * dc;
            ++n;
        }
    }
    rig.force_throttle(0.0f);
    if (n == 0) {
        return;
    }

    std::cout << "\nКонтрольний прогін (" << n << " вибірок):\n"
              << std::fixed << std::setprecision(2)
              << "  відхилення поля до компенсації : "
              << std::sqrt(err_raw / static_cast<double>(n)) << " мкТл (RMS)\n"
              << "  відхилення поля після          : "
              << std::sqrt(err_clean / static_cast<double>(n)) << " мкТл (RMS)\n";
}

void print_vector(const char* label, const Vector3& v)
{
    std::cout << label << " = [ " << std::showpos << std::fixed << std::setprecision(4)
              << v.x << "  " << v.y << "  " << v.z << " ] мкТл/А\n" << std::noshowpos;
}

}  // namespace

int main()
{
    BenchRig rig{
        Vector3{21.5f, 1.2f, 43.8f},          // типовий вектор для наших широт
        Vector3{-0.128f, 0.061f, -0.212f},    // істинна чутливість
        118.0f,                               // струм при 100% газу
        0.0f                                  // спробуйте 3.0f — прогін впаде
    };

    BenchRun run{rig};
    Phase previous = run.phase();
    float previous_throttle = run.throttle();
    auto now = 0ms;

    // 30 с стелі на весь регламент — довше тримати стенд нема сенсу.
    for (int tick = 0; tick < 3000; ++tick, now += kDt) {
        rig.tick();
        const Phase phase = run.step(now);

        std::cout << std::fixed << std::setprecision(2);
        if (phase != previous) {
            std::cout << '[' << std::setw(6) << now.count() / 1000.0 << " с] "
                      << name(previous) << " → " << name(phase)
                      << "  газ " << std::setprecision(0) << run.throttle()
                      << "%  I=" << std::setprecision(1) << rig.current() << " А\n";
            previous = phase;
            previous_throttle = run.throttle();
        } else if (run.throttle() != previous_throttle) {
            std::cout << '[' << std::setw(6) << now.count() / 1000.0 << " с] "
                      << name(phase)
                      << "  газ " << std::setprecision(0) << run.throttle()
                      << "%  I=" << std::setprecision(1) << rig.current()
                      << " А  вибірок " << run.collected() << '\n';
            previous_throttle = run.throttle();
        }

        if (phase == Phase::Done || phase == Phase::Failed) {
            break;
        }
    }

    if (run.phase() != Phase::Done) {
        const std::string_view why = run.failure().empty()
                                         ? std::string_view{"вичерпано час прогону"}
                                         : run.failure();
        std::cerr << "\nКалібрування не завершилося: " << why << '\n';
        rig.set_throttle(0.0f);
        return 1;
    }

    const Fit& fit = *run.outcome();
    std::cout << "\nВибірок у регресії: " << fit.samples << '\n';
    print_vector("k     ", fit.k);
    print_vector("істина", rig.truth());
    std::cout << std::fixed << std::setprecision(4)
              << "R²     = [ " << fit.r2[0] << "  " << fit.r2[1] << "  " << fit.r2[2] << " ]\n"
              << std::setprecision(1)
              << "завада = " << fit.interference_pct << "% при I_max = " << fit.i_max
              << " А — " << verdict(fit.interference_pct) << '\n'
              << "параметри записано у " << kParamFile << '\n';

    validate(rig, fit.k);
    return 0;
}
