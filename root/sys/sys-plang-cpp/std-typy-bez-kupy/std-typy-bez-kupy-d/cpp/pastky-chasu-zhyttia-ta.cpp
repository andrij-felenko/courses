#include <string_view>
#include <charconv>
#include <optional>

struct CsqResponse {
    int signal_strength{0};
    int bit_error_rate{0};
};

[[nodiscard]] std::optional<CsqResponse> parse_csq_cpp(std::string_view response) noexcept {
    // Вхід: "+CSQ: 24,99\r\nOK" — рядок не змінюється, може бути у Flash (.rodata)
    constexpr std::string_view PREFIX = "+CSQ: ";
    auto prefix_pos = response.find(PREFIX);
    if (prefix_pos == std::string_view::npos) {
        return std::nullopt;
    }

    response.remove_prefix(prefix_pos + PREFIX.size());

    CsqResponse result{};
    auto res1 = std::from_chars(response.data(), response.data() + response.size(), result.signal_strength);
    if (res1.ec != std::errc{}) return std::nullopt;

    response.remove_prefix(res1.ptr - response.data());
    if (response.empty() || response.front() != ',') return std::nullopt;
    response.remove_prefix(1); // пропускаємо кому

    auto res2 = std::from_chars(response.data(), response.data() + response.size(), result.bit_error_rate);
    if (res2.ec != std::errc{}) return std::nullopt;

    return result;
}
