#include <cstdint>
#include <expected>

namespace power {

/* Опис структур апаратних регістрів для типобезпечного доступу */
struct PowerControllerRegisters {
    volatile uint32_t cr1;
    volatile uint32_t cr2;
    volatile uint32_t cr3;
    volatile uint32_t cr4;
    volatile uint32_t sr1;
    volatile uint32_t sr2;
};

struct ClockControllerRegisters {
    volatile uint32_t ahb1rstr;
    volatile uint32_t ahb2rstr;
    volatile uint32_t ahb3rstr;
    uint32_t reserved0;
    volatile uint32_t ahb1enr;
    volatile uint32_t ahb2enr;
    volatile uint32_t ahb3enr;
};

/* Прив'язка структур до фізичних адрес адресного простору пам'яті */
inline auto& pwr_regs = *reinterpret_cast<PowerControllerRegisters*>(0x40007000U);
inline auto& rcc_regs = *reinterpret_cast<ClockControllerRegisters*>(0x40021000U);

/* Константи бітових масок конфігурації */
constexpr uint32_t PVM2_MONITOR_ENABLE = 1U << 0;
constexpr uint32_t POWER_SWITCH_ENABLE = 1U << 1;
constexpr uint32_t ISOLATION_DEASSERT  = 1U << 9;
constexpr uint32_t PVM2_VOLTAGE_READY  = 1U << 1;
constexpr uint32_t GPIOG_CLOCK_ENABLE  = 1U << 6;
constexpr uint32_t GPIOG_RESET_ASSERT  = 1U << 6;

enum class DomainError {
    VoltageOutOfRange,
    PowerSwitchTimeout,
    HardwareFault
};

/* RAII-клас для суворого контролю життєвого циклу силового домену */
class Vddio2DomainGuard {
public:
    /* Фабричний метод для безпечного конструювання об'єкта */
    static std::expected<Vddio2DomainGuard, DomainError> acquire(uint32_t timeout_cycles = 100000U) {
        /* 1. Активація схеми моніторингу вхідної напруги шини */
        pwr_regs.cr2 |= PVM2_MONITOR_ENABLE;

        /* 2. Очікування виходу напруги зовнішнього джерела на безпечний рівень */
        while ((pwr_regs.sr2 & PVM2_VOLTAGE_READY) == 0U) {
            if (--timeout_cycles == 0U) {
                pwr_regs.cr2 &= ~PVM2_MONITOR_ENABLE;
                return std::unexpected(DomainError::VoltageOutOfRange);
            }
        }

        /* 3. Комутація силового ключа живлення домену */
        pwr_regs.cr2 |= POWER_SWITCH_ENABLE;

        /* Апаратна пауза на наростання напруги */
        for (volatile uint32_t i = 0; i < 1000U; ++i) {
            asm volatile ("nop");
        }

        /* 4. Зняття апаратної ізоляції сигнальних ліній */
        pwr_regs.cr2 |= ISOLATION_DEASSERT;

        /* 5. Подання тактування на периферійний модуль */
        rcc_regs.ahb2enr |= GPIOG_CLOCK_ENABLE;

        /* 6. Початкове скидання тригерів периферії */
        rcc_regs.ahb2rstr |= GPIOG_RESET_ASSERT;
        rcc_regs.ahb2rstr &= ~GPIOG_RESET_ASSERT;

        return Vddio2DomainGuard{};
    }

    /* Деструктор гарантовано виконує вимкнення в строго зворотному порядку */
    ~Vddio2DomainGuard() noexcept {
        /* 1. Зупинка тактування блоку */
        rcc_regs.ahb2enr &= ~GPIOG_CLOCK_ENABLE;

        /* 2. Активація апаратної ізоляції сигнальних шин */
        pwr_regs.cr2 &= ~ISOLATION_DEASSERT;

        /* 3. Розмикання силового ключа живлення */
        pwr_regs.cr2 &= ~POWER_SWITCH_ENABLE;

        /* 4. Вимкнення компаратора моніторингу */
        pwr_regs.cr2 &= ~PVM2_MONITOR_ENABLE;
    }

    /* Заборона копіювання для запобігання подвійному вимкненню ресурсу */
    Vddio2DomainGuard(const Vddio2DomainGuard&) = delete;
    Vddio2DomainGuard& operator=(const Vddio2DomainGuard&) = delete;

    /* Дозвіл переміщення володіння ресурсом */
    Vddio2DomainGuard(Vddio2DomainGuard&&) noexcept = default;
    Vddio2DomainGuard& operator=(Vddio2DomainGuard&&) noexcept = default;

private:
    /* Приватний конструктор доступний лише через фабричний метод acquire() */
    Vddio2DomainGuard() noexcept = default;
};

} // namespace power
