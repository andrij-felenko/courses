#include "telemetry.hpp"

#include "platform.hpp"

#include <algorithm>
#include <charconv>

namespace diag {
namespace {

// PA2 = USART2_TX, альтернативна функція AF7.
inline constexpr unsigned pin_uart_tx = 2U;
inline constexpr unsigned af_usart2 = 7U;

// APB1 = 42 МГц, ділильник = 42e6 / (16 * 115200) = 22.786:
// мантиса 22, дробова частина round(0.786 * 16) = 13.
inline constexpr std::uint32_t brr_115200 = (22U << 4) | 13U;

// Скільки обертів очікування TXE вважати ознакою мертвого передавача.
// Один символ на 115200 — близько 87 мкс; на 168 МГц це десятки тисяч
// тактів, тож із запасом беремо мільйон.
inline constexpr std::uint32_t tx_spin_limit = 1'000'000U;

[[nodiscard]] bool wait_flag(std::uint32_t flag) noexcept
{
    for (std::uint32_t spins = 0; spins < tx_spin_limit; ++spins) {
        if (stm32::usart2::sr::any(flag)) {
            return true;
        }
    }
    // Передавач не звільняється — кабель від'єднали або периферія збилася.
    // Діагностика не має права підвісити систему, яку вона діагностує.
    return false;
}

} // namespace

LineBuilder& LineBuilder::operator<<(std::string_view text) noexcept
{
    const std::size_t n = std::min(text.size(), room());
    std::copy_n(text.begin(), n, buf_.begin() + static_cast<std::ptrdiff_t>(len_));
    len_ += n;
    truncated_ = truncated_ || n < text.size();
    return *this;
}

LineBuilder& LineBuilder::operator<<(std::uint32_t value) noexcept
{
    char* const first = buf_.data() + len_;
    const auto [ptr, ec] = std::to_chars(first, buf_.data() + buf_.size(), value);
    if (ec != std::errc{}) {
        truncated_ = true;
        return *this;
    }
    len_ = static_cast<std::size_t>(ptr - buf_.data());
    return *this;
}

LineBuilder& LineBuilder::hex(std::uint32_t value) noexcept
{
    *this << std::string_view{"0x"};
    if (room() < 8U) {
        truncated_ = true;
        return *this;
    }

    static constexpr std::string_view digits{"0123456789ABCDEF"};
    for (int shift = 28; shift >= 0; shift -= 4) {
        buf_[len_++] = digits[(value >> shift) & 0xFU];
    }
    return *this;
}

void Telemetry::init() noexcept
{
    using namespace stm32;

    rcc::ahb1enr::set(rcc::gpioa_en);
    rcc::apb1enr::set(rcc::usart2_en);
    hw::dsb();

    gpioa::set_mode(pin_uart_tx, gpioa::Mode::alternate);
    gpioa::set_alternate(pin_uart_tx, af_usart2);

    usart2::brr::write(brr_115200);
    usart2::cr1::write(usart2::ue | usart2::te);
}

void Telemetry::write(std::string_view text) noexcept
{
    for (const char c : text) {
        if (!wait_flag(stm32::usart2::txe)) {
            return;
        }
        stm32::usart2::dr::write(static_cast<std::uint32_t>(static_cast<unsigned char>(c)));
    }
    static_cast<void>(wait_flag(stm32::usart2::tc));
}

void Telemetry::line(std::string_view text) noexcept
{
    write(text);
    write("\r\n");
}

std::string_view Telemetry::render(const CrashReport& report, std::span<char> scratch) noexcept
{
    LineBuilder out{scratch};

    out << "BOOT #" << report.boot_count
        << " cause=" << to_string(report.cause)
        << " flags=";
    out.hex(report.raw_reset_flags);
    out << " faults=" << report.fault_count
        << " safe=" << report.safe_state_entries;

    if (report.panic != PanicReason::none) {
        out << " panic=" << to_string(report.panic) << " pc=";
        out.hex(report.fault.pc);
        out << " lr=";
        out.hex(report.fault.lr);
        out << " sp=";
        out.hex(report.fault.sp);
        out << " cfsr=";
        out.hex(report.fault.cfsr);
        out << " up=" << report.uptime_ms << "ms";
    }

    if (out.truncated()) {
        // Обрізаний рядок телеметрії — теж діагностика: краще чесна
        // позначка, ніж мовчки загублений хвіст із адресою падіння.
        out << "…";
    }

    return out.view();
}

} // namespace diag
