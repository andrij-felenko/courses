// Ручне керування маскою в C++ дає ті самі витоки, що й у C: кожен новий
// шлях виходу треба памʼятати. Нижче в цьому ж модулі — та сама логіка на
// вартовому, де про вихід дбає компілятор.
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "demo/demos.hpp"
#include "mcu/cpu.hpp"
#include "mcu/critical_section.hpp"

namespace {

// Останній розібраний відлік: його пише фон, а читає обробник ШІМ.
volatile std::uint16_t g_last_sample{0};

constexpr std::byte kFrameMark{0xA5};
constexpr std::size_t kFrameSize = 5U;

// Кадр давача: 0xA5 | довжина | старший байт | молодший байт | XOR-сума.
// Спільної памʼяті розбір не чіпає, тож синхронізації тут немає.
std::expected<std::uint16_t, demo::FrameError> decode(std::span<const std::byte> frame) noexcept
{
    if (frame.size() < kFrameSize) {
        return std::unexpected(demo::FrameError::BadArgument);
    }
    if (frame[0] != kFrameMark || std::to_integer<std::size_t>(frame[1]) != 2U) {
        return std::unexpected(demo::FrameError::BadMark);
    }

    std::byte checksum{0};
    for (const std::byte value : frame.first(4U)) {
        checksum ^= value;
    }
    if (checksum != frame[4]) {
        return std::unexpected(demo::FrameError::BadChecksum);
    }

    return static_cast<std::uint16_t>((std::to_integer<std::uint16_t>(frame[2]) << 8) |
                                      std::to_integer<std::uint16_t>(frame[3]));
}

} // namespace

namespace demo {

// ТАК РОБИТИ НЕ МОЖНА: два ранні виходи лишають PRIMASK одиницею назавжди.
std::expected<void, FrameError> handle_frame_manual(std::span<const std::byte> frame) noexcept
{
    const std::uint32_t saved_primask = mcu::cpu::primask();
    mcu::cpu::disable_irq();
    mcu::cpu::barrier();

    const auto decoded = decode(frame);
    if (!decoded) {
        // Витік: плата мовчить, поки її не перезавантажить сторожовий таймер,
        // а в журналі лишається сама тільки «завада на лінії давача».
        return std::unexpected(decoded.error());
    }
    g_last_sample = *decoded;

    mcu::cpu::barrier();
    mcu::cpu::set_primask(saved_primask); // сюди доходить лише щасливий шлях
    return {};
}

// Те саме на вартовому: скільки б виходів не додали далі, маска повертається.
std::expected<void, FrameError> handle_frame(std::span<const std::byte> frame) noexcept
{
    const mcu::CriticalSectionGuard lock; // вхід у секцію

    const auto decoded = decode(frame);
    if (!decoded) {
        return std::unexpected(decoded.error()); // деструктор відновить маску тут
    }
    g_last_sample = *decoded;
    return {}; // і тут
}

std::uint16_t last_sample() noexcept { return g_last_sample; }

} // namespace demo
