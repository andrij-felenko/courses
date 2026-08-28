#include <cstdint>
#include <array>
#include <span>

namespace LowPower {

/* Регістровий опис портів введення-виведення */
struct GpioRegisters {
    volatile std::uint32_t moder;
    volatile std::uint32_t otyper;
    volatile std::uint32_t ospeedr;
    volatile std::uint32_t pupdr;
    volatile std::uint32_t idr;
    volatile std::uint32_t odr;
    volatile std::uint32_t bsrr;
    volatile std::uint32_t lckr;
    volatile std::uint32_t afr[2];
    volatile std::uint32_t brr;
};

inline auto& gpio_a = *reinterpret_cast<GpioRegisters*>(0x48000000UL);
inline auto& gpio_b = *reinterpret_cast<GpioRegisters*>(0x48000400UL);
inline auto& gpio_c = *reinterpret_cast<GpioRegisters*>(0x48000800UL);
inline auto& dbgmcu_cr = *reinterpret_cast<volatile std::uint32_t*>(0xE0042004UL);

enum class PinMode : std::uint32_t {
    Input  = 0b00,
    Output = 0b01,
    AltFn  = 0b10,
    Analog = 0b11
};

enum class PullMode : std::uint32_t {
    Floating = 0b00,
    PullUp   = 0b01,
    PullDown = 0b10
};

struct PortBackup {
    std::uint32_t moder{0xFFFFFFFFUL};
    std::uint32_t pupdr{0x00000000UL};
};

class SleepManager {
public:
    constexpr SleepManager() noexcept = default;

    /* RAII-сторож низькоспоживаного стану */
    class SleepScopeGuard {
    public:
        explicit SleepScopeGuard(SleepManager& manager) noexcept : manager_(manager) {
            manager_.enter_sleep_configuration();
        }

        ~SleepScopeGuard() noexcept {
            manager_.restore_active_configuration();
        }

        SleepScopeGuard(const SleepScopeGuard&) = delete;
        SleepScopeGuard& operator=(const SleepScopeGuard&) = delete;

    private:
        SleepManager& manager_;
    };

    [[nodiscard]] SleepScopeGuard guard() noexcept {
        return SleepScopeGuard{*this};
    }

    void set_load_switch(bool enabled) noexcept {
        constexpr std::uint32_t switch_pin_mask = (1U << 12);
        if (enabled) {
            gpio_b.bsrr = (switch_pin_mask << 16U); /* Reset pin -> Active Low ON */
        } else {
            gpio_b.bsrr = switch_pin_mask;          /* Set pin -> OFF */
        }
    }

    void enter_sleep_configuration() noexcept {
        backup_[0] = { .moder = gpio_a.moder, .pupdr = gpio_a.pupdr };
        backup_[1] = { .moder = gpio_b.moder, .pupdr = gpio_b.pupdr };
        backup_[2] = { .moder = gpio_c.moder, .pupdr = gpio_c.pupdr };

        /* 1. Ізоляція шин даних */
        gpio_a.odr &= ~((1U << 2) | (1U << 3) | (1U << 5) | (1U << 7));

        /* 2. Знеструмлення периферії */
        set_load_switch(false);

        /* 3. Переведення пінів у чистий Analog, зберігаючи пін пробудження PA0 */
        gpio_a.moder = 0xFFFFFFFCUL | (backup_[0].moder & 0x03UL);
        gpio_a.pupdr = 0x00000000UL | (backup_[0].pupdr & 0x03UL);

        /* Зберігаємо вихідний пін ключа живлення PB12 */
        constexpr std::uint32_t pb12_mask = (0b11U << (12 * 2));
        gpio_b.moder = (~pb12_mask) | (backup_[1].moder & pb12_mask);
        gpio_b.pupdr = 0x00000000UL;

        /* Порт C повністю переводиться в Analog */
        gpio_c.moder = 0xFFFFFFFFUL;
        gpio_c.pupdr = 0x00000000UL;

        /* 4. Вимкнення блоку налагодження ядра */
        dbgmcu_cr = 0x00000000UL;
    }

    void restore_active_configuration() noexcept {
        gpio_a.moder = backup_[0].moder;
        gpio_a.pupdr = backup_[0].pupdr;

        gpio_b.moder = backup_[1].moder;
        gpio_b.pupdr = backup_[1].pupdr;

        gpio_c.moder = backup_[2].moder;
        gpio_c.pupdr = backup_[2].pupdr;

        set_load_switch(true);
    }

private:
    std::array<PortBackup, 3> backup_{};
};

} // namespace LowPower
