#pragma once

#include <algorithm>
#include <chrono>
#include <concepts>
#include <cstdint>
#include <expected>
#include <optional>

// Передпольотний шлюз живлення: вирішує, чи можна зараз стирати Flash.
// Вердикт — std::expected: дозвіл несе умови (пом'якшення режиму),
// відмова несе причину й усі виміри для телеметрії.

namespace ota {

struct SafetyLimits {
    std::int16_t  tempMinC           = 5;
    std::int16_t  tempMaxC           = 45;
    std::uint8_t  minSocPercent      = 45;
    std::uint16_t borMv              = 2700;  // апаратний поріг скиду
    std::uint16_t borMarginMv        = 200;   // запас над ним
    std::uint16_t testLoadMa         = 200;   // каліброване тестове навантаження
    std::uint16_t otaPeakMa          = 320;   // піковий струм стирання й радіо
    std::uint16_t otaPeakThrottledMa = 175;   // те саме в пом'якшеному режимі
    std::uint8_t  maxPowerFaults     = 3;     // після стількох зривів — блокування

    [[nodiscard]] constexpr std::uint16_t safeFloorMv() const noexcept {
        return static_cast<std::uint16_t>(borMv + borMarginMv);
    }
};

enum class DenyReason : std::uint8_t {
    Cold, Hot, LowSoc, HighEsr, PowerFaultLockout, SensorFault
};

enum class Urgency : std::uint8_t { Routine, EmergencySecurityFix };

struct ThrottleProfile {
    std::uint16_t cpuMhz;
    std::uint16_t spiMhz;
    std::int8_t   txDbm;
};

// Замість 160 МГц ядра, 80 МГц шини Flash і +20 dBm передавача.
inline constexpr ThrottleProfile kSafeThrottle{ .cpuMhz = 40, .spiMhz = 20, .txDbm = 10 };

struct PulseMeasurement {
    std::uint16_t idleMv;
    std::uint16_t loadMv;
    std::uint16_t esrMilliOhm;  // повний послідовний опір: комірка + монтаж
    std::uint16_t forecastMv;
};

// Порожній optional чесно означає «не міряли», а не «нуль».
struct Diagnostics {
    std::optional<std::int16_t>     tempC{};
    std::optional<std::uint8_t>     socPercent{};
    std::optional<std::uint16_t>    idleMv{};
    std::optional<PulseMeasurement> pulse{};
    std::uint8_t                    powerFaults = 0;
};

struct Allowance {
    bool                           externalPower = false;
    std::optional<ThrottleProfile> throttle{};
    Diagnostics                    diag{};
};

struct Denial {
    DenyReason  reason;
    Diagnostics diag{};
};

using Verdict = std::expected<Allowance, Denial>;

[[nodiscard]] constexpr bool throttledAllowance(const Allowance& a) noexcept {
    return a.throttle.has_value();
}

template <typename T>
concept PowerHal = requires(T& hal, bool on, std::chrono::microseconds t, std::uint32_t word) {
    { hal.vbusPresent() }        -> std::same_as<bool>;
    { hal.temperatureC() }       -> std::same_as<std::optional<std::int16_t>>;
    { hal.stateOfCharge() }      -> std::same_as<std::optional<std::uint8_t>>;
    { hal.railVoltageMv() }      -> std::same_as<std::optional<std::uint16_t>>;
    { hal.testLoad(on) }         -> std::same_as<void>;
    { hal.sleep(t) }             -> std::same_as<void>;
    { hal.loadFaultWord() }      -> std::same_as<std::optional<std::uint32_t>>;
    { hal.storeFaultWord(word) } -> std::same_as<bool>;
};

template <PowerHal Hal>
class PreflightGate {
public:
    constexpr explicit PreflightGate(Hal& hal, SafetyLimits limits = {}) noexcept
        : hal_(hal), limits_(limits) {}

    [[nodiscard]] Verdict evaluate(Urgency urgency = Urgency::Routine);

    // Викликається після успішно прошитого образу.
    bool clearFaults() { return storeLatch(Latch{}); }

    [[nodiscard]] const SafetyLimits& limits() const noexcept { return limits_; }

private:
    // Латч у backup-домені RTC: один регістр, що переживає скид ядра.
    struct Latch {
        bool         armed  = false;
        std::uint8_t faults = 0;
    };

    static constexpr std::uint32_t kMagic      = 0xB7u;
    static constexpr int           kMagicShift = 24;
    static constexpr std::uint32_t kArmedBit   = 0x1u;
    static constexpr int           kFaultShift = 8;

