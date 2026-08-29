// accelerometer.inl — визначення шаблонних методів драйвера.
//
// Файл підключається наприкінці accelerometer.hpp: оголошення класу читається
// як зміст, реалізація лежить окремо й не заважає.
#pragma once

#include <algorithm>
#include <array>
#include <utility>

#include "bus_recovery.hpp"
#include "fixed_point.hpp"
#include "reliable_transport.hpp"

namespace accel {

namespace detail {

inline constexpr std::chrono::milliseconds kPowerOnDelay{10};
inline constexpr unsigned kTurnOnSamples = 2;         // фільтр іще не набрав
inline constexpr std::size_t kFifoChunkSamples = 8;   // 8 × 6 = 48 байтів
inline constexpr std::chrono::milliseconds kStartupTimeout{50};

[[nodiscard]] constexpr std::int16_t clampToInt16(std::int32_t value) noexcept
{
    return static_cast<std::int16_t>(std::clamp(value, -32768, 32767));
}

} // namespace detail

template <BusTransport Transport>
Accelerometer<Transport>::Accelerometer(Transport transport) noexcept
    : transport_(std::move(transport))
{
    applyScale();
}

// --- транзакції нижнього рівня -------------------------------------------

template <BusTransport Transport>
Result<std::uint8_t> Accelerometer<Transport>::readByte(regs::Reg reg) noexcept
{
    std::array<std::uint8_t, 1> buffer{};
    if (auto outcome = transport_.read(regs::raw(reg), buffer); !outcome) {
        return std::unexpected(outcome.error());
    }
    return buffer[0];
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::writeByte(regs::Reg reg, std::uint8_t value) noexcept
{
    const std::array<std::uint8_t, 1> buffer{value};
    if (auto outcome = transport_.write(regs::raw(reg), buffer); !outcome) {
        return outcome; // тінь лишається старою: у кремнії нічого не змінилося
    }
    if (regs::isShadowed(reg)) {
        shadow_.store(reg, value);
    }
    return {};
}

template <BusTransport Transport>
template <typename FieldType>
Result<void> Accelerometer<Transport>::updateField(regs::Reg reg, std::uint8_t value) noexcept
{
    if (!regs::isShadowed(reg) || !FieldType::fits(value)) {
        return std::unexpected(Status::InvalidParam);
    }
    return writeByte(reg, FieldType::insert(shadow_.value(reg), value));
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::setBits(regs::Reg reg, std::uint8_t bits) noexcept
{
    if (!regs::isShadowed(reg)) {
        return std::unexpected(Status::InvalidParam);
    }
    return writeByte(reg, static_cast<std::uint8_t>(shadow_.value(reg) | bits));
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::clearBits(regs::Reg reg, std::uint8_t bits) noexcept
{
    if (!regs::isShadowed(reg)) {
        return std::unexpected(Status::InvalidParam);
    }
    return writeByte(reg, static_cast<std::uint8_t>(shadow_.value(reg) & ~bits));
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::readBurst(regs::Reg start, std::span<std::uint8_t> out) noexcept
{
    if (out.empty()) {
        return std::unexpected(Status::InvalidParam);
    }
    // Автоінкремент адреси: без нього чип шість разів віддасть OUT_X_L.
    const auto address = static_cast<std::uint8_t>(
        out.size() > 1 ? (regs::raw(start) | regs::kAutoIncrement) : regs::raw(start));
    return transport_.read(address, out);
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::syncShadow() noexcept
{
    // Тінь стартує зі справжнього вмісту кремнію: інакше перше ж оновлення
    // поля затерло б заводські біти нулями.
    for (const regs::Reg reg : ShadowBank::order) {
        auto value = readByte(reg);
        if (!value) {
            return std::unexpected(value.error());
        }
        shadow_.store(reg, *value);
    }
    return {};
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::reapplyConfig() noexcept
{
    for (const regs::Reg reg : ShadowBank::order) {
        const std::array<std::uint8_t, 1> buffer{shadow_.value(reg)};
        if (auto outcome = transport_.write(regs::raw(reg), buffer); !outcome) {
            return outcome;
        }
    }
    return {};
}

// --- життєвий цикл --------------------------------------------------------

template <BusTransport Transport>
void Accelerometer<Transport>::applyScale() noexcept
{
    scaleSi_ = static_cast<float>(sensitivityMicroG(config_.range)) * 1e-6F * kStandardGravity;
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::initialise(const Config &config) noexcept
{
    config_ = config;
    applyScale();
    initialised_ = false;

    transport_.delay(detail::kPowerOnDelay);

    // Крок 1: чи це той чип? Неправильний монтаж і підробка мусять упасти
    // тут, на стенді, а не в польоті.
    auto who = readByte(regs::Reg::WhoAmI);
    if (!who) {
        return std::unexpected(who.error());
    }
    if (*who != regs::kWhoAmIValue) {
        return std::unexpected(Status::NotFound);
    }

    if (auto outcome = syncShadow(); !outcome) {
        return outcome;
    }

    // Крок 2: CTRL_REG4 — BDU замикає вихідні регістри до кінця вичитування
    // блоку, інакше молодший і старший байти належатимуть різним вибіркам.
    std::uint8_t ctrl4 = shadow_.value(regs::Reg::Ctrl4);
    ctrl4 = static_cast<std::uint8_t>(ctrl4 & ~regs::kCtrl4HighResolution);
    ctrl4 = static_cast<std::uint8_t>(ctrl4 | regs::kCtrl4Bdu);
    ctrl4 = regs::FullScaleField::insert(ctrl4, static_cast<std::uint8_t>(config_.range));
    if (config_.resolution == Resolution::Bits16) {
        ctrl4 = static_cast<std::uint8_t>(ctrl4 | regs::kCtrl4HighResolution);
    }
    if (auto outcome = writeByte(regs::Reg::Ctrl4, ctrl4); !outcome) {
        return outcome;
    }

    // Крок 3: буфер поки в обхід — читаємо останній відлік напряму.
    if (auto outcome = writeFifoControl(FifoMode::Bypass, 0); !outcome) {
        return outcome;
    }
    if (auto outcome = clearBits(regs::Reg::Ctrl5, regs::kCtrl5FifoEnable); !outcome) {
        return outcome;
    }

    // Крок 4: жодних переривань, поки прикладний код їх не попросить.
    const auto allInterrupts = static_cast<std::uint8_t>(
        regs::kInt1DataReady | regs::kInt1Watermark | regs::kInt1Overrun);
    if (auto outcome = clearBits(regs::Reg::Ctrl3, allInterrupts); !outcome) {
        return outcome;
    }

    // Крок 5: осі й частота — саме цей запис будить чип із режиму спокою.
    std::uint8_t ctrl1 = shadow_.value(regs::Reg::Ctrl1);
    ctrl1 = regs::OdrField::insert(ctrl1, static_cast<std::uint8_t>(config_.odr));
    ctrl1 = static_cast<std::uint8_t>(ctrl1 | regs::kCtrl1AxesXyz);
    if (auto outcome = writeByte(regs::Reg::Ctrl1, ctrl1); !outcome) {
        return outcome;
    }

    initialised_ = true;

    // Крок 6: перші відліки проходять недозаповненим цифровим фільтром —
    // викидаємо їх, щоб прикладна логіка не побачила сходинки.
    for (unsigned i = 0; i < detail::kTurnOnSamples; ++i) {
        static_cast<void>(waitForData(detail::kStartupTimeout));
        static_cast<void>(readRaw());
    }

    return {};
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::shutdown() noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    auto outcome = updateField<regs::OdrField>(regs::Reg::Ctrl1,
                                               static_cast<std::uint8_t>(Odr::PowerDown));
    initialised_ = false;
    return outcome;
}

// --- конфігурація ---------------------------------------------------------

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::setRange(Range range) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    if (auto outcome = updateField<regs::FullScaleField>(regs::Reg::Ctrl4,
                                                         static_cast<std::uint8_t>(range));
        !outcome) {
        return outcome; // масштаб не чіпаємо: у кремнії лишився старий діапазон
    }
    config_.range = range;
    applyScale();
    return {};
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::setOdr(Odr odr) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    if (auto outcome = updateField<regs::OdrField>(regs::Reg::Ctrl1,
                                                   static_cast<std::uint8_t>(odr));
        !outcome) {
        return outcome;
    }
    config_.odr = odr;
    return {};
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::setLowPower(bool enable) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    return enable ? setBits(regs::Reg::Ctrl1, regs::kCtrl1LowPower)
                  : clearBits(regs::Reg::Ctrl1, regs::kCtrl1LowPower);
}

template <BusTransport Transport>
void Accelerometer<Transport>::setCalibration(const Calibration &calibration) noexcept
{
    calibration_ = calibration;
    // Обидва шляхи перетворення мусять давати однакову корекцію, тож
    // недописаний коефіцієнт добудовуємо з парного.
    for (std::size_t axis = 0; axis < 3; ++axis) {
        if (calibration_.gain[axis] == 0.0F && calibration_.gainMilli[axis] == 0) {
            calibration_.gain[axis] = 1.0F;
            calibration_.gainMilli[axis] = 1000;
        } else if (calibration_.gain[axis] == 0.0F) {
            calibration_.gain[axis] = static_cast<float>(calibration_.gainMilli[axis]) / 1000.0F;
        } else if (calibration_.gainMilli[axis] == 0) {
            calibration_.gainMilli[axis] =
                static_cast<std::int32_t>(calibration_.gain[axis] * 1000.0F + 0.5F);
        }
    }
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::enableDataReadyInterrupt(bool enable) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    return enable ? setBits(regs::Reg::Ctrl3, regs::kInt1DataReady)
                  : clearBits(regs::Reg::Ctrl3, regs::kInt1DataReady);
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::enableWatermarkInterrupt(bool enable) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    const auto bits = static_cast<std::uint8_t>(regs::kInt1Watermark | regs::kInt1Overrun);
    return enable ? setBits(regs::Reg::Ctrl3, bits) : clearBits(regs::Reg::Ctrl3, bits);
}

// --- читання --------------------------------------------------------------

template <BusTransport Transport>
Result<DataStatus> Accelerometer<Transport>::dataStatus() noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    auto value = readByte(regs::Reg::Status);
    if (!value) {
        return std::unexpected(value.error());
    }
    return DataStatus{.ready = (*value & regs::kStatusZyxDataReady) != 0,
                      .overrun = (*value & regs::kStatusZyxOverrun) != 0};
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::waitForData(std::chrono::milliseconds timeout) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    return waitForFlag(transport_, regs::raw(regs::Reg::Status),
                       regs::kStatusZyxDataReady, timeout);
}

template <BusTransport Transport>
RawSample Accelerometer<Transport>::decode(
    std::span<const std::uint8_t, regs::kSampleBytes> bytes) const noexcept
{
    RawSample raw{};
    for (std::size_t axis = 0; axis < raw.size(); ++axis) {
        const auto pair = bytes.subspan(axis * 2).template first<2>();
        const std::int16_t code = fixed::signExtend(fixed::littleEndian(pair), config_.resolution);
        raw[axis] = detail::clampToInt16(static_cast<std::int32_t>(code) -
                                         static_cast<std::int32_t>(calibration_.offset[axis]));
    }
    return raw;
}

template <BusTransport Transport>
Result<RawSample> Accelerometer<Transport>::readRaw() noexcept
{
    auto status = dataStatus();
    if (!status) {
        return std::unexpected(status.error());
    }
    if (!status->ready) {
        return std::unexpected(Status::NoData);
    }

    // Шість байтів однією транзакцією: BDU тримає їх замороженими, поки
    // останній не піде на шину. Шість окремих читань дали б розрив даних.
    std::array<std::uint8_t, regs::kSampleBytes> buffer{};
    if (auto outcome = readBurst(regs::Reg::OutXL, buffer); !outcome) {
        return std::unexpected(outcome.error());
    }
    return decode(std::span<const std::uint8_t, regs::kSampleBytes>{buffer});
}

template <BusTransport Transport>
Acceleration Accelerometer<Transport>::toSi(const RawSample &raw) const noexcept
{
    return Acceleration{
        .x = static_cast<float>(raw[0]) * scaleSi_ * calibration_.gain[0],
        .y = static_cast<float>(raw[1]) * scaleSi_ * calibration_.gain[1],
        .z = static_cast<float>(raw[2]) * scaleSi_ * calibration_.gain[2]};
}

template <BusTransport Transport>
MilliG Accelerometer<Transport>::toMilliG(const RawSample &raw) const noexcept
{
    const auto corrected = [&](std::size_t axis) {
        const std::int32_t mg = fixed::toMilliG(raw[axis], config_.range);
        return fixed::divideRounded(static_cast<std::int64_t>(mg) * calibration_.gainMilli[axis],
                                    1000);
    };
    return MilliG{.x = corrected(0), .y = corrected(1), .z = corrected(2)};
}

template <BusTransport Transport>
MilliMetrePerSecond2 Accelerometer<Transport>::toMilliMetrePerSecond2(
    const RawSample &raw) const noexcept
{
    // Множення на g₀ живе всередині fixed::toMillimetrePerSecond2 і робиться
    // в 64 бітах; підсилення осі накладаємо тим самим цілим коефіцієнтом.
    const auto corrected = [&](std::size_t axis) {
        const std::int32_t value = fixed::toMillimetrePerSecond2(raw[axis], config_.range);
        return fixed::divideRounded(
            static_cast<std::int64_t>(value) * calibration_.gainMilli[axis], 1000);
    };
    return MilliMetrePerSecond2{.x = corrected(0), .y = corrected(1), .z = corrected(2)};
}

template <BusTransport Transport>
Result<Acceleration> Accelerometer<Transport>::readAcceleration() noexcept
{
    return readRaw().transform([this](const RawSample &raw) { return toSi(raw); });
}

template <BusTransport Transport>
Result<MilliG> Accelerometer<Transport>::readMilliG() noexcept
{
    return readRaw().transform([this](const RawSample &raw) { return toMilliG(raw); });
}

template <BusTransport Transport>
Result<MilliMetrePerSecond2> Accelerometer<Transport>::readMilliMetrePerSecond2() noexcept
{
    return readRaw().transform(
        [this](const RawSample &raw) { return toMilliMetrePerSecond2(raw); });
}

// --- апаратний буфер ------------------------------------------------------

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::writeFifoControl(FifoMode mode,
                                                        std::uint8_t watermark) noexcept
{
    std::uint8_t value = regs::FifoModeField::insert(0, static_cast<std::uint8_t>(mode));
    value = regs::WatermarkField::insert(value, watermark);
    return writeByte(regs::Reg::FifoCtrl, value);
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::configureFifo(const FifoConfig &config) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    if (config.watermark >= regs::kFifoDepth) {
        return std::unexpected(Status::InvalidParam);
    }

    if (config.mode == FifoMode::Bypass) {
        if (auto outcome = writeFifoControl(FifoMode::Bypass, 0); !outcome) {
            return outcome;
        }
        return clearBits(regs::Reg::Ctrl5, regs::kCtrl5FifoEnable);
    }

    // Прохід через Bypass очищає вміст буфера: інакше перші вибірки нового
    // режиму приїхали б упереміш зі старими.
    if (auto outcome = writeFifoControl(FifoMode::Bypass, 0); !outcome) {
        return outcome;
    }
    if (auto outcome = setBits(regs::Reg::Ctrl5, regs::kCtrl5FifoEnable); !outcome) {
        return outcome;
    }
    return writeFifoControl(config.mode, config.watermark);
}

template <BusTransport Transport>
Result<void> Accelerometer<Transport>::restartFifo() noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }

    const std::uint8_t saved = shadow_.value(regs::Reg::FifoCtrl);
    const auto mode = static_cast<FifoMode>(regs::FifoModeField::extract(saved));
    const std::uint8_t watermark = regs::WatermarkField::extract(saved);

    if (mode == FifoMode::Bypass) {
        return {}; // нічого не накопичується — нічого й скидати
    }
    if (auto outcome = writeFifoControl(FifoMode::Bypass, 0); !outcome) {
        return outcome;
    }
    return writeFifoControl(mode, watermark);
}

template <BusTransport Transport>
Result<FifoStatus> Accelerometer<Transport>::fifoStatus() noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    auto value = readByte(regs::Reg::FifoSrc);
    if (!value) {
        return std::unexpected(value.error());
    }

    const bool empty = (*value & regs::kFifoSrcEmpty) != 0;
    return FifoStatus{
        .samples = empty ? std::uint8_t{0}
                         : static_cast<std::uint8_t>(*value & regs::kFifoSrcLevelMask),
        .watermarkHit = (*value & regs::kFifoSrcWatermark) != 0,
        .overrun = (*value & regs::kFifoSrcOverrun) != 0};
}

template <BusTransport Transport>
Result<std::size_t> Accelerometer<Transport>::readFifo(std::span<Acceleration> out) noexcept
{
    if (!initialised_) {
        return std::unexpected(Status::NotInitialised);
    }
    if (out.empty()) {
        return std::unexpected(Status::InvalidParam);
    }

    auto status = fifoStatus();
    if (!status) {
        return std::unexpected(status.error());
    }
    if (status->samples == 0) {
        return std::unexpected(Status::NoData);
    }

    std::size_t remaining = std::min<std::size_t>(status->samples, out.size());
    std::size_t done = 0;

    while (remaining > 0) {
        const std::size_t chunk = std::min(remaining, detail::kFifoChunkSamples);
        std::array<std::uint8_t, detail::kFifoChunkSamples * regs::kSampleBytes> buffer{};
        const auto view = std::span<std::uint8_t>{buffer}.first(chunk * regs::kSampleBytes);

        // Адреса всередині блоку OUT_* закільцьовується, тож одна транзакція
        // з автоінкрементом віддає підряд кілька повних вибірок.
        if (auto outcome = readBurst(regs::Reg::OutXL, view); !outcome) {
            return done > 0 ? Result<std::size_t>{done}
                            : Result<std::size_t>{std::unexpected(outcome.error())};
        }

        for (std::size_t i = 0; i < chunk; ++i) {
            const auto sample = std::span<const std::uint8_t>{view}
                                    .subspan(i * regs::kSampleBytes)
                                    .template first<regs::kSampleBytes>();
            out[done + i] = toSi(decode(sample));
        }

        done += chunk;
        remaining -= chunk;
    }

    return done;
}

// --- аварійне відновлення -------------------------------------------------

template <BusTransport Transport>
template <GpioLines Lines>
Result<void> Accelerometer<Transport>::recoverBus(Lines &lines) noexcept
{
    if (auto outcome = accel::recoverBus(lines); !outcome) {
        return outcome;
    }

    // Чип пережив дотактовування, але міг втратити конфігурацію разом із
    // живленням — звіряємо ідентифікатор і повертаємо налаштування з тіні.
    auto who = readByte(regs::Reg::WhoAmI);
    if (!who) {
        return std::unexpected(who.error());
    }
    if (*who != regs::kWhoAmIValue) {
        initialised_ = false;
        return std::unexpected(Status::NotFound);
    }
    return reapplyConfig();
}

} // namespace accel
