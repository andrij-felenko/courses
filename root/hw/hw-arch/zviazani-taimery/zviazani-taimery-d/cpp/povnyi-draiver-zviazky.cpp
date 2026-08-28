#include <cstdint>
#include <expected>
#include <span>

namespace hw::timer {

/* Базові адреси периферійних блоків таймерів */
inline constexpr std::uintptr_t tim1_base = 0x40010000U;
inline constexpr std::uintptr_t tim2_base = 0x40000000U;
inline constexpr std::uintptr_t tim3_base = 0x40000400U;

/* Регістрова карта таймера загального призначення */
struct alignas(4) TimerRegisters {
    volatile std::uint32_t cr1;
    volatile std::uint32_t cr2;
    volatile std::uint32_t smcr;
    volatile std::uint32_t dier;
    volatile std::uint32_t sr;
    volatile std::uint32_t egr;
    volatile std::uint32_t ccmr1;
    volatile std::uint32_t ccmr2;
    volatile std::uint32_t ccer;
    volatile std::uint32_t cnt;
    volatile std::uint32_t psc;
    volatile std::uint32_t arr;
    volatile std::uint32_t rcr;
    volatile std::uint32_t ccr1;
    volatile std::uint32_t ccr2;
    volatile std::uint32_t ccr3;
    volatile std::uint32_t ccr4;
    volatile std::uint32_t bdtr;
    volatile std::uint32_t dcr;
    volatile std::uint32_t dmar;
};

/* Типізовані переліки конфігурації тригерної матриці */
enum class MasterTriggerSource : std::uint32_t {
    Reset       = 0x00U,
    EnableCen   = 0x01U,
    UpdateEvent = 0x02U,
    ComparePulse= 0x03U,
    Oc1Ref      = 0x04U,
    Oc2Ref      = 0x05U,
    Oc3Ref      = 0x06U,
    Oc4Ref      = 0x07U
};

enum class TriggerInput : std::uint32_t {
    Itr0        = 0x00U,
    Itr1        = 0x01U,
    Itr2        = 0x02U,
    Itr3        = 0x03U,
    Ti1fEdge    = 0x04U,
    Ti1Filtered = 0x05U,
    Ti2Filtered = 0x06U,
    EtrFiltered = 0x07U
};

enum class SlaveMode : std::uint32_t {
    Disabled       = 0x00U,
    ResetMode      = 0x04U,
    GatedMode      = 0x05U,
    TriggerMode    = 0x06U,
    ExtClockMode1  = 0x07U
};

enum class TimerError : std::uint8_t {
    InvalidPrescaler,
    InvalidPeriod,
    BusClockTooLow
};

/* Клас безпечного інкапсульованого доступу до таймера */
template <std::uintptr_t BaseAddress>
class HardwareTimer {
public:
    [[nodiscard]] static TimerRegisters& regs() noexcept {
        return *reinterpret_cast<TimerRegisters*>(BaseAddress);
    }

    static void enable() noexcept {
        regs().cr1 |= (1U << 0);
    }

    static void disable() noexcept {
        regs().cr1 &= ~(1U << 0);
    }

    static void reset_counter() noexcept {
        regs().cnt = 0;
    }

    static void configure_master(std::uint16_t prescaler, std::uint16_t period,
                                 MasterTriggerSource trgo_src) noexcept {
        disable();
        regs().psc = prescaler;
        regs().arr = period;

        std::uint32_t cr2 = regs().cr2;
        cr2 &= ~(0x07U << 4);
        cr2 |= (static_cast<std::uint32_t>(trgo_src) & 0x07U) << 4;
        regs().cr2 = cr2;

        regs().egr |= (1U << 0); // Оновлення конфігурації (UG)
    }

    static void configure_slave(std::uint16_t prescaler, std::uint16_t period,
                                TriggerInput trgi_input, SlaveMode mode) noexcept {
        disable();
        regs().psc = prescaler;
        regs().arr = period;

        std::uint32_t smcr = regs().smcr;
        smcr &= ~((0x07U << 4) | 0x07U);
        smcr |= (static_cast<std::uint32_t>(trgi_input) & 0x07U) << 4;
        smcr |= (static_cast<std::uint32_t>(mode) & 0x07U);
        regs().smcr = smcr;

        regs().egr |= (1U << 0);
    }
};

/* Апаратний 32-бітний каскадний таймер */
class CascadedTimer32 {
public:
    using Master = HardwareTimer<tim2_base>;
    using Slave  = HardwareTimer<tim3_base>;

    static void init() noexcept {
        // Master (TIM2): рахує молодші 16 біт, генерує TRGO по кожному переповненню
        Master::configure_master(0, 0xFFFFU, MasterTriggerSource::UpdateEvent);

        // Slave (TIM3): інкрементується за фронтом тригера ITR1 (TRGO майстра)
        Slave::configure_slave(0, 0xFFFFU, TriggerInput::Itr1, SlaveMode::ExtClockMode1);

        Master::reset_counter();
        Slave::reset_counter();

        Slave::enable();
        Master::enable();
    }

    [[nodiscard]] static std::uint32_t read_atomic() noexcept {
        std::uint16_t high1{};
        std::uint16_t low{};
        std::uint16_t high2{};

        do {
            high1 = static_cast<std::uint16_t>(Slave::regs().cnt);
            low   = static_cast<std::uint16_t>(Master::regs().cnt);
            high2 = static_cast<std::uint16_t>(Slave::regs().cnt);
        } while (high1 != high2);

        return (static_cast<std::uint32_t>(high1) << 16) | static_cast<std::uint32_t>(low);
    }
};

/* Апаратний прецизійний частотомір */
class HardwareFrequencyMeter {
public:
    using Timebase = HardwareTimer<tim2_base>;
    using Counter  = HardwareTimer<tim3_base>;

    [[nodiscard]] static std::expected<void, TimerError> init(std::uint32_t apb_clock_hz) noexcept {
        if (apb_clock_hz < 10000U) {
            return std::unexpected(TimerError::BusClockTooLow);
        }

        const auto psc = static_cast<std::uint16_t>((apb_clock_hz / 10000U) - 1U);
        constexpr std::uint16_t arr = 9999U; // Вікно рівно 1.000000 с

        Timebase::configure_master(psc, arr, MasterTriggerSource::EnableCen);
        Counter::configure_slave(0, 0xFFFFU, TriggerInput::Itr1, SlaveMode::GatedMode);

        // Активація зовнішнього входу ETR для підрахунку імпульсів
        Counter::regs().smcr |= (1U << 14);

        return {};
    }

    static void start_measurement() noexcept {
        Counter::reset_counter();
        Timebase::reset_counter();
        Timebase::enable();
    }
};

} // namespace hw::timer