    // 12 мс на затухання перехідних процесів, далі 8 відліків по 250 мкс —
    // це рівно 12–14-та мілісекунда імпульсу, — хвіст до 15 мс і релаксація.
    static constexpr unsigned                  kSamples   = 8;
    static constexpr std::chrono::microseconds kSampleGap{250};
    static constexpr std::chrono::milliseconds kSettle{12};
    static constexpr std::chrono::milliseconds kTail{1};
    static constexpr std::chrono::milliseconds kRelax{60};

    // Знімає навантаження на будь-якому виході — і на аварійному теж.
    class LoadGuard {
    public:
        explicit LoadGuard(Hal& hal) : hal_(hal) { hal_.testLoad(true); }
        ~LoadGuard() { hal_.testLoad(false); }
        LoadGuard(const LoadGuard&) = delete;
        LoadGuard& operator=(const LoadGuard&) = delete;
    private:
        Hal& hal_;
    };

    // Знімає зведення латча, якщо вихід стався повз явний disarm().
    class ArmGuard {
    public:
        ArmGuard(PreflightGate& gate, Latch latch) noexcept
            : gate_(gate), latch_(latch) {}
        ~ArmGuard() {
            if (armed_) {
                latch_.armed = false;
                static_cast<void>(gate_.storeLatch(latch_));
            }
        }
        [[nodiscard]] bool disarm() {
            armed_ = false;
            latch_.armed = false;
            return gate_.storeLatch(latch_);
        }
        ArmGuard(const ArmGuard&) = delete;
        ArmGuard& operator=(const ArmGuard&) = delete;
    private:
        PreflightGate& gate_;
        Latch          latch_;
        bool           armed_ = true;
    };

    std::optional<Latch> loadLatch();
    bool storeLatch(Latch latch);
    std::optional<std::uint16_t> sampleRailMv();
    std::optional<std::uint16_t> pulseMeasure();

