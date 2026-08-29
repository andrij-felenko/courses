#include "calibration_blob.hpp"
#include "divider.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <print>

namespace {

/* Паспортні дані з розрахунку: дільник 100к/200к під вхід АЦП, Vref = 3.3 В. */
constexpr psu::DividerSpec spec{
    .r1Ohms = 100'000, .r2Ohms = 200'000, .vrefMv = 3300, .adcMaxCode = 4095};

/* Модель конкретної плати на столі: резистори з допуску 1% розбіглися в різні
   боки, а вбудований стабілізатор дає не рівно 3.300 В. Саме ці відхилення
   заводське калібрування й вилучає. У прошивці цього класу немає. */
struct Board {
    double r1Ohms;
    double r2Ohms;
    double vrefMv;

    [[nodiscard]] std::uint16_t sample(double vinMv, std::uint16_t adcMax) const noexcept {
        const double vPin = vinMv * r2Ohms / (r1Ohms + r2Ohms);
        const double code = std::clamp(vPin * adcMax / vrefMv, 0.0, static_cast<double>(adcMax));
        return static_cast<std::uint16_t>(code + 0.5);   // вхід АЦП насичується, а не рахує далі
    }
};

} // namespace

int main() {
    const Board board{.r1Ohms = 98'700.0, .r2Ohms = 201'500.0, .vrefMv = 3287.0};
    constexpr psu::Millivolt refLowMv = 1000;
    constexpr psu::Millivolt refHighMv = 4000;

    auto sensor = psu::BatterySense::create(spec);
    if (!sensor) {
        std::println(stderr, "паспорт каналу хибний: {}", psu::describe(sensor.error()));
        return 1;
    }

    // --- Заводський стенд: дві еталонні напруги з калібратора ---
    const psu::RefPoint low{board.sample(refLowMv, spec.adcMaxCode), refLowMv};
    const psu::RefPoint high{board.sample(refHighMv, spec.adcMaxCode), refHighMv};
    std::println("Еталонні точки: {} мВ -> код {}, {} мВ -> код {}",
                 low.trueMv, low.raw, high.trueMv, high.raw);

    const auto fitted = sensor->fitTwoPoint(low, high);
    if (!fitted) {
        // Плата не проходить заводський тест — далі по конвеєру вона не йде.
        std::println(stderr, "калібрування не вдалося: {}", psu::describe(fitted.error()));
        return 1;
    }
    std::println("Поправка: нахил {} ppm ({:+.3f}%), зсув {:+} мВ\n",
                 fitted->gainPpm,
                 (static_cast<double>(fitted->gainPpm) - 1'000'000.0) / 10'000.0,
                 fitted->offsetMv);

    /* --- Запис у EEPROM і читання назад при завантаженні прошивки ---
       Емуляція сторінки: у прошивці на її місці буде читання i2c-мікросхеми
       або сектора Flash, решта коду від цього не міняється. */
    const psu::nvm::Blob page = psu::nvm::pack(*fitted);
    const auto loaded = psu::nvm::unpack(page);
    if (loaded) {
        std::println("Читання з EEPROM: ok (нахил {} ppm, зсув {:+} мВ)",
                     loaded->gainPpm, loaded->offsetMv);
        if (const auto applied = sensor->setCalibration(*loaded); !applied) {
            std::println(stderr, "поправка відхилена: {}", psu::describe(applied.error()));
            return 1;
        }
    } else {
        std::println("Читання з EEPROM: {} -> працюємо на паспортних номіналах",
                     psu::nvm::describe(loaded.error()));
    }

    // --- Що буде, якщо сторінка побилася ---
    psu::nvm::Blob damaged = page;
    damaged[9] ^= std::byte{0x08};   // один перекинутий біт у полі нахилу
    const auto broken = psu::nvm::unpack(damaged);
    std::println("Побитий запис: {} -> працюємо на паспортних номіналах\n",
                 broken ? std::string_view{"ok"} : psu::nvm::describe(broken.error()));

    // --- Робота в полі: порівняння з поправкою і без неї ---
    const auto nominalSensor = psu::BatterySense::create(spec);   // паспортні номінали, поправки немає
    if (!nominalSensor) {
        std::println(stderr, "паспорт каналу хибний: {}", psu::describe(nominalSensor.error()));
        return 1;
    }

    std::println("  Vбат | код | без кал. | похиб. | з кал. | похиб.");
    std::println("  -----+-------+---------+--------+---------+-------");
    for (const psu::Millivolt trueMv : {3000, 3300, 3600, 3900, 4200}) {
        const std::uint16_t code = board.sample(trueMv, spec.adcMaxCode);
        const auto rawMv = nominalSensor->toMillivolts(code);
        const auto calMv = sensor->toMillivolts(code);
        if (!rawMv || !calMv) {
            std::println("  {:6} | {:5} | {}", trueMv, code,
                         psu::describe(rawMv ? calMv.error() : rawMv.error()));
            continue;
        }
        std::println("  {:6} | {:5} | {:7} | {:+6} | {:7} | {:+6}",
                     trueMv, code, *rawMv, *rawMv - trueMv, *calMv, *calMv - trueMv);
    }

    // --- Незручний випадок: драйвер АЦП віддав код поза роздільністю ---
    const auto overflow = sensor->toMillivolts(5000);
    std::println("\nКод 5000 при 12 бітах: {}",
                 overflow ? std::string_view{"ok"} : psu::describe(overflow.error()));
    return 0;
}
