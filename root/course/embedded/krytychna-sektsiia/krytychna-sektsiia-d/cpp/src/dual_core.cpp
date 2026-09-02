// Два ядра — дві незалежні маски. CPSID i на одному ядрі нічого не забороняє
// другому, тому спільну памʼять замикаємо ще й апаратним спінлоком.
// Приклад для RP2040: два Cortex-M0+ і блок SIO.
#include <cstdint>
#include <expected>

#include "demo/demos.hpp"
#include "mcu/critical_section.hpp"

namespace {

constexpr std::uintptr_t kSioBase = 0xD0000000UL;
constexpr std::uint32_t kMailboxLock = 0U;
constexpr std::uint32_t kSpinLimit = 10000U;

// Читання регістра повертає ненуль, якщо лок дістався нам, і 0, якщо ним
// володіє інше ядро. Запис будь-якого значення звільняє лок.
[[nodiscard]] volatile std::uint32_t& spinlock(std::uint32_t index) noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(kSioBase + 0x100U + 4U * index);
}

struct Mailbox {
    std::uint32_t seq; // лічильник публікацій
    std::int32_t setpoint_ma;
    std::int32_t measured_ma;
};

// Лінкер кладе структуру в ділянку SRAM, видиму обом ядрам.
volatile Mailbox g_mailbox{};

// Вартовий апаратного спінлока з обмеженим очікуванням: якщо друге ядро тримає
// лок надто довго, це вже несправність, і вічний цикл її лише сховає.
class [[nodiscard]] SpinlockGuard {
public:
    explicit SpinlockGuard(std::uint32_t index) noexcept : index_{index}
    {
        for (std::uint32_t spins = 0; spins < kSpinLimit; ++spins) {
            if (spinlock(index_) != 0U) {
                mcu::cpu::dmb(); // усе нижче не має випередити захоплення лока
                held_ = true;
                return;
            }
        }
    }

    ~SpinlockGuard() noexcept
    {
        if (held_) {
            mcu::cpu::dmb();
            spinlock(index_) = 1U;
        }
    }

    [[nodiscard]] bool held() const noexcept { return held_; }

    SpinlockGuard(const SpinlockGuard&) = delete;
    SpinlockGuard& operator=(const SpinlockGuard&) = delete;
    SpinlockGuard(SpinlockGuard&&) = delete;
    SpinlockGuard& operator=(SpinlockGuard&&) = delete;

private:
    std::uint32_t index_;
    bool held_{false};
};

} // namespace

namespace demo {

std::expected<void, MailboxError> mailbox_publish(std::int32_t setpoint_ma,
                                                  std::int32_t measured_ma) noexcept
{
    // Порядок обовʼязковий: спершу свої переривання, потім міжʼядерний лок.
    // Навпаки — обробник цього ж ядра зайде сюди й чекатиме на лок, який
    // тримає воно саме. Це глухий кут, з якого виходять лише перезавантаженням.
    const mcu::CriticalSectionGuard local;
    const SpinlockGuard shared{kMailboxLock};

    if (!shared.held()) {
        return std::unexpected(MailboxError::LockTimeout);
    }

    g_mailbox.seq = g_mailbox.seq + 1;
    g_mailbox.setpoint_ma = setpoint_ma;
    g_mailbox.measured_ma = measured_ma;
    return {};
}

std::expected<std::int32_t, MailboxError> mailbox_read_setpoint() noexcept
{
    const mcu::CriticalSectionGuard local;
    const SpinlockGuard shared{kMailboxLock};

    if (!shared.held()) {
        return std::unexpected(MailboxError::LockTimeout);
    }
    return g_mailbox.setpoint_ma;
}

} // namespace demo
