// supervisor.cpp — вимірювання середовища й рішення, що вимкнути першим.

#include "field/supervisor.hpp"

#include <cmath>

#include "field/platform.hpp"

namespace field {
namespace {

// Дільник температури: 10 кОм від опорної напруги до вузла, NTC від вузла
// на землю. Паспорт термістора: 10 кОм при +25 °C, β = 3435 K.
constexpr float kNtcTopOhm = 10'000.0F;
constexpr float kNtcR25Ohm = 10'000.0F;
constexpr float kNtcBetaK = 3435.0F;
constexpr float kKelvin25 = 298.15F;

constexpr std::uint16_t kVbatDivider = 2;  // 100к/100к: на ніжці рівно половина

std::optional<std::int16_t> readTemperature() noexcept {
    const auto counts = plat::readAdc(plat::Channel::Ntc);
    if (!counts) {
        return std::nullopt;
    }

    // Нуль і повна шкала — це не −60 °C і не +200 °C, а обрив дільника чи
    // замикання термістора. Віддати таке як температуру означало б скомандувати
    // супервізорові вимкнути все або не вмикати нічого.
    if (*counts == 0 || *counts >= plat::kAdcFullScale) {
        return std::nullopt;
    }

    const float rNtc = kNtcTopOhm * static_cast<float>(*counts) /
                       static_cast<float>(plat::kAdcFullScale - *counts);
    const float invT = 1.0F / kKelvin25 + std::log(rNtc / kNtcR25Ohm) / kNtcBetaK;
    const float celsius = 1.0F / invT - 273.15F;

    return static_cast<std::int16_t>(std::lround(celsius));
}

std::optional<std::uint16_t> readVoltage() noexcept {
    const auto counts = plat::readAdc(plat::Channel::Vbat);
    if (!counts) {
        return std::nullopt;
    }
    const std::uint32_t mv =
        (static_cast<std::uint32_t>(*counts) * plat::kAdcVrefMv) / plat::kAdcFullScale;
    return static_cast<std::uint16_t>(mv * kVbatDivider);
}

}  // namespace

std::string_view name(Deny reason) noexcept {
    switch (reason) {
        case Deny::Hot: return "hot";
        case Deny::Cold: return "cold";
        case Deny::Sag: return "sag";
        case Deny::Blind: break;
    }
    return "blind";
}

// --- оренда передавача ------------------------------------------------------

Supervisor::RadioLease& Supervisor::RadioLease::operator=(RadioLease&& other) noexcept {
    if (this != &other) {
        release();
        owner_ = other.owner_;
        other.owner_ = nullptr;
    }
    return *this;
}

bool Supervisor::RadioLease::live() const noexcept {
    return owner_ != nullptr && plat::loadOn(plat::Load::Radio);
}

void Supervisor::RadioLease::release() noexcept {
    if (owner_ != nullptr) {
        owner_->releaseRadio();
        owner_ = nullptr;
    }
}

// --- застосування стану -----------------------------------------------------

void Supervisor::applyThermal(Thermal state) noexcept {
    if (thermal_ == state) {
        return;
    }
    thermal_ = state;

    switch (state) {
        case Thermal::Nominal:
            plat::setCoreDivider(0);  // 168 МГц
            break;
        case Thermal::Throttled:
            // Половина частоти — це приблизно половина динамічного споживання
            // ядра, тобто менше тепла в корпусі, який і так не встигає його
            // віддати. Радіо при цьому мовчить: його імпульс гріє найдужче.
            plat::setCoreDivider(1);  // 84 МГц
            plat::setLoad(plat::Load::Radio, false);
            break;
        case Thermal::Critical:
            plat::setCoreDivider(2);  // 42 МГц
            plat::setLoad(plat::Load::Radio, false);
            plat::setLoad(plat::Load::Heater, false);
            plat::setLoad(plat::Load::Charger, false);
            break;
    }
}

void Supervisor::stepThermal(std::int16_t temperatureC) noexcept {
    switch (thermal_) {
        case Thermal::Nominal:
            if (temperatureC >= Limits::kCriticalOnC) {
                applyThermal(Thermal::Critical);
            } else if (temperatureC >= Limits::kThrottleOnC) {
                applyThermal(Thermal::Throttled);
            }
            break;
        case Thermal::Throttled:
            if (temperatureC >= Limits::kCriticalOnC) {
                applyThermal(Thermal::Critical);
            } else if (temperatureC <= Limits::kThrottleOffC) {
                applyThermal(Thermal::Nominal);
            }
            break;
        case Thermal::Critical:
            if (temperatureC <= Limits::kCriticalOffC) {
                applyThermal(Thermal::Throttled);
            }
            break;
    }
}

void Supervisor::stepCold(const Sample& sample) noexcept {
    const std::int16_t t = *sample.temperatureC;

    // Заряд нижче нуля не «небажаний», а заборонений: іони літію не встигають
    // увійти в графіт і осідають на аноді металевими голками, які проростають
    // крізь сепаратор. Це відкладена пожежа, і жодна дозарядка її не варта.
    if (t <= Limits::kChargeBlockC) {
        chargeBlocked_ = true;
    } else if (t >= Limits::kChargeAllowC) {
        chargeBlocked_ = false;
    }
    plat::setLoad(plat::Load::Charger, !chargeBlocked_ && thermal_ != Thermal::Critical);

    // Підігрів сам споживає струм, тому вмикається лише коли джерело тримає
    // напругу: інакше на морозі він же й посадить шину.
    const bool supplyOk = sample.vbatMv && *sample.vbatMv >= Limits::kSupplyOkMv;
    if (!supplyOk || thermal_ == Thermal::Critical) {
        heaterOn_ = false;
    } else if (t <= Limits::kHeaterOnC) {
        heaterOn_ = true;
    } else if (t >= Limits::kHeaterOffC) {
        heaterOn_ = false;
    }
    plat::setLoad(plat::Load::Heater, heaterOn_);
}

void Supervisor::stepSupply(std::uint16_t mv) noexcept {
    if (!plat::loadOn(plat::Load::Radio)) {
        idleMv_ = mv;  // без навантаження бачимо ЕРС джерела
        return;
    }

    if (mv < Limits::kShedMv) {
        // Просадка під навантаженням. Знімаємо передавач негайно: ще кілька
        // десятків мілівольт — і спрацює BOR, а перезапуск посеред кадру
        // коштує дорожче за втрачений сеанс.
        plat::setLoad(plat::Load::Radio, false);
        ++sagEvents_;

        if (idleMv_ > mv) {
            rIntMohm_ = static_cast<std::uint16_t>((static_cast<std::uint32_t>(idleMv_ - mv) * 1000) /
                                                   Limits::kRadioPulseMa);
        }
    }
}

// --- зовнішній інтерфейс ----------------------------------------------------

Supervisor::Supervisor(bool safeStart, std::chrono::milliseconds now)
    : blindSince_{now}, startedAt_{now} {
    plat::setLoad(plat::Load::Radio, false);
    plat::setLoad(plat::Load::Heater, false);
    plat::setLoad(plat::Load::Charger, false);

    if (safeStart) {
        applyThermal(Thermal::Throttled);
    }
}

Sample Supervisor::measure() noexcept {
    return Sample{readTemperature(), readVoltage()};
}

void Supervisor::step(const Sample& sample, std::chrono::milliseconds now) {
    if (sample.blind()) {
        if (!blind_) {
            blind_ = true;
            blindSince_ = now;
        }
        // Осліпнути на секунду — дрібниця (АЦП міг не встигнути). Осліпнути
        // надовго — означає більше не знати, у якому ми середовищі, а в
        // такому стані єдина безпечна дія — не діяти.
        if (now - blindSince_ > Limits::kBlindLimit) {
            applyThermal(Thermal::Critical);
        }
        return;
    }

    blind_ = false;

    if (sample.temperatureC) {
        lastTempC_ = *sample.temperatureC;
        stepThermal(*sample.temperatureC);
        stepCold(sample);
    }
    if (sample.vbatMv) {
        stepSupply(*sample.vbatMv);
    }
}

std::expected<Supervisor::RadioLease, Deny> Supervisor::requestRadio() noexcept {
    if (blind_ || idleMv_ == 0) {
        return std::unexpected{Deny::Blind};
    }
    if (thermal_ != Thermal::Nominal) {
        return std::unexpected{Deny::Hot};
    }
    if (lastTempC_ <= Limits::kChargeBlockC && rIntMohm_ &&
        *rIntMohm_ > Limits::kColdRIntMohm) {
        // На морозі внутрішній опір джерела зростає в рази. Це не «холодно»,
        // а «джерело більше не тримає двоамперний імпульс».
        return std::unexpected{Deny::Cold};
    }

    if (rIntMohm_) {
        const std::uint32_t drop =
            (static_cast<std::uint32_t>(Limits::kRadioPulseMa) * *rIntMohm_) / 1000;
        if (idleMv_ <= drop || idleMv_ - drop < Limits::kFloorMv) {
            return std::unexpected{Deny::Sag};
        }
    }

    plat::setLoad(plat::Load::Radio, true);
    return RadioLease{*this};
}

void Supervisor::releaseRadio() noexcept {
    // Замір під навантаженням і замір після нього дають різницю, з якої прямо
    // рахується внутрішній опір джерела. Це єдине місце, де прилад може
    // дізнатися його НЕ з паспорта, а зі свого сьогоднішнього акумулятора
    // на своєму сьогоднішньому морозі.
    const auto loaded = plat::loadOn(plat::Load::Radio) ? readVoltage() : std::nullopt;

    plat::setLoad(plat::Load::Radio, false);
    plat::delayFor(std::chrono::microseconds{2000});  // шина відновлюється

    const auto idle = readVoltage();
    if (!idle) {
        return;
    }

    idleMv_ = *idle;
    if (loaded && *idle > *loaded) {
        rIntMohm_ = static_cast<std::uint16_t>(
            (static_cast<std::uint32_t>(*idle - *loaded) * 1000) / Limits::kRadioPulseMa);
    }
}

}  // namespace field
