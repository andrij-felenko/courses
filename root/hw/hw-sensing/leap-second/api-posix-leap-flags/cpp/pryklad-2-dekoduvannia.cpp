#include <iostream>
#include <cstdint>
#include <string_view>

namespace ntp_protocol {

enum class LeapWarning : uint8_t {
    NoWarning = 0,
    AddSecond = 1,
    DeleteSecond = 2,
    AlarmUnsynchronized = 3
};

[[nodiscard]] constexpr LeapWarning extract_leap_warning(uint8_t ntp_first_byte) noexcept {
    return static_cast<LeapWarning>((ntp_first_byte >> 6) & 0x03);
}

[[nodiscard]] constexpr std::string_view format_leap_status(LeapWarning warning) noexcept {
    switch (warning) {
        case LeapWarning::NoWarning:
            return "LI 00: Корекція відсутня (штатний хід годинника)";
        case LeapWarning::AddSecond:
            return "LI 01: Попередження: додавання +1 секунди (23:59:60 UTC)";
        case LeapWarning::DeleteSecond:
            return "LI 10: Попередження: вилучення 1 секунди (23:59:58 -> 00:00:00)";
        case LeapWarning::AlarmUnsynchronized:
            return "LI 11: Аварійний стан: годинник сервера розсинхронізовано";
    }
    return "Невідомий код стану";
}

} // namespace ntp_protocol