    Hal&         hal_;
    SafetyLimits limits_;
};

template <PowerHal Hal>
std::optional<typename PreflightGate<Hal>::Latch> PreflightGate<Hal>::loadLatch()
{
    const auto word = hal_.loadFaultWord();
    if (!word) {
        return std::nullopt;
    }
    if (((*word >> kMagicShift) & 0xFFu) != kMagic) {
        return Latch{};  // перше вмикання або втрачений backup-домен
    }
    return Latch{
        .armed  = (*word & kArmedBit) != 0u,
        .faults = static_cast<std::uint8_t>((*word >> kFaultShift) & 0xFFu)
    };
}

template <PowerHal Hal>
bool PreflightGate<Hal>::storeLatch(Latch latch)
{
    const std::uint32_t word = (kMagic << kMagicShift)
                             | (static_cast<std::uint32_t>(latch.faults) << kFaultShift)
                             | (latch.armed ? kArmedBit : 0u);
    return hal_.storeFaultWord(word);
}

// Один відлік АЦП шумить на кілька мілівольт, а ми рахуємо різницю
// двох напруг — тому серія з усередненням, а не поодинокий замір.
template <PowerHal Hal>
std::optional<std::uint16_t> PreflightGate<Hal>::sampleRailMv()
{
    std::uint32_t acc = 0;
    for (unsigned i = 0; i < kSamples; ++i) {
        const auto mv = hal_.railVoltageMv();
        if (!mv) {
            return std::nullopt;
        }
        acc += *mv;
        if (i + 1 < kSamples) {
            hal_.sleep(kSampleGap);
        }
    }
    return static_cast<std::uint16_t>((acc + kSamples / 2) / kSamples);
}

template <PowerHal Hal>
std::optional<std::uint16_t> PreflightGate<Hal>::pulseMeasure()
{
    std::optional<std::uint16_t> loadMv;
    {
        LoadGuard load{hal_};
        hal_.sleep(kSettle);
        loadMv = sampleRailMv();
        hal_.sleep(kTail);
    }
    // Без паузи наступний замір побачить занижену напругу: подвійний
    // електричний шар розсмоктується десятки мілісекунд.
    hal_.sleep(kRelax);
    return loadMv;
}

template <PowerHal Hal>
Verdict PreflightGate<Hal>::evaluate(Urgency urgency)
{
    Diagnostics diag{};
    const auto deny = [&diag](DenyReason reason) -> Verdict {
        return std::unexpected(Denial{reason, diag});
    };

    if (limits_.testLoadMa == 0 || limits_.otaPeakMa == 0) {
        return deny(DenyReason::SensorFault);  // зіпсована конфігурація
    }

    // 0. Латч попередньої спроби. Лишився зведеним — минулий імпульсний тест
    // обірвався апаратним скидом, але ДО стирання Flash: пристрій живий.
    auto latch = loadLatch();
    if (!latch) {
        return deny(DenyReason::SensorFault);
    }
    if (latch->armed) {
        if (latch->faults < 0xFFu) {
            ++latch->faults;
        }
        latch->armed = false;
        if (!storeLatch(*latch)) {
            return deny(DenyReason::SensorFault);
        }
    }
    diag.powerFaults = latch->faults;
    if (latch->faults >= limits_.maxPowerFaults) {
        return deny(DenyReason::PowerFaultLockout);
    }

    // 1. Зовнішнє живлення знімає всі питання до комірки.
    if (hal_.vbusPresent()) {
        const auto mv = sampleRailMv();
        if (!mv) {
            return deny(DenyReason::SensorFault);
        }
        diag.idleMv = mv;
        return Allowance{.externalPower = true, .throttle = std::nullopt, .diag = diag};
    }

    // 2. Температурний коридор: на морозі опір комірки росте в рази.
    const auto tempC = hal_.temperatureC();
    if (!tempC) {
        return deny(DenyReason::SensorFault);
    }
    diag.tempC = tempC;
    if (*tempC < limits_.tempMinC) {
        return deny(DenyReason::Cold);
    }
    if (*tempC > limits_.tempMaxC) {
        return deny(DenyReason::Hot);
    }

    // 3. Залишковий заряд за паливоміром — груба, але дешева відсічка.
    const auto soc = hal_.stateOfCharge();
    if (!soc) {
        return deny(DenyReason::SensorFault);
    }
    diag.socPercent = soc;
    if (*soc < limits_.minSocPercent) {
        return deny(DenyReason::LowSoc);
    }

    // 4. Напруга спокою до вмикання сильнострумових вузлів.
    const auto idleMv = sampleRailMv();
    if (!idleMv) {
        return deny(DenyReason::SensorFault);
    }
    diag.idleMv = idleMv;
    if (*idleMv < limits_.safeFloorMv()) {
        return deny(DenyReason::LowSoc);
    }

    // 5. Зводимо латч і тільки тоді вантажимо комірку: якщо шина провалиться,
    // скид застане нас саме тут — і слід лишиться в NV.
    latch->armed = true;
    if (!storeLatch(*latch)) {
        return deny(DenyReason::SensorFault);
    }
    ArmGuard guard{*this, *latch};

    const auto loadMv = pulseMeasure();
    if (!loadMv) {
        return deny(DenyReason::SensorFault);
    }
    if (!guard.disarm()) {
        return deny(DenyReason::SensorFault);
    }
    if (*loadMv > *idleMv) {
        // Під навантаженням напруга не росте: бреше дільник або мультиплексор.
        return deny(DenyReason::SensorFault);
    }

    const auto deltaTest = static_cast<std::uint16_t>(*idleMv - *loadMv);
    const auto esr = static_cast<std::uint16_t>(std::min<std::uint32_t>(
        0xFFFFu,
        (std::uint32_t{deltaTest} * 1000u + limits_.testLoadMa / 2u) / limits_.testLoadMa));

    // Екстраполяція просідання з тестового струму на піковий струм OTA.
    const auto forecast = [&](std::uint16_t peakMa) -> std::optional<std::uint16_t> {
        const std::uint32_t drop =
            (std::uint32_t{deltaTest} * peakMa + limits_.testLoadMa / 2u) / limits_.testLoadMa;
        if (drop >= *idleMv) {
            return std::nullopt;
        }
        return static_cast<std::uint16_t>(*idleMv - drop);
    };

    const auto full = forecast(limits_.otaPeakMa);
    diag.pulse = PulseMeasurement{
        .idleMv = *idleMv,
        .loadMv = *loadMv,
        .esrMilliOhm = esr,
        .forecastMv = full.value_or(0)
    };

    if (full && *full >= limits_.safeFloorMv()) {
        return Allowance{.externalPower = false, .throttle = std::nullopt, .diag = diag};
    }

    // 6. Критичний патч безпеки заслуговує на другу спробу — з нижчою
    // частотою ядра, повільнішою шиною Flash і тихішим радіо.
    if (urgency == Urgency::EmergencySecurityFix) {
        if (const auto eased = forecast(limits_.otaPeakThrottledMa);
            eased && *eased >= limits_.safeFloorMv()) {
            diag.pulse->forecastMv = *eased;
            return Allowance{.externalPower = false, .throttle = kSafeThrottle, .diag = diag};
        }
    }

    return deny(DenyReason::HighEsr);
}

}  // namespace ota
