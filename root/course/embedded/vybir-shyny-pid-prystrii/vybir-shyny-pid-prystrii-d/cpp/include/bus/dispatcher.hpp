// Неблокуючий диспетчер шин I2C та SPI, C++23.
//
// Той самий предмет, що й у версії на C, але контракт інший: буфери приходять
// як std::span (довжина невіддільна від вказівника), помилка постановки — це
// std::expected, а лінія CS живе як RAII-об'єкт, який неможливо забути підняти.
#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <type_traits>

#include "stm32h7xx_hal.h"

namespace bus {

enum class Result : std::uint8_t { Ok, HardwareError, Timeout, BusLocked };
enum class Op : std::uint8_t { Read, Write, Transfer };
enum class SubmitError : std::uint8_t { QueueFull, NoDevice, EmptyTransaction, CommandTooLong };

// Режим тактування SPI одним значенням замість пари констант HAL.
enum class SpiMode : std::uint8_t { Mode0, Mode1, Mode2, Mode3 };

constexpr std::uint32_t clock_polarity(SpiMode mode) noexcept
{
    return (mode == SpiMode::Mode2 || mode == SpiMode::Mode3) ? SPI_POLARITY_HIGH
                                                              : SPI_POLARITY_LOW;
}

constexpr std::uint32_t clock_phase(SpiMode mode) noexcept
{
    return (mode == SpiMode::Mode1 || mode == SpiMode::Mode3) ? SPI_PHASE_2EDGE
                                                              : SPI_PHASE_1EDGE;
}

struct I2cLines {
    GPIO_TypeDef* scl_port{};
    std::uint16_t scl_pin{};
    GPIO_TypeDef* sda_port{};
    std::uint16_t sda_pin{};
    std::uint8_t  alternate{};   // GPIO_AF4_I2C1 тощо
};

enum class RecoveryOutcome : std::uint8_t { NotStuck, Released, StillStuck, ReinitFailed };

// Дев'ять тактів SCL і ручний СТОП — лікування пастки «I2C Bus Lockup».
RecoveryOutcome recover_i2c_bus(I2C_HandleTypeDef& i2c, const I2cLines& lines) noexcept;

struct Device {
    std::uint16_t i2c_address{};        // 7-бітна, без зсуву
    GPIO_TypeDef* cs_port{};
    std::uint16_t cs_pin{};
    SpiMode       spi_mode{SpiMode::Mode0};
    std::uint32_t spi_prescaler{SPI_BAUDRATEPRESCALER_8};
};

// Команда чипа: адреса регістра для I2C або довільні байти для SPI.
// Зберігається за значенням, тому не залежить від часу життя аргументів.
class Command {
public:
    static constexpr std::size_t kMaxBytes = 4;

    constexpr Command() noexcept = default;

    static constexpr Command reg8(std::uint8_t reg) noexcept
    {
        Command cmd;
        cmd.bytes_[0] = reg;
        cmd.size_ = 1;
        return cmd;
    }

    static constexpr Command reg16(std::uint16_t reg) noexcept
    {
        Command cmd;
        cmd.bytes_[0] = static_cast<std::uint8_t>(reg >> 8);
        cmd.bytes_[1] = static_cast<std::uint8_t>(reg);
        cmd.size_ = 2;
        return cmd;
    }

    static constexpr Command raw(std::initializer_list<std::uint8_t> data) noexcept
    {
        Command cmd;
        for (std::uint8_t byte : data) {
            if (cmd.size_ == kMaxBytes) {
                break;
            }
            cmd.bytes_[cmd.size_++] = byte;
        }
        return cmd;
    }

    [[nodiscard]] constexpr std::size_t size() const noexcept { return size_; }
    [[nodiscard]] constexpr bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] std::uint8_t* data() noexcept { return bytes_.data(); }

    // Апаратний блок I2C вміє сам віддати адресу регістра — але лише 8 або 16 бітів.
    [[nodiscard]] constexpr std::optional<std::uint16_t> memory_address() const noexcept
    {
        if (size_ == 1) {
            return bytes_[0];
        }
        if (size_ == 2) {
            return static_cast<std::uint16_t>((bytes_[0] << 8) | bytes_[1]);
        }
        return std::nullopt;
    }

    [[nodiscard]] constexpr std::uint32_t memory_address_size() const noexcept
    {
        return (size_ == 2) ? I2C_MEMADD_SIZE_16BIT : I2C_MEMADD_SIZE_8BIT;
    }

private:
    std::array<std::uint8_t, kMaxBytes> bytes_{};
    std::uint8_t size_{0};
};

