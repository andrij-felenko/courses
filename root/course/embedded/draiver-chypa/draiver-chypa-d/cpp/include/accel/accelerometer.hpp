// accelerometer.hpp — Рівень 3: драйвер чипа в термінах предметної області.
//
// Стан живе в екземплярі класу, а не в глобальних змінних, тому два однакові
// чипи на різних шинах — це просто два об'єкти. Транспорт передається за
// значенням і належить драйверові: час життя шини й час життя драйвера
// збігаються самі собою, без ручного закриття дескрипторів.
#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <span>

#include "registers.hpp"
#include "shadow_registers.hpp"
#include "status.hpp"
#include "transport.hpp"
#include "types.hpp"

namespace accel {

template <BusTransport Transport>
class Accelerometer {
public:
    struct Config {
        Range      range{Range::G2};
        Odr        odr{Odr::Hz100};
        Resolution resolution{Resolution::Bits16};
    };

    explicit Accelerometer(Transport transport) noexcept;

    // Життєвий цикл: перевірка WHO_AM_I, підняття тіні зі справжніх регістрів,
    // BDU, діапазон, частота, осі.
    [[nodiscard]] Result<void> initialise(const Config &config) noexcept;
    [[nodiscard]] Result<void> shutdown() noexcept;

    // Конфігурація
    [[nodiscard]] Result<void> setRange(Range range) noexcept;
    [[nodiscard]] Result<void> setOdr(Odr odr) noexcept;
    [[nodiscard]] Result<void> setLowPower(bool enable) noexcept;
    void setCalibration(const Calibration &calibration) noexcept;

    // Переривання: обробник лише сигналить задачі, шину читає задача.
    [[nodiscard]] Result<void> enableDataReadyInterrupt(bool enable) noexcept;
    [[nodiscard]] Result<void> enableWatermarkInterrupt(bool enable) noexcept;

    // Читання
    [[nodiscard]] Result<DataStatus> dataStatus() noexcept;
    [[nodiscard]] Result<void> waitForData(std::chrono::milliseconds timeout) noexcept;
    [[nodiscard]] Result<RawSample> readRaw() noexcept;
    [[nodiscard]] Result<Acceleration> readAcceleration() noexcept;

    // Два цілочисельні шляхи для ядер без FPU: у мілігравітаціях (звичний
    // для даташита вимір) і одразу в SI, у міліметрах на секунду в квадраті.
    [[nodiscard]] Result<MilliG> readMilliG() noexcept;
    [[nodiscard]] Result<MilliMetrePerSecond2> readMilliMetrePerSecond2() noexcept;

    // Апаратний буфер
    [[nodiscard]] Result<void> configureFifo(const FifoConfig &config) noexcept;
    [[nodiscard]] Result<void> restartFifo() noexcept;
    [[nodiscard]] Result<FifoStatus> fifoStatus() noexcept;
    [[nodiscard]] Result<std::size_t> readFifo(std::span<Acceleration> out) noexcept;

    // Аварійне скидання шини лініями GPIO з подальшим поверненням
    // конфігурації з тіньових регістрів.
    template <GpioLines Lines>
    [[nodiscard]] Result<void> recoverBus(Lines &lines) noexcept;

    [[nodiscard]] Acceleration toSi(const RawSample &raw) const noexcept;
    [[nodiscard]] MilliG toMilliG(const RawSample &raw) const noexcept;
    [[nodiscard]] MilliMetrePerSecond2 toMilliMetrePerSecond2(const RawSample &raw) const noexcept;

    [[nodiscard]] bool initialised() const noexcept { return initialised_; }
    [[nodiscard]] Range range() const noexcept { return config_.range; }
    [[nodiscard]] Transport &transport() noexcept { return transport_; }

private:
    [[nodiscard]] Result<std::uint8_t> readByte(regs::Reg reg) noexcept;
    [[nodiscard]] Result<void> writeByte(regs::Reg reg, std::uint8_t value) noexcept;

    template <typename FieldType>
    [[nodiscard]] Result<void> updateField(regs::Reg reg, std::uint8_t value) noexcept;

    [[nodiscard]] Result<void> setBits(regs::Reg reg, std::uint8_t bits) noexcept;
    [[nodiscard]] Result<void> clearBits(regs::Reg reg, std::uint8_t bits) noexcept;
    [[nodiscard]] Result<void> readBurst(regs::Reg start, std::span<std::uint8_t> out) noexcept;
    [[nodiscard]] Result<void> syncShadow() noexcept;
    [[nodiscard]] Result<void> reapplyConfig() noexcept;
    [[nodiscard]] Result<void> writeFifoControl(FifoMode mode, std::uint8_t watermark) noexcept;

    [[nodiscard]] RawSample decode(std::span<const std::uint8_t, regs::kSampleBytes> bytes) const noexcept;
    void applyScale() noexcept;

    Transport   transport_;
    Config      config_{};
    ShadowBank  shadow_{};
    Calibration calibration_{};
    float       scaleSi_{0.0F};
    bool        initialised_{false};
};

} // namespace accel

#include "accelerometer.inl"
