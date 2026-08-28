#include <string_view>
#include <optional>
#include <array>
#include <cstdint>
#include <cctype>

struct DeviceSerialNumber {
    std::array<char, 3> prefix{};
    uint8_t year{0};
    uint8_t week{0};
    uint16_t modelCode{0};
    uint16_t sequence{0};
    uint8_t checksum{0};
};

class SerialNumberValidator {
public:
    static constexpr size_t kLength = 14;

    static constexpr bool ValidateLuhn(std::string_view digits) noexcept {
        int sum = 0;
        bool alternate = false;

        for (auto it = digits.rbegin(); it != digits.rend(); ++it) {
            if (!std::isdigit(static_cast<unsigned char>(*it))) {
                return false;
            }
            int n = *it - '0';
            if (alternate) {
                n *= 2;
                if (n > 9) {
                    n = (n % 10) + 1;
                }
            }
            sum += n;
            alternate = !alternate;
        }
        return (sum % 10 == 0);
    }

    static std::optional<DeviceSerialNumber> Parse(std::string_view raw) noexcept {
        if (raw.size() != kLength) {
            return std::nullopt;
        }

        if (!std::isupper(static_cast<unsigned char>(raw[0])) ||
            !std::isupper(static_cast<unsigned char>(raw[1]))) {
            return std::nullopt;
        }

        // Перевірка контрольної суми Луна для позицій 2..13
        if (!ValidateLuhn(raw.substr(2))) {
            return std::nullopt;
        }

        DeviceSerialNumber sn{};
        sn.prefix[0] = raw[0];
        sn.prefix[1] = raw[1];
        sn.prefix[2] = '\0';

        sn.year = static_cast<uint8_t>((raw[2] - '0') * 10 + (raw[3] - '0'));
        sn.week = static_cast<uint8_t>((raw[4] - '0') * 10 + (raw[5] - '0'));
        sn.modelCode = static_cast<uint16_t>((raw[6] - '0') * 100 + 
                                             (raw[7] - '0') * 10 + 
                                             (raw[8] - '0'));
        sn.sequence = static_cast<uint16_t>((raw[9] - '0') * 1000 + 
                                            (raw[10] - '0') * 100 + 
                                            (raw[11] - '0') * 10 + 
                                            (raw[12] - '0'));
        sn.checksum = static_cast<uint8_t>(raw[13] - '0');

        if (sn.week < 1 || sn.week > 53) {
            return std::nullopt;
        }
        return sn;
    }
};
