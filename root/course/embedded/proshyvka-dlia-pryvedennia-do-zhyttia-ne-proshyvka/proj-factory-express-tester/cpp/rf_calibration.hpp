#pragma once

#include <array>
#include <cstdint>
#include <limits>

#include "fct.hpp"
#include "hal.hpp"
#include "platform_probe.hpp"

// Радіотракт: несуча на трьох каналах, підстроювання кварцу за виміром
// стенда й запис знайденого коду в OTP. Мережевого з'єднання немає —
// на конвеєрі на нього немає ні часу, ні чистого ефіру.

namespace fct {

inline constexpr std::int16_t kCwPowerDdbm = 40;      // +4.0 dBm
inline constexpr std::int32_t kCwPowerTolDdbm = 15;   // ±1.5 dBm
inline constexpr std::uint32_t kCwSettleUs = 2'000;
inline constexpr std::uint32_t kRfMeasTimeoutUs = 100'000;

inline constexpr std::int32_t kXoPpmLimit = 10;
inline constexpr int kXoMaxSteps = 32;

inline constexpr std::uint32_t kOtpTrimSignature = 0xCA5A0000u;
inline constexpr std::int32_t kOtpVddaMinMv = 3200;
inline constexpr std::int32_t kOtpVddaMaxMv = 3400;

inline constexpr std::array<std::uint32_t, 3> kChannelsKhz{2'402'000, 2'440'000,
                                                           2'480'000};
inline constexpr std::uint32_t kCalChannelKhz = 2'440'000;

// Знайдений код ємнісного масиву: пустий — калібрування не відпрацювало,
// і в OTP писати нічого.
inline std::optional<std::uint8_t> g_trim_found{};

// Несуча як RAII: хоч би куди вийшов тест, ефір лишається чистим.
class CwTone {
public:
    CwTone(std::uint32_t freq_khz, std::int16_t power_ddbm) noexcept
        : on_{hal::radio_cw_start(freq_khz, power_ddbm)}
    {
        if (on_) {
            hal::delay_us(kCwSettleUs);
        }
    }

    ~CwTone()
    {
        if (on_) {
            hal::radio_cw_stop();
        }
    }

    CwTone(const CwTone&) = delete;
    CwTone& operator=(const CwTone&) = delete;

