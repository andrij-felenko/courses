// Реалізація шаблона Sensor. Включається з sensor.hpp — окремо не збирається.
#pragma once

#include <algorithm>
#include <chrono>
#include <cstdlib>

namespace chip {
namespace detail {

using namespace std::chrono_literals;

inline constexpr float kGravity = 9.80665F;

inline constexpr auto kBootTimeout   = 20ms;
inline constexpr auto kDataTimeout   = 250ms;
inline constexpr auto kPollStep      = 1ms;
inline constexpr auto kSelfTestSettle = 90ms;

// Паспортне вікно самотесту для ±2 g, у мg (там один розряд — рівно 1 мg).
inline constexpr std::int32_t kSelfTestMinMg = 17;
inline constexpr std::int32_t kSelfTestMaxMg = 360;
inline constexpr unsigned     kSelfTestAvg   = 5;

/// Відлік лежить у двох байтах little-endian, вирівняний уліво: значущі
/// дванадцять біт сидять у старших розрядах.
[[nodiscard]] inline std::int16_t rawAxis(std::span<const std::byte, 2> pair) noexcept
{
    const auto lo = std::to_integer<std::uint16_t>(pair[0]);
    const auto hi = std::to_integer<std::uint16_t>(pair[1]);
    const auto packed = static_cast<std::int16_t>(static_cast<std::uint16_t>(lo | (hi << 8)));
    return static_cast<std::int16_t>(packed / 16);
}

[[nodiscard]] inline Vector3 decodeSample(std::span<const std::byte, kSampleBytes> raw,
                                          float lsb_to_ms2) noexcept
{
    return Vector3{
        .x = static_cast<float>(rawAxis(raw.subspan<0, 2>())) * lsb_to_ms2,
        .y = static_cast<float>(rawAxis(raw.subspan<2, 2>())) * lsb_to_ms2,
        .z = static_cast<float>(rawAxis(raw.subspan<4, 2>())) * lsb_to_ms2,
    };
}

/// Замість `goto restore` — деструктор: збудження самотесту знімається й
/// тоді, коли посеред перевірки впала шина.
template <typename F>
class ScopeExit {
public:
    explicit ScopeExit(F fn) noexcept : fn_{std::move(fn)} {}
    ~ScopeExit() { fn_(); }
    ScopeExit(const ScopeExit&) = delete;
    ScopeExit& operator=(const ScopeExit&) = delete;

private:
    F fn_;
};

} // namespace detail

// ---------------------------------------------------------------- транспорт

template <BusTransport Transport>
auto Sensor<Transport>::readRegs(std::uint8_t reg, std::span<std::byte> dst) -> Result
{
    return bus_.read(reg, dst);
}

template <BusTransport Transport>
auto Sensor<Transport>::readReg(reg::Reg r) -> std::expected<std::uint8_t, Status>
{
    std::byte value{};
    if (auto rc = bus_.read(reg::raw(r), std::span{&value, 1}); !rc) {
        return std::unexpected{rc.error()};
    }
    return std::to_integer<std::uint8_t>(value);
}

template <BusTransport Transport>
auto Sensor<Transport>::writeReg(reg::Reg r, std::uint8_t value) -> Result
{
    const auto byte = static_cast<std::byte>(value);
    return bus_.write(reg::raw(r), std::span{&byte, 1});
}

template <BusTransport Transport>
auto Sensor<Transport>::writeCtrl(reg::Reg r, std::uint8_t value) -> Result
{
    if (auto rc = writeReg(r, value); !rc) {
        return rc;
    }
    switch (r) {
    case reg::Reg::Ctrl1: shadow_ctrl1_ = value; break;
    case reg::Reg::Ctrl4: shadow_ctrl4_ = value; break;
    case reg::Reg::Ctrl5: shadow_ctrl5_ = value; break;
    default: break;
    }
    return {};
}

// ------------------------------------------------------ скидання й NVM

template <BusTransport Transport>
auto Sensor<Transport>::bootAndWait() -> Result
{
    if (auto rc = writeReg(reg::Reg::Ctrl5, reg::kCtrl5Boot); !rc) {
        return rc;
    }

    // BOOT самоскидний. Чекаємо квантовано: нескінченного опитування
    // прапорця тут бути не може.
    for (std::chrono::milliseconds waited{0}; waited < detail::kBootTimeout;
         waited += detail::kPollStep) {
        bus_.delay(detail::kPollStep);
        const auto ctrl5 = readReg(reg::Reg::Ctrl5);
        if (!ctrl5) {
            return std::unexpected{ctrl5.error()};
        }
        if ((*ctrl5 & reg::kCtrl5Boot) == 0U) {
            shadow_ctrl5_ = *ctrl5;
            return {};
        }
    }
    return std::unexpected{Status::Timeout};
}

template <BusTransport Transport>
auto Sensor<Transport>::reloadTrim() -> Result
{
    if (auto rc = bootAndWait(); !rc) {
        return rc;
    }

    // Справно піднята NVM лишає керувальні регістри в заводських значеннях.
    std::array<std::byte, 6> ctrl{};
    if (auto rc = readRegs(reg::autoIncrement(reg::Reg::Ctrl1), ctrl); !rc) {
        return rc;
    }
    if (std::to_integer<std::uint8_t>(ctrl[0]) != reg::kCtrl1ResetValue) {
        return std::unexpected{Status::CalibrationInvalid};
    }
    for (std::size_t i = 1; i < ctrl.size(); ++i) {
        if (ctrl[i] != std::byte{0}) {
            return std::unexpected{Status::CalibrationInvalid};
        }
    }

    shadow_ctrl1_ = std::to_integer<std::uint8_t>(ctrl[0]);
    shadow_ctrl4_ = std::to_integer<std::uint8_t>(ctrl[3]);
    shadow_ctrl5_ = std::to_integer<std::uint8_t>(ctrl[4]);
    return {};
}

template <BusTransport Transport>
auto Sensor<Transport>::softReset() -> Result
{
    auto rc = reloadTrim();
    initialized_ = false;
    sample_pending_.store(false, std::memory_order_release);
    return rc;
}

// ------------------------------------------------------- життєвий цикл

template <BusTransport Transport>
auto Sensor<Transport>::init() -> Result
{
    const auto who = readReg(reg::Reg::WhoAmI);
    if (!who) {
        return std::unexpected{who.error()};
    }
    if (*who != reg::kWhoAmIValue) {
        // Відповідь є, але це не наша мікросхема: переплутана адреса або
        // інший датчик на тій самій шині.
        return std::unexpected{Status::DeviceNotFound};
    }

    if (auto rc = reloadTrim(); !rc) {
        return rc;
    }
    if (auto rc = writeCtrl(reg::Reg::Ctrl4, reg::kCtrl4Bdu | reg::kCtrl4HighRes); !rc) {
        return rc;
    }
    const auto ctrl1 = static_cast<std::uint8_t>(
        reg::kCtrl1XyzEnable |
        (static_cast<std::uint8_t>(Odr::Hz100) << reg::kCtrl1OdrShift));
    if (auto rc = writeCtrl(reg::Reg::Ctrl1, ctrl1); !rc) {
        return rc;
    }

    range_       = Range::G2;
    lsb_to_ms2_  = mgPerLsb(Range::G2) * 0.001F * detail::kGravity;
    initialized_ = true;
    return {};
}

template <BusTransport Transport>
auto Sensor<Transport>::setRange(Range range) -> Result
{
    if (!initialized_) {
        return std::unexpected{Status::NotInitialized};
    }

    const auto ctrl4 = static_cast<std::uint8_t>(
        (shadow_ctrl4_ & static_cast<std::uint8_t>(~reg::kCtrl4FsMask)) |
        (static_cast<std::uint8_t>(range) << reg::kCtrl4FsShift));
    if (auto rc = writeCtrl(reg::Reg::Ctrl4, ctrl4); !rc) {
        return rc;
    }

    range_      = range;
    lsb_to_ms2_ = mgPerLsb(range) * 0.001F * detail::kGravity;
    return {};
}

template <BusTransport Transport>
auto Sensor<Transport>::setOdr(Odr odr) -> Result
{
    if (!initialized_) {
        return std::unexpected{Status::NotInitialized};
    }
    const auto ctrl1 = static_cast<std::uint8_t>(
        (shadow_ctrl1_ & static_cast<std::uint8_t>(~reg::kCtrl1OdrMask)) |
        (static_cast<std::uint8_t>(odr) << reg::kCtrl1OdrShift));
    return writeCtrl(reg::Reg::Ctrl1, ctrl1);
}

template <BusTransport Transport>
auto Sensor<Transport>::shutdown() -> Result
{
    if (!initialized_) {
        return std::unexpected{Status::NotInitialized};
    }
    const auto ctrl1 =
        static_cast<std::uint8_t>(shadow_ctrl1_ & static_cast<std::uint8_t>(~reg::kCtrl1OdrMask));
    if (auto rc = writeCtrl(reg::Reg::Ctrl1, ctrl1); !rc) {
        return rc;
    }
    initialized_ = false;
    sample_pending_.store(false, std::memory_order_release);
    return {};
}

// ----------------------------------------------------- читання відліків

template <BusTransport Transport>
auto Sensor<Transport>::readAcceleration() -> std::expected<Vector3, Status>
{
    if (!initialized_) {
        return std::unexpected{Status::NotInitialized};
    }

    const auto status = readReg(reg::Reg::Status);
    if (!status) {
        return std::unexpected{status.error()};
    }
    if ((*status & reg::kStatusZyxDataReady) == 0U) {
        return std::unexpected{Status::DataNotReady};
    }

    // Шість байтів однією транзакцією: під BDU вихідні регістри заморожені,
    // поки не прочитано старший байт, тож три осі — з одного моменту часу.
    std::array<std::byte, kSampleBytes> raw{};
    if (auto rc = readRegs(reg::autoIncrement(reg::Reg::OutXL), raw); !rc) {
        return std::unexpected{rc.error()};
    }

    sample_pending_.store(false, std::memory_order_release);
    return detail::decodeSample(std::span<const std::byte, kSampleBytes>{raw}, lsb_to_ms2_);
}

template <BusTransport Transport>
auto Sensor<Transport>::waitDataReady() -> Result
{
    for (std::chrono::milliseconds waited{0}; waited < detail::kDataTimeout;
         waited += detail::kPollStep) {
        const auto status = readReg(reg::Reg::Status);
        if (!status) {
            return std::unexpected{status.error()};
        }
        if ((*status & reg::kStatusZyxDataReady) != 0U) {
            return {};
        }
        bus_.delay(detail::kPollStep);
    }
    return std::unexpected{Status::Timeout};
}

// ------------------------------------------------------- апаратна черга

template <BusTransport Transport>
auto Sensor<Transport>::enableFifo(bool enable) -> Result
{
    if (!initialized_) {
        return std::unexpected{Status::NotInitialized};
    }

    const auto ctrl5 = enable
        ? static_cast<std::uint8_t>(shadow_ctrl5_ | reg::kCtrl5FifoEn)
        : static_cast<std::uint8_t>(shadow_ctrl5_ &
                                    static_cast<std::uint8_t>(~reg::kCtrl5FifoEn));
    if (auto rc = writeCtrl(reg::Reg::Ctrl5, ctrl5); !rc) {
        return rc;
    }

    // Черга перезапускається лише через Bypass: без цього кроку після
    // переповнення вона так і лишиться закритою.
    if (auto rc = writeReg(reg::Reg::FifoCtrl, reg::kFifoModeBypass); !rc) {
        return rc;
    }
    if (!enable) {
        return {};
    }
    return writeReg(reg::Reg::FifoCtrl, reg::kFifoModeStream);
}

template <BusTransport Transport>
auto Sensor<Transport>::readFifo(FifoScratch& scratch, std::span<Vector3> out)
    -> std::expected<FifoBatch, Status>
{
    if (!initialized_) {
        return std::unexpected{Status::NotInitialized};
    }
    if (out.empty()) {
        return std::unexpected{Status::InvalidParam};
    }

    const auto src = readReg(reg::Reg::FifoSrc);
    if (!src) {
        return std::unexpected{src.error()};
    }

    FifoBatch batch{};
    batch.overrun   = (*src & reg::kFifoSrcOverrun) != 0U;
    batch.watermark = (*src & reg::kFifoSrcWatermark) != 0U;

    std::size_t available = *src & reg::kFifoSrcCountMask;
    available = std::min({available, kFifoDepth, out.size()});
    if (available == 0) {
        return std::unexpected{Status::DataNotReady};
    }

    // Одна пакетна транзакція на всю порцію: читання OUT_X_L з
    // автоінкрементом просуває чергу на відлік за кожні шість байтів.
    const auto bytes = scratch.head(available * kSampleBytes);
    if (auto rc = readRegs(reg::autoIncrement(reg::Reg::OutXL), bytes); !rc) {
        return std::unexpected{rc.error()};
    }

    for (std::size_t i = 0; i < available; ++i) {
        const std::span<const std::byte, kSampleBytes> one{
            bytes.data() + i * kSampleBytes, kSampleBytes};
        out[i] = detail::decodeSample(one, lsb_to_ms2_);
    }
    batch.samples = out.first(available);
    sample_pending_.store(false, std::memory_order_release);

    if (batch.overrun) {
        // Дані віддали, але попередили: частину відліків утрачено, і чергу
        // треба перезапустити через Bypass.
        if (auto rc = enableFifo(true); !rc) {
            return std::unexpected{rc.error()};
        }
    }
    return batch;
}

// ------------------------------------------------------------- самотест

template <BusTransport Transport>
auto Sensor<Transport>::averageRaw(unsigned count)
    -> std::expected<std::array<std::int32_t, 3>, Status>
{
    std::array<std::byte, kSampleBytes> raw{};
    std::array<std::int32_t, 3> sum{0, 0, 0};

    // Перший відлік після зміни режиму відкидаємо: він іще від старих
    // налаштувань.
    if (auto rc = waitDataReady(); !rc) {
        return std::unexpected{rc.error()};
    }
    if (auto rc = readRegs(reg::autoIncrement(reg::Reg::OutXL), raw); !rc) {
        return std::unexpected{rc.error()};
    }

    for (unsigned i = 0; i < count; ++i) {
        if (auto rc = waitDataReady(); !rc) {
            return std::unexpected{rc.error()};
        }
        if (auto rc = readRegs(reg::autoIncrement(reg::Reg::OutXL), raw); !rc) {
            return std::unexpected{rc.error()};
        }
        const std::span<const std::byte, kSampleBytes> view{raw};
        sum[0] += detail::rawAxis(view.subspan<0, 2>());
        sum[1] += detail::rawAxis(view.subspan<2, 2>());
        sum[2] += detail::rawAxis(view.subspan<4, 2>());
    }

    for (auto& value : sum) {
        value /= static_cast<std::int32_t>(count);
    }
    return sum;
}

template <BusTransport Transport>
auto Sensor<Transport>::selfTest() -> Result
{
    if (!initialized_) {
        return std::unexpected{Status::NotInitialized};
    }

    const std::uint8_t saved_ctrl1 = shadow_ctrl1_;
    const std::uint8_t saved_ctrl4 = shadow_ctrl4_;
    const Range saved_range = range_;

    detail::ScopeExit restore{[&] {
        (void)writeCtrl(reg::Reg::Ctrl4, saved_ctrl4);
        (void)writeCtrl(reg::Reg::Ctrl1, saved_ctrl1);
        range_      = saved_range;
        lsb_to_ms2_ = mgPerLsb(saved_range) * 0.001F * detail::kGravity;
    }};

    // Паспортне вікно задано для ±2 g, високого роздільного, 50 Гц.
    if (auto rc = writeCtrl(reg::Reg::Ctrl4, reg::kCtrl4Bdu | reg::kCtrl4HighRes); !rc) {
        return rc;
    }
    const auto ctrl1 = static_cast<std::uint8_t>(
        reg::kCtrl1XyzEnable |
        (static_cast<std::uint8_t>(Odr::Hz50) << reg::kCtrl1OdrShift));
    if (auto rc = writeCtrl(reg::Reg::Ctrl1, ctrl1); !rc) {
        return rc;
    }
    bus_.delay(detail::kSelfTestSettle);

    const auto base = averageRaw(detail::kSelfTestAvg);
    if (!base) {
        return std::unexpected{base.error()};
    }

    // Умикаємо електростатичне збудження маси.
    if (auto rc = writeCtrl(reg::Reg::Ctrl4,
                            reg::kCtrl4Bdu | reg::kCtrl4HighRes | reg::kCtrl4SelfTest0);
        !rc) {
        return rc;
    }
    bus_.delay(detail::kSelfTestSettle);

    const auto excited = averageRaw(detail::kSelfTestAvg);
    if (!excited) {
        return std::unexpected{excited.error()};
    }

    for (std::size_t axis = 0; axis < 3; ++axis) {
        const auto delta = std::abs((*excited)[axis] - (*base)[axis]);
        if (delta < detail::kSelfTestMinMg || delta > detail::kSelfTestMaxMg) {
            return std::unexpected{Status::SelfTestFailed};
        }
    }
    return {};
}

} // namespace chip
