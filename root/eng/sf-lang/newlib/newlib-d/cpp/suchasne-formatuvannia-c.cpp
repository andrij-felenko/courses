#include <array>
#include <string_view>
#include <span>
#include <cstdio>
#include <cstdint>

// Ідіоматичне форматування C++ без використання динамічної купи
namespace logger {

template <std::size_t N>
class StackBuffer {
public:
    constexpr auto data() noexcept -> char* { return buffer_.data(); }
    constexpr auto size() const noexcept -> std::size_t { return N; }
    constexpr auto span() noexcept -> std::span<char> { return {buffer_.data(), N}; }

private:
    std::array<char, N> buffer_{};
};

void log_telemetry_cpp(std::uint32_t timestamp, float current, float voltage) noexcept {
    StackBuffer<64> log_buf;
    
    // snprintf залишається найекономнішим за обсягом Flash у Newlib-nano
    const int len = std::snprintf(
        log_buf.data(), log_buf.size(),
        "[%lu ms] I=%.2f A, U=%.2f V\r\n",
        static_cast<unsigned long>(timestamp),
        static_cast<double>(current),
        static_cast<double>(voltage)
    );

    if (len > 0) {
        std::fwrite(log_buf.data(), 1, static_cast<std::size_t>(len), stdout);
    }
}

} // namespace logger
