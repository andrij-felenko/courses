#include "mcu/pin.hpp"

#include "stm32f4xx.h"

#include <array>

namespace mcu {
namespace {

constexpr std::array<GPIO_TypeDef*, 5> kPorts{GPIOA, GPIOB, GPIOC, GPIOD, GPIOE};
constexpr std::array<std::uint32_t, 5> kClocks{
    RCC_AHB1ENR_GPIOAEN, RCC_AHB1ENR_GPIOBEN, RCC_AHB1ENR_GPIOCEN,
    RCC_AHB1ENR_GPIODEN, RCC_AHB1ENR_GPIOEEN};

std::size_t s_rejected = 0;
bool s_leased = false;

[[nodiscard]] GPIO_TypeDef* regs(Port port) noexcept
{
    return kPorts[static_cast<std::size_t>(port)];
}

void enable_clock(Port port) noexcept
{
    RCC->AHB1ENR |= kClocks[static_cast<std::size_t>(port)];
    static_cast<void>(RCC->AHB1ENR);   // зворотне читання перед доступом до порту
}

void set_pair(volatile std::uint32_t& reg, std::uint8_t n, std::uint32_t value) noexcept
{
    const std::uint32_t shift = static_cast<std::uint32_t>(n) * 2U;
    std::uint32_t v = reg;
    v &= ~(0x3U << shift);
    v |= (value & 0x3U) << shift;
    reg = v;
}

void set_alternate(GPIO_TypeDef* r, std::uint8_t n, std::uint8_t alt) noexcept
{
    const std::uint32_t idx = static_cast<std::uint32_t>(n) >> 3U;
    const std::uint32_t shift = (static_cast<std::uint32_t>(n) & 0x7U) * 4U;
    std::uint32_t v = r->AFR[idx];
    v &= ~(0xFU << shift);
    v |= static_cast<std::uint32_t>(alt) << shift;
    r->AFR[idx] = v;
}

// Стан ліній SWD після скидання: AF0, SWDIO з підтяжкою вгору, SWCLK — вниз.
constexpr PinConfig kSwdioDefault{Mode::Alternate, Pull::Up, Speed::VeryHigh,
                                  OutputType::PushPull, 0};
constexpr PinConfig kSwclkDefault{Mode::Alternate, Pull::Down, Speed::VeryHigh,
                                  OutputType::PushPull, 0};

}  // namespace

void Pin::apply(Port port, std::uint8_t n, const PinConfig& cfg) noexcept
{
    enable_clock(port);
    GPIO_TypeDef* r = regs(port);

    // Порядок важить: MODER — останнім, інакше вивід на мить видасть на плату
    // голку зі старою альтернативною функцією.
    set_alternate(r, n, cfg.alternate);
    set_pair(r->OSPEEDR, n, static_cast<std::uint32_t>(cfg.speed));
    set_pair(r->PUPDR, n, static_cast<std::uint32_t>(cfg.pull));

    if (cfg.otype == OutputType::OpenDrain) {
        r->OTYPER |= (1U << n);
    } else {
        r->OTYPER &= ~(1U << n);
    }

    set_pair(r->MODER, n, static_cast<std::uint32_t>(cfg.mode));
}

std::expected<Pin, PinError> Pin::configure(Port port, std::uint8_t n,
                                            const PinConfig& cfg) noexcept
{
    if (n > 15) {
        return std::unexpected(PinError::InvalidPin);
    }
    if (!cfg.valid()) {
        return std::unexpected(PinError::InvalidAlternate);
    }
    if (is_swd_pin(port, n) && !s_leased) {
        ++s_rejected;
        return std::unexpected(PinError::SwdPinLocked);
    }

    apply(port, n, cfg);
    return Pin{port, n};
}

void Pin::write(bool level) const noexcept
{
    // BSRR: атомарна установка (молодша половина) і скидання (старша).
    regs(port_)->BSRR = level ? (1U << n_) : (1U << (n_ + 16U));
}

bool Pin::read() const noexcept
{
    return (regs(port_)->IDR & (1U << n_)) != 0U;
}

void Pin::toggle() const noexcept
{
    regs(port_)->ODR ^= (1U << n_);
}

std::expected<SwdPinLease, PinError> SwdPinLease::acquire(std::uint32_t key) noexcept
{
    if (key != kSwdUnlockKey) {
        return std::unexpected(PinError::WrongKey);
    }
    s_leased = true;
    return SwdPinLease{};
}

SwdPinLease::SwdPinLease(SwdPinLease&& other) noexcept : owns_{other.owns_}
{
    other.owns_ = false;
}

SwdPinLease::~SwdPinLease()
{
    if (!owns_) {
        return;
    }
    // Виводи повертаються шині налагодження навіть тоді, коли посеред роботи
    // з ними трапився ранній вихід із функції.
    Pin::apply(Port::A, 13, kSwdioDefault);
    Pin::apply(Port::A, 14, kSwclkDefault);
    s_leased = false;
}

std::expected<Pin, PinError> SwdPinLease::configure(std::uint8_t n,
                                                    const PinConfig& cfg) noexcept
{
    if (!owns_) {
        return std::unexpected(PinError::SwdPinLocked);
    }
    return Pin::configure(Port::A, n, cfg);
}

std::size_t rejected_count() noexcept
{
    return s_rejected;
}

std::string_view to_string(PinError error) noexcept
{
    switch (error) {
        case PinError::InvalidPin:       return "номер виводу поза межами";
        case PinError::InvalidAlternate: return "немає такої альтернативної функції";
        case PinError::SwdPinLocked:     return "вивід належить шині SWD";
        case PinError::WrongKey:         return "хибний ключ оренди";
    }
    return "невідомий стан";
}

}  // namespace mcu
