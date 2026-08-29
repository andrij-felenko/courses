#pragma once

#include <cstdint>
#include <expected>
#include <string_view>

namespace psu {

/* Напруга всередині вузла — цілі мілівольти: мікроконтролер без FPU
   не має чим множити double, а мілівольта тут вистачає з головою. */
using Millivolt = std::int32_t;

enum class SenseError {
    badSpec,          // нульові номінали, Vref або роздільність АЦП
    rawOutOfRange,    // код більший за роздільність АЦП
    gainOutOfBand,    // нахил поза смугою — плата зібрана не так
    badCalPoints      // еталонні точки збіглися або йдуть у зворотному порядку
};

[[nodiscard]] std::string_view describe(SenseError err) noexcept;

/* Паспортні дані вузла — те, що інженер порахував і поклав у специфікацію. */
struct DividerSpec {
    std::uint32_t r1Ohms{100'000};
    std::uint32_t r2Ohms{200'000};
    std::uint16_t vrefMv{3300};
    std::uint16_t adcMaxCode{4095};
};

/* Заводська поправка: mv = nominal * gainPpm / 1e6 + offsetMv.
   Спершу нахил, потім зсув — рівно в тому порядку, у якому їх обчислює
   BatterySense::fitTwoPoint(); інший порядок дав би інші коефіцієнти. */
struct Calibration {
    static constexpr std::uint32_t unityPpm = 1'000'000;
    /* Смуга здорового глузду: допуск 1%, дрейф і старіння дають одиниці
       відсотків. Нахил 0.8 чи 1.25 означає не похибку, а впаяний не той
       номінал або еталон, поданий не на той вивід. */
    static constexpr std::uint32_t minPpm = 800'000;
    static constexpr std::uint32_t maxPpm = 1'250'000;

    std::uint32_t gainPpm{unityPpm};
    Millivolt offsetMv{0};

    [[nodiscard]] constexpr bool plausible() const noexcept {
        return gainPpm >= minPpm && gainPpm <= maxPpm;
    }
};

/* Еталонна точка заводського стенда: подали точну напругу — зчитали сирий код. */
struct RefPoint {
    std::uint16_t raw{};
    Millivolt trueMv{};
};

class BatterySense {
public:
    /* Єдиний спосіб отримати об'єкт: конструктор мовчки прийняв би дільник
       з нулем у знаменнику, а std::expected змушує виклик подивитися на помилку. */
    [[nodiscard]] static std::expected<BatterySense, SenseError>
    create(DividerSpec spec, Calibration cal = {}) noexcept;

    [[nodiscard]] std::expected<Millivolt, SenseError>
    toMillivolts(std::uint16_t raw) const noexcept;

    [[nodiscard]] std::expected<Calibration, SenseError>
    fitTwoPoint(RefPoint low, RefPoint high) const noexcept;

    [[nodiscard]] std::expected<void, SenseError>
    setCalibration(Calibration cal) noexcept;

    [[nodiscard]] const Calibration& calibration() const noexcept { return cal_; }
    [[nodiscard]] const DividerSpec& spec() const noexcept { return spec_; }

private:
    BatterySense(DividerSpec spec, Calibration cal) noexcept : spec_{spec}, cal_{cal} {}

    /* Нескалібрована напруга за паспортними номіналами. */
    [[nodiscard]] Millivolt nominalMv(std::uint16_t raw) const noexcept;

    DividerSpec spec_;
    Calibration cal_;
};

} // namespace psu
