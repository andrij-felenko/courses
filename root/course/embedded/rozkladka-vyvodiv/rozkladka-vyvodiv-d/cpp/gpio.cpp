#include "gpio.hpp"

#include <array>
#include <optional>

namespace mcu::gpio {
namespace {

constexpr std::size_t kPortCount  = 8;       // GPIOA..GPIOH
constexpr std::uintptr_t kStride  = 0x400;   // блоки портів через 1 КБ
constexpr std::uint32_t kLckk     = 1u << 16;

// Виданий струм живе між викликами: друга таблиця мусить бачити першу.
std::array<unsigned, kPortCount> g_port_ma{};
unsigned g_chip_ma = 0;

// Вимкнення переривань як ресурс: послідовність LCKR не можна переривати.
class CriticalSection {
public:
    CriticalSection() noexcept : primask_{__get_PRIMASK()} { __disable_irq(); }
    ~CriticalSection() { __set_PRIMASK(primask_); }

    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;

private:
    std::uint32_t primask_;
};

[[nodiscard]] std::optional<std::size_t> port_index(const GPIO_TypeDef* port) noexcept
{
    if (port == nullptr) {
        return std::nullopt;
    }

    const auto base  = reinterpret_cast<std::uintptr_t>(port);
    const auto first = static_cast<std::uintptr_t>(GPIOA_BASE);
    if (base < first) {
        return std::nullopt;
    }

    const auto offset = base - first;
    if (offset % kStride != 0) {
        return std::nullopt;
    }

    const auto index = offset / kStride;
    if (index >= kPortCount) {
        return std::nullopt;
    }
    return static_cast<std::size_t>(index);
}

// Системні й резервні ніжки впізнаємо за адресою, а не за словом у таблиці:
// саме помилковий запис у таблиці ми й ловимо.
[[nodiscard]] bool is_swd(const Pin& p) noexcept
{
    return p.port == GPIOA && (p.number == 13 || p.number == 14);
}

[[nodiscard]] bool is_backup(const Pin& p) noexcept
{
    return p.port == GPIOC && p.number >= 13 && p.number <= 15;
}

[[nodiscard]] std::unexpected<Fault> fault(Reason reason, std::string_view signal,
                                           unsigned value = 0, unsigned limit = 0,
                                           std::string_view rival = {}) noexcept
{
    return std::unexpected(Fault{reason, signal, rival, value, limit});
}

[[nodiscard]] std::expected<void, Fault> validate(const PinPlan& p) noexcept
{
    if (!port_index(p.pin.port)) {
        return fault(Reason::UnknownPort, p.signal);
    }
    if (p.pin.number > 15) {
        return fault(Reason::PinOutOfRange, p.signal, p.pin.number, 15);
    }

    // 1. Шина налагодження: дозволено лише те, чим вона є, — AF0.
    if (is_swd(p.pin)) {
        if (p.ec != ElectricalClass::System) {
            return fault(Reason::ClassMismatch, p.signal,
                         static_cast<unsigned>(p.ec),
                         static_cast<unsigned>(ElectricalClass::System), "PA13/PA14 = SWD");
        }
        if (p.mode != Mode::Alternate || p.af != 0) {
            return fault(Reason::DebugPin, p.signal, static_cast<unsigned>(p.mode),
                         static_cast<unsigned>(Mode::Alternate), "SWDIO/SWCLK");
        }
    } else if (p.ec == ElectricalClass::System) {
        return fault(Reason::ClassMismatch, p.signal,
                     static_cast<unsigned>(ElectricalClass::System));
    }

    // 2. Домен резервного живлення: слабкі ключі, повільні фронти, без AF.
    if (is_backup(p.pin)) {
        if (p.ec != ElectricalClass::Backup) {
            return fault(Reason::ClassMismatch, p.signal, static_cast<unsigned>(p.ec),
                         static_cast<unsigned>(ElectricalClass::Backup), "PC13..PC15 = Backup");
        }
        if (p.mode == Mode::Alternate) {
            return fault(Reason::BackupAlternate, p.signal, p.af);
        }
        if (p.speed != Speed::Low) {
            return fault(Reason::BackupSpeed, p.signal, static_cast<unsigned>(p.speed),
                         static_cast<unsigned>(Speed::Low));
        }
        if (p.load_ma > Limits::backup_ma) {
            return fault(Reason::BackupCurrent, p.signal, p.load_ma, Limits::backup_ma);
        }
    } else if (p.ec == ElectricalClass::Backup) {
        return fault(Reason::ClassMismatch, p.signal,
                     static_cast<unsigned>(ElectricalClass::Backup));
    }

    // 3. Аналоговий тракт існує лише там, де кремній завів його на АЦП.
    if (p.mode == Mode::Analog && p.ec != ElectricalClass::Tta) {
        return fault(Reason::AnalogOnDigital, p.signal, static_cast<unsigned>(p.ec),
                     static_cast<unsigned>(ElectricalClass::Tta));
    }

    // 4. Номер альтернативної функції.
    if (p.mode == Mode::Alternate) {
        if (p.af > 15) {
            return fault(Reason::AfOutOfRange, p.signal, p.af, 15);
        }
    } else if (p.af != 0) {
        // AF поза режимом Alternate нічого не робить, зате ховає помилку копіювання.
        return fault(Reason::AfUnused, p.signal, p.af, 0);
    }

    // 5. Крутизна фронту: звичайний вихід не має права на Very High,
    //    а все, що реально тягне струм, — лише Low.
    if (p.mode == Mode::Output && p.speed == Speed::VeryHigh) {
        return fault(Reason::SlewTooFast, p.signal, static_cast<unsigned>(p.speed),
                     static_cast<unsigned>(Speed::High));
    }
    if (p.load_ma > 0 && p.speed != Speed::Low) {
        return fault(Reason::SlewTooFast, p.signal, static_cast<unsigned>(p.speed),
                     static_cast<unsigned>(Speed::Low));
    }

    // 6. Струм окремої ніжки (домен RTC уже перевірено суворішою межею).
    if (!is_backup(p.pin) && p.load_ma > Limits::pin_ma) {
        return fault(Reason::PinCurrent, p.signal, p.load_ma, Limits::pin_ma);
    }

    return {};
}

[[nodiscard]] std::expected<std::array<unsigned, kPortCount>, Fault>
weigh(std::span<const PinPlan> layout) noexcept
{
    std::array<unsigned, kPortCount> added{};

    for (std::size_t i = 0; i < layout.size(); ++i) {
        const PinPlan& p = layout[i];

        if (auto ok = validate(p); !ok) {
            return std::unexpected(ok.error());
        }

        // Головний конфлікт теми: дві функції на одній фізичній ніжці.
        // Мультиплексор пропустить лише останній запис — тихо.
        for (std::size_t j = 0; j < i; ++j) {
            if (layout[j].pin == p.pin) {
                return fault(Reason::Duplicate, p.signal, p.pin.number, 0, layout[j].signal);
            }
        }

        added[*port_index(p.pin.port)] += p.load_ma;
    }

    unsigned chip = g_chip_ma;
    for (std::size_t i = 0; i < kPortCount; ++i) {
        const unsigned total = g_port_ma[i] + added[i];
        if (total > Limits::port_ma) {
            std::string_view culprit{};
            for (const PinPlan& p : layout) {
                if (port_index(p.pin.port) == i) {
                    culprit = p.signal;
                    break;
                }
            }
            return fault(Reason::PortCurrent, culprit, total, Limits::port_ma);
        }
        chip += added[i];
    }

    if (chip > Limits::chip_ma) {
        return fault(Reason::ChipCurrent, layout.front().signal, chip, Limits::chip_ma);
    }

    return added;
}

void enable_clock(std::size_t index) noexcept
{
    RCC->AHB1ENR |= (1u << index);
    // Читання назад: шина AHB застосовує запис із затримкою в такт.
    [[maybe_unused]] const std::uint32_t sync = RCC->AHB1ENR;
}

void write(const PinPlan& p) noexcept
{
    GPIO_TypeDef* g = p.pin.port;
    const auto two  = static_cast<std::uint32_t>(p.pin.number) * 2u;
    const auto one  = static_cast<std::uint32_t>(p.pin.number);

    // Порядок навмисний: усе, крім MODER, ставимо ДО перемикання режиму,
    // інакше ніжка на кілька тактів дістається блоку зі старим AF.
    if (p.mode == Mode::Alternate) {
        const std::uint32_t idx   = one >> 3;         // AFRL або AFRH
        const std::uint32_t shift = (one & 7u) * 4u;  // 4 біти на ніжку
        g->AFR[idx] = (g->AFR[idx] & ~(0xFu << shift)) | (static_cast<std::uint32_t>(p.af) << shift);
    }

    if (p.drive == Drive::OpenDrain) {
        g->OTYPER |= (1u << one);
    } else {
        g->OTYPER &= ~(1u << one);
    }

    g->OSPEEDR = (g->OSPEEDR & ~(0x3u << two)) | (static_cast<std::uint32_t>(p.speed) << two);
    g->PUPDR   = (g->PUPDR   & ~(0x3u << two)) | (static_cast<std::uint32_t>(p.pull)  << two);
    g->MODER   = (g->MODER   & ~(0x3u << two)) | (static_cast<std::uint32_t>(p.mode)  << two);
}

// Після скидання PA15 і PB4 підтягнуті вгору, PB3 — вниз: залишки JTAG.
// Віддаємо ніжки під звичайний GPIO — вхід без підтяжки, AF0 очищено.
void release_to_gpio(GPIO_TypeDef* port, std::uint8_t pin) noexcept
{
    const auto two   = static_cast<std::uint32_t>(pin) * 2u;
    const auto idx   = static_cast<std::uint32_t>(pin) >> 3;
    const auto shift = (static_cast<std::uint32_t>(pin) & 7u) * 4u;

    port->MODER    &= ~(0x3u << two);   // 0b00 = вхід
    port->PUPDR    &= ~(0x3u << two);
    port->OSPEEDR  &= ~(0x3u << two);
    port->AFR[idx] &= ~(0xFu << shift);
}

}  // namespace

std::expected<void, Fault> apply(std::span<const PinPlan> layout) noexcept
{
    if (layout.empty()) {
        return {};
    }

    const auto added = weigh(layout);
    if (!added) {
        return std::unexpected(added.error());
    }

    // Жодного запису в регістр вище цього рядка.
    for (const PinPlan& p : layout) {
        enable_clock(*port_index(p.pin.port));
    }
    for (const PinPlan& p : layout) {
        write(p);
    }

    for (std::size_t i = 0; i < kPortCount; ++i) {
        g_port_ma[i] += (*added)[i];
        g_chip_ma    += (*added)[i];
    }

    return {};
}

std::expected<void, Fault> secure_debug_port() noexcept
{
    RCC->AHB1ENR |= (1u << 0) | (1u << 1);   // GPIOA, GPIOB
    [[maybe_unused]] const std::uint32_t sync = RCC->AHB1ENR;

    release_to_gpio(GPIOA, 15);  // JTDI
    release_to_gpio(GPIOB, 3);   // JTDO/SWO — трасування втрачаємо свідомо
    release_to_gpio(GPIOB, 4);   // NJTRST

    if ((GPIOA->LCKR & kLckk) != 0) {
        return {};  // замок уже стоїть і тримається до скидання
    }

    constexpr std::uint32_t swd = (1u << 13) | (1u << 14);
    std::uint32_t confirm = 0;
    {
        // Послідовність із довідника: 1+біти, 0+біти, 1+біти, потім читання.
        const CriticalSection guard;

        GPIOA->LCKR = kLckk | swd;
        GPIOA->LCKR = swd;
        GPIOA->LCKR = kLckk | swd;
        [[maybe_unused]] const std::uint32_t first_read = GPIOA->LCKR;
        confirm = GPIOA->LCKR;
    }

    if ((confirm & kLckk) == 0) {
        return fault(Reason::LockFailed, "SWDIO/SWCLK", confirm, kLckk);
    }

    // Тепер MODER/AFR цих двох ніжок апаратно нерухомі: навіть чужа
    // бібліотечна ініціалізація порту вже не відріже програматор.
    return {};
}

std::string_view describe(Reason reason) noexcept
{
    using enum Reason;
    switch (reason) {
    case UnknownPort:     return "невідомий порт GPIO";
    case PinOutOfRange:   return "номер ніжки поза 0..15";
    case DebugPin:        return "спроба забрати ніжку SWD";
    case ClassMismatch:   return "клас не збігається з таблицею виводів";
    case AnalogOnDigital: return "аналоговий режим на цифровій ніжці";
    case AfOutOfRange:    return "номер альтернативної функції > 15";
    case AfUnused:        return "AF заданий поза режимом Alternate";
    case SlewTooFast:     return "надлишкова крутизна фронту";
    case BackupAlternate: return "альтернативна функція в домені RTC";
    case BackupSpeed:     return "домен RTC не тримає такої швидкості";
    case BackupCurrent:   return "понад 3 мА на ніжці домену RTC";
    case PinCurrent:      return "перевищено струм однієї ніжки";
    case PortCurrent:     return "перевищено струм порту";
    case ChipCurrent:     return "перевищено струм кристала";
    case Duplicate:       return "дві функції на одній ніжці";
    case LockFailed:      return "замок LCKR не підтвердився";
    }
    return "невідомий стан";
}

unsigned port_budget_ma(const GPIO_TypeDef* port) noexcept
{
    const auto index = port_index(port);
    return index ? g_port_ma[*index] : 0u;
}

unsigned chip_budget_ma() noexcept
{
    return g_chip_ma;
}

}  // namespace mcu::gpio