    [[nodiscard]] bool on() const noexcept { return on_; }

private:
    bool on_;
};

[[nodiscard]] inline std::expected<hal::RfMeasurement, Failure> measure_channel(
    std::uint32_t freq_khz) noexcept
{
    const CwTone tone{freq_khz, kCwPowerDdbm};
    if (!tone.on()) {
        return fail(Error::Fail, "Трансивер не вмикає несучу",
                    static_cast<std::int32_t>(freq_khz / 1000), "MHz");
    }
    const auto meas = hal::stand_measure_rf(freq_khz, kRfMeasTimeoutUs);
    if (!meas) {
        return fail(Error::Timeout, "Вимірювач стенда не відповів",
                    static_cast<std::int32_t>(freq_khz / 1000), "MHz");
    }
    return *meas;
}

// 1 ppm на 2440 МГц — це 2440 Гц; ділимо з округленням до найближчого.
[[nodiscard]] constexpr std::int32_t hz_to_ppm(std::int32_t error_hz,
                                               std::uint32_t freq_khz) noexcept
{
    const std::int32_t per_ppm = static_cast<std::int32_t>(freq_khz / 1000);
    const std::int32_t half = per_ppm / 2;
    return error_hz >= 0 ? (error_hz + half) / per_ppm : (error_hz - half) / per_ppm;
}

[[nodiscard]] constexpr std::int32_t abs32(std::int32_t x) noexcept
{
    return x < 0 ? -x : x;
}

inline Outcome test_rf_cw() noexcept
{
    g_trim_found.reset();

    if (!hal::radio_init()) {
        return fail(Error::Fail, "Трансивер не ініціалізується");
    }

    // 1. Потужність на нижньому, середньому й верхньому каналах.
    for (const auto freq_khz : kChannelsKhz) {
        const auto meas = measure_channel(freq_khz);
        if (!meas) {
            return std::unexpected(meas.error());
        }
        const std::int32_t dev = abs32(std::int32_t{meas->power_ddbm} - kCwPowerDdbm);
        if (dev > kCwPowerTolDdbm) {
            return fail(Error::Fail,
                        "P_out поза ±1.5 dBm: балун, фільтр або імпеданс доріжки",
                        meas->power_ddbm, "ddBm");
        }
        hal::watchdog_kick();
    }

    // 2. Підстроювання кварцу. Ємність масиву тягне частоту вниз, тому
    // додатне відхилення лікуємо більшим кодом, від'ємне — меншим.
    std::uint8_t trim = hal::radio_xo_trim();
    std::uint8_t best_trim = trim;
    std::int32_t best_ppm = std::numeric_limits<std::int32_t>::max();
    std::optional<std::int32_t> prev_ppm{};

    for (int step = 0; step < kXoMaxSteps; ++step) {
        hal::radio_xo_trim_set(trim);

        const auto meas = measure_channel(kCalChannelKhz);
        if (!meas) {
            return std::unexpected(meas.error());
        }
        const std::int32_t ppm = hz_to_ppm(meas->freq_error_hz, kCalChannelKhz);
        if (abs32(ppm) < abs32(best_ppm)) {
            best_ppm = ppm;
            best_trim = trim;
        }
        if (abs32(ppm) <= kXoPpmLimit) {
            break;
        }
        // Знак перескочив: сусідні коди вже по різні боки нуля.
        if (prev_ppm && (ppm > 0) != (*prev_ppm > 0)) {
            break;
        }
        if (ppm > 0) {
            if (trim >= hal::kXoTrimMax) {
                break;
            }
            ++trim;
        } else {
            if (trim == 0) {
                break;
            }
            --trim;
        }
        prev_ppm = ppm;
        hal::watchdog_kick();
    }

    hal::radio_xo_trim_set(best_trim);
    if (abs32(best_ppm) > kXoPpmLimit) {
        return fail(Error::Fail, "Кварц не заганяється в ±10 ppm", best_ppm, "ppm");
    }

    g_trim_found = best_trim;
    return pass("Несуча в допуску, кварц підстроєний", best_ppm, "ppm");
}

inline Outcome test_otp_trim() noexcept
{
    if (!g_trim_found) {
        return fail(Error::Skipped, "Немає калібрувального коду — писати нічого");
    }

    const std::uint32_t trim = *g_trim_found & 0x3Fu;
    // Слово несе код і його доповнення: напівпропалений біт видно одразу.
    const std::uint32_t word = kOtpTrimSignature | (trim << 8) | (~trim & 0x3Fu);

    const auto stored = hal::otp_read(hal::kOtpWordXoTrim);
    if (!stored) {
        return fail(Error::Fail, "OTP: слово не читається");
    }
    if (*stored != 0) {
        // Плата вже проходила стенд: перепалити не можна, лише звірити.
        if (*stored != word) {
            return fail(Error::InvalidId, "OTP уже містить інший код",
                        static_cast<std::int32_t>((*stored >> 8) & 0x3Fu), "trim");
        }
        return pass("OTP уже пропалений тим самим кодом",
                    static_cast<std::int32_t>(trim), "trim");
    }

    const auto before = read_vdda_mv();
    if (!before) {
        return std::unexpected(before.error());
    }
    if (*before < kOtpVddaMinMv || *before > kOtpVddaMaxMv) {
        return fail(Error::Fail, "V_DDA поза вікном пропалювання", *before, "mV");
    }

    if (!hal::otp_write(hal::kOtpWordXoTrim, word)) {
        return fail(Error::Fail, "OTP: контролер відмовив у записі");
    }

    // Просідання під час імпульсу 200 мА лишає біт напівпропаленим, і дефект
    // випливе вже в полі — тому міряємо напругу ще й після запису.
    const auto after = read_vdda_mv();
    if (!after) {
        return std::unexpected(after.error());
    }
    if (*after < kOtpVddaMinMv) {
        return fail(Error::Fail, "V_DDA просіла під час пропалювання", *after, "mV");
    }

    const auto readback = hal::otp_read(hal::kOtpWordXoTrim);
    if (!readback || *readback != word) {
        return fail(Error::Fail, "OTP: зчитане слово не збіглося із записаним");
    }

    return pass("Код підстроювання пропалений і звірений",
                static_cast<std::int32_t>(trim), "trim");
}

}  // namespace fct