// Ненав'язливий колбек: зберігає посилання на довгоживучий об'єкт-обробник і
// вказівник на функцію. Без купи, без std::function, без прихованих алокацій
// у перериванні. Тимчасовий об'єкт прив'язати не можна — він не переживе обміну.
class Completion {
public:
    constexpr Completion() noexcept = default;

    template <class F>
        requires std::is_invocable_v<F&, Result>
    explicit Completion(F& handler) noexcept
        : context_{&handler},
          invoke_{[](void* ctx, Result result) { (*static_cast<F*>(ctx))(result); }}
    {
    }

    template <class F>
    Completion(F&& handler) = delete;

    void operator()(Result result) const
    {
        if (invoke_ != nullptr) {
            invoke_(context_, result);
        }
    }

    [[nodiscard]] explicit operator bool() const noexcept { return invoke_ != nullptr; }

private:
    void* context_{nullptr};
    void (*invoke_)(void*, Result){nullptr};
};

struct Transaction {
    const Device*                 device{nullptr};
    Op                            op{Op::Read};
    Command                       command{};
    std::span<const std::uint8_t> tx{};
    std::span<std::uint8_t>       rx{};
    Completion                    done{};
    std::uint32_t                 timeout_ms{5};
};

// CS живе рівно стільки, скільки триває транзакція: об'єкт створюють перед
// стартом обміну й руйнують у коді завершення, хай там помилка чи успіх.
class ChipSelect {
public:
    explicit ChipSelect(const Device& device) noexcept : device_{&device}
    {
        if (device_->cs_port != nullptr) {
            HAL_GPIO_WritePin(device_->cs_port, device_->cs_pin, GPIO_PIN_RESET);
        }
    }

    ChipSelect(const ChipSelect&) = delete;
    ChipSelect& operator=(const ChipSelect&) = delete;

    ~ChipSelect()
    {
        if (device_->cs_port != nullptr) {
            HAL_GPIO_WritePin(device_->cs_port, device_->cs_pin, GPIO_PIN_SET);
        }
    }

private:
    const Device* device_;
};

// Маскування переривань на кілька інструкцій — теж ресурс, теж RAII.
class IrqLock {
public:
    IrqLock() noexcept : primask_{__get_PRIMASK()} { __disable_irq(); }
    IrqLock(const IrqLock&) = delete;
    IrqLock& operator=(const IrqLock&) = delete;
    ~IrqLock()
    {
        if (primask_ == 0U) {
            __enable_irq();
        }
    }

private:
    std::uint32_t primask_;
};

class Dispatcher {
public:
    static constexpr std::size_t kQueueCapacity = 16;

    struct Stats {
        std::uint32_t done{};
        std::uint32_t failed{};
        std::uint32_t dropped{};
        std::uint32_t recovered{};
    };

    Dispatcher(I2C_HandleTypeDef& i2c, const I2cLines& lines) noexcept;
    explicit Dispatcher(SPI_HandleTypeDef& spi) noexcept;
    ~Dispatcher();

    Dispatcher(const Dispatcher&) = delete;
    Dispatcher& operator=(const Dispatcher&) = delete;

    // Кладе транзакцію в чергу. Буфери tx/rx лишаються за клієнтом і мусять
    // жити до виклику Completion.
    [[nodiscard]] std::expected<void, SubmitError> submit(const Transaction& txn) noexcept;

    // З головного циклу: нагляд за таймаутом і відкладене лікування шини I2C.
    void poll() noexcept;

    [[nodiscard]] Stats stats() const noexcept { return stats_; }

    // Місток від слабких колбеків HAL.
    static Dispatcher* from_handle(const void* hal_handle) noexcept;
    void on_transfer_complete() noexcept;
    void on_error() noexcept;

private:
    enum class Kind : std::uint8_t { I2c, Spi };
    enum class Phase : std::uint8_t { Idle, CommandBytes, Data };

    [[nodiscard]] Result start_current() noexcept;
    [[nodiscard]] HAL_StatusTypeDef start_i2c(Transaction& txn) noexcept;
    [[nodiscard]] HAL_StatusTypeDef start_spi_data(Transaction& txn) noexcept;
    void apply_spi_mode(const Device& device) noexcept;
    void complete(Result result) noexcept;

    Kind      kind_;
    void*     handle_;
    I2cLines  lines_{};

    std::array<Transaction, kQueueCapacity> queue_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
    volatile bool  busy_{false};
    volatile Phase phase_{Phase::Idle};
    volatile bool  needs_recovery_{false};
    std::uint32_t  started_ms_{0};

    std::optional<ChipSelect> chip_select_{};
    Stats stats_{};
};

}  // namespace bus
