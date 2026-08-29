#pragma once

#include "bsp/status.hpp"
#include "bsp/types.hpp"

#include <chrono>
#include <cstdint>
#include <span>

namespace bsp {

/** Умовні номери портів GPIO у нотації плати. */
enum class GpioPort : std::uint8_t { A = 0, B = 1, C = 2 };

struct Pin {
    GpioPort      port{};
    std::uint8_t  number{};
};

enum class PinMode : std::uint8_t {
    Analog = 0,  ///< Hi-Z без підтяжок і вхідного буфера (нуль витоку)
    Input,
    InputPullUp,
    OutputPushPull,
    OutputOpenDrain,
    Alternate    ///< вивід віддано периферії
};

/**
 * @brief Межа вниз: усе, чого BSP вимагає від вендорного шару.
 *
 * Перенесення плати на інший мікроконтролер — це новий нащадок IPlatform,
 * і жодного рядка в реалізації контракту чи в застосунку.
 */
class IPlatform {
public:
    virtual ~IPlatform() = default;

    [[nodiscard]] virtual Result clock_init() noexcept = 0;

    virtual void pin_mode(Pin pin, PinMode mode) noexcept = 0;
    virtual void pin_write(Pin pin, bool level) noexcept = 0;
    [[nodiscard]] virtual bool pin_read(Pin pin) const noexcept = 0;

    [[nodiscard]] virtual Result i2c_init() noexcept = 0;
    virtual void i2c_deinit() noexcept = 0;

    /* Розмір буфера їде разом із покажчиком — окремого аргументу довжини немає. */
    [[nodiscard]] virtual Result i2c_write(std::uint8_t addr,
                                           std::span<const std::uint8_t> tx) noexcept = 0;
    [[nodiscard]] virtual Result i2c_read(std::uint8_t addr,
                                          std::span<std::uint8_t> rx) noexcept = 0;
    [[nodiscard]] virtual Result i2c_write_read(std::uint8_t addr,
                                                std::span<const std::uint8_t> tx,
                                                std::span<std::uint8_t> rx) noexcept = 0;

    [[nodiscard]] virtual Result adc_init() noexcept = 0;
    virtual void adc_deinit() noexcept = 0;
    /** Оцифрування каналу з апаратним усередненням 16 вибірок; 12 біт. */
    [[nodiscard]] virtual std::expected<std::uint16_t, Status>
        adc_sample(std::uint8_t channel) noexcept = 0;
    /** Заводська константа Vrefint (код АЦП, знятий на 3.000 В). */
    [[nodiscard]] virtual std::uint16_t vrefint_cal() const noexcept = 0;

    [[nodiscard]] virtual std::chrono::milliseconds tick() const noexcept = 0;
    virtual void delay(std::chrono::microseconds us) const noexcept = 0;

    /** М'ютекс спільної шини з успадкуванням пріоритетів. */
    [[nodiscard]] virtual bool try_lock_bus(std::chrono::milliseconds timeout) noexcept = 0;
    virtual void unlock_bus() noexcept = 0;

    /** Дочекатися спустошення черг UART і завершення передач DMA. */
    [[nodiscard]] virtual Result flush_async_io(std::chrono::milliseconds timeout) noexcept = 0;
    /** Зупинити ядро до пробудження від RTC або зовнішньої лінії. */
    [[nodiscard]] virtual Result enter_stop(SleepMode mode,
                                            std::chrono::milliseconds timeout) noexcept = 0;

    [[nodiscard]] virtual bool in_isr() const noexcept = 0;
};

/**
 * @brief RAII-захоплення шини: розблокування не можна забути навіть на throw.
 */
class [[nodiscard]] BusLock {
public:
    BusLock(IPlatform& platform, std::chrono::milliseconds timeout) noexcept
        : platform_{&platform}, held_{platform.try_lock_bus(timeout)} {}

    ~BusLock() {
        if (held_) {
            platform_->unlock_bus();
        }
    }

    BusLock(const BusLock&) = delete;
    BusLock& operator=(const BusLock&) = delete;
    BusLock(BusLock&&) = delete;
    BusLock& operator=(BusLock&&) = delete;

    [[nodiscard]] explicit operator bool() const noexcept { return held_; }

private:
    IPlatform* platform_;
    bool       held_;
};

} // namespace bsp
