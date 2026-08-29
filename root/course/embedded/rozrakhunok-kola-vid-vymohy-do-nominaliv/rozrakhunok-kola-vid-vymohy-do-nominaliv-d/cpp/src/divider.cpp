#include "divider.hpp"

#include <algorithm>
#include <limits>

namespace psu {
namespace {

/* Стеля суми плечей. Це і санітарна перевірка (дільник на гігаоми не буває),
   і гарантія, що чисельник у nominalMv не переповнить 64 біти:
   65535 * 65535 * 1e8 ~ 4.3e17 < 1.8e19. */
constexpr std::uint64_t rSumMax = 100'000'000;

/* Фізична стеля вузла: 1 кВ. Вище — не вимірювання, а помилка в паспорті. */
constexpr std::uint64_t mvMax = 1'000'000;

/* Розведення еталонних точок: різниця напруг стоїть у знаменнику нахилу,
   тож на близьких точках шум еталона множиться на порядки. */
constexpr Millivolt minCalSpanMv = 500;

/* Ділення з округленням до найближчого. Просте відкидання дробової частини
   на кожному кроці стабільно з'їдає до молодшого розряду АЦП. */
[[nodiscard]] constexpr std::uint64_t divRound(std::uint64_t num, std::uint64_t den) noexcept {
    return (num + den / 2) / den;
}

[[nodiscard]] constexpr std::int64_t divRound(std::int64_t num, std::int64_t den) noexcept {
    return num >= 0 ? (num + den / 2) / den : -((-num + den / 2) / den);
}

[[nodiscard]] constexpr bool specIsSane(const DividerSpec& s) noexcept {
    return s.r1Ohms != 0 && s.r2Ohms != 0 && s.vrefMv != 0 && s.adcMaxCode != 0
        && static_cast<std::uint64_t>(s.r1Ohms) + s.r2Ohms <= rSumMax;
}

} // namespace

std::string_view describe(SenseError err) noexcept {
    switch (err) {
        case SenseError::badSpec:       return "хибні паспортні дані каналу";
        case SenseError::rawOutOfRange: return "код АЦП поза роздільністю";
        case SenseError::gainOutOfBand: return "нахил калібрування поза смугою";
        case SenseError::badCalPoints:  return "непридатні еталонні точки";
    }
    return "невідома помилка";
}

std::expected<BatterySense, SenseError>
BatterySense::create(DividerSpec spec, Calibration cal) noexcept {
    if (!specIsSane(spec)) {
        return std::unexpected{SenseError::badSpec};
    }
    if (!cal.plausible()) {
        return std::unexpected{SenseError::gainOutOfBand};
    }
    return BatterySense{spec, cal};
}

std::expected<void, SenseError> BatterySense::setCalibration(Calibration cal) noexcept {
    if (!cal.plausible()) {
        return std::unexpected{SenseError::gainOutOfBand};
    }
    cal_ = cal;
    return {};
}

/* Обидва множення й обидва ділення зведено в ОДИН дріб:
       Vin = raw * Vref * (R1 + R2) / (ADC_MAX * R2)
   Якби рахували в два кроки (спершу напруга на піні, потім масштаб дільника),
   перше округлення множилося б на коефіцієнт 1.5 і давало зайвий мілівольт. */
Millivolt BatterySense::nominalMv(std::uint16_t raw) const noexcept {
    const auto num = static_cast<std::uint64_t>(raw) * spec_.vrefMv
                   * (static_cast<std::uint64_t>(spec_.r1Ohms) + spec_.r2Ohms);
    const auto den = static_cast<std::uint64_t>(spec_.adcMaxCode) * spec_.r2Ohms;
    return static_cast<Millivolt>(std::min(divRound(num, den), mvMax));
}

std::expected<Millivolt, SenseError>
BatterySense::toMillivolts(std::uint16_t raw) const noexcept {
    /* Код більший за роздільність — це не «трохи завелика напруга», а збій
       драйвера АЦП чи неузгоджене вирівнювання результату (ліве/праве). */
    if (raw > spec_.adcMaxCode) {
        return std::unexpected{SenseError::rawOutOfRange};
    }

    const auto nominal = static_cast<std::int64_t>(nominalMv(raw));
    auto scaled = divRound(nominal * static_cast<std::int64_t>(cal_.gainPpm),
                           static_cast<std::int64_t>(Calibration::unityPpm));
    scaled += cal_.offsetMv;

    /* Зсув калібрування від'ємний, а на вході нуль — арифметика дає мінус.
       Від'ємної напруги на цьому вузлі бути не може: захисні діоди не пустять. */
    return static_cast<Millivolt>(std::max<std::int64_t>(0, scaled));
}

std::expected<Calibration, SenseError>
BatterySense::fitTwoPoint(RefPoint low, RefPoint high) const noexcept {
    if (low.raw > spec_.adcMaxCode || high.raw > spec_.adcMaxCode) {
        return std::unexpected{SenseError::rawOutOfRange};
    }
    if (low.trueMv < 0 || high.raw <= low.raw
        || high.trueMv - low.trueMv < minCalSpanMv) {
        return std::unexpected{SenseError::badCalPoints};
    }

    const auto nomLow  = static_cast<std::int64_t>(nominalMv(low.raw));
    const auto nomHigh = static_cast<std::int64_t>(nominalMv(high.raw));
    if (nomHigh <= nomLow) {
        return std::unexpected{SenseError::badCalPoints};
    }

    /* Нахил: у скільки разів справжня різниця напруг більша за паспортну.
       Сюди зібралися разом допуск R1 і R2, похибка опорної напруги
       й підсилення самого АЦП — розділяти їх нема ні потреби, ні змоги. */
    const auto gain = divRound(
        static_cast<std::uint64_t>(high.trueMv - low.trueMv) * Calibration::unityPpm,
        static_cast<std::uint64_t>(nomHigh - nomLow));

    Calibration fitted{};
    if (gain > std::numeric_limits<std::uint32_t>::max()) {
        return std::unexpected{SenseError::gainOutOfBand};
    }
    fitted.gainPpm = static_cast<std::uint32_t>(gain);
    if (!fitted.plausible()) {
        return std::unexpected{SenseError::gainOutOfBand};
    }

    /* Зсув: що лишилося в нижній точці після застосування нахилу.
       Це зсув нуля АЦП і струм витоку входу, який тече крізь плече дільника. */
    const auto offset = static_cast<std::int64_t>(low.trueMv)
                      - divRound(nomLow * static_cast<std::int64_t>(fitted.gainPpm),
                                 static_cast<std::int64_t>(Calibration::unityPpm));
    fitted.offsetMv = static_cast<Millivolt>(offset);
    return fitted;
}

} // namespace psu
