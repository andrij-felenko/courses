#include <iostream>
#include <span>
#include <string_view>
#include <string>
#include <array>
#include <optional>
#include <format>
#include <cstdint>

enum class MacAddressType {
    UniversalUnicast,
    UniversalMulticast,
    LocalUnicast,
    LocalMulticast
};

struct ParsedMac {
    std::array<uint8_t, 6> raw{};
    uint32_t oui24{0};
    MacAddressType type{MacAddressType::UniversalUnicast};

    [[nodiscard]] bool isUniversalUnicast() const noexcept {
        return type == MacAddressType::UniversalUnicast;
    }

    [[nodiscard]] std::array<uint8_t, 8> toEui64() const noexcept {
        return {raw[0], raw[1], raw[2], 0xFF, 0xFE, raw[3], raw[4], raw[5]};
    }

    [[nodiscard]] std::string format() const {
        return std::format("{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}",
                           raw[0], raw[1], raw[2], raw[3], raw[4], raw[5]);
    }
};

struct ParsedUsbDevice {
    uint16_t bcdUsb{0};
    uint8_t  deviceClass{0};
    uint8_t  deviceSubclass{0};
    uint8_t  deviceProtocol{0};
    uint8_t  maxPacketSize0{0};
    uint16_t vendorId{0};
    uint16_t productId{0};
    uint16_t bcdDevice{0};

    [[nodiscard]] std::string toUdevRule(std::string_view symlinkName) const {
        return std::format("SUBSYSTEM==\"usb\", ATTR{{idVendor}}==\"{:04x}\", "
                           "ATTR{{idProduct}}==\"{:04x}\", MODE=\"0666\", SYMLINK+=\"{}\"",
                           vendorId, productId, symlinkName);
    }
};

class HardwareIdentifierValidator {
private:
    static constexpr int hexCharToNibble(char c) noexcept {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'a' && c <= 'f') return c - 'a' + 10;
        if (c >= 'A' && c <= 'F') return c - 'A' + 10;
        return -1;
    }

public:
    static std::optional<ParsedMac> parseMac(std::string_view str) noexcept {
        ParsedMac result{};
        int byteIdx = 0;
        int nibbleCnt = 0;
        uint8_t curByte = 0;

        for (char c : str) {
            if (c == ':' || c == '-') {
                if (nibbleCnt != 2) return std::nullopt;
                result.raw[byteIdx++] = curByte;
                curByte = 0;
                nibbleCnt = 0;
                if (byteIdx > 6) return std::nullopt;
                continue;
            }
            int nibble = hexCharToNibble(c);
            if (nibble < 0) return std::nullopt;

            curByte = static_cast<uint8_t>((curByte << 4) | static_cast<uint8_t>(nibble));
            nibbleCnt++;
            if (nibbleCnt == 2) {
                if (byteIdx >= 6) return std::nullopt;
                result.raw[byteIdx++] = curByte;
                curByte = 0;
                nibbleCnt = 0;
            }
        }

        if (byteIdx != 6 || nibbleCnt != 0) return std::nullopt;

        result.oui24 = (static_cast<uint32_t>(result.raw[0]) << 16) |
                       (static_cast<uint32_t>(result.raw[1]) << 8)  |
                       static_cast<uint32_t>(result.raw[2]);

        bool isGroup = (result.raw[0] & 0x01) != 0;
        bool isLocal = (result.raw[0] & 0x02) != 0;

        if (!isGroup && !isLocal) result.type = MacAddressType::UniversalUnicast;
        else if (isGroup && !isLocal) result.type = MacAddressType::UniversalMulticast;
        else if (!isGroup && isLocal) result.type = MacAddressType::LocalUnicast;
        else result.type = MacAddressType::LocalMulticast;

        return result;
    }

    static std::optional<ParsedUsbDevice> parseUsbDescriptor(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 18) return std::nullopt;
        if (buffer[0] != 18 || buffer[1] != 0x01) return std::nullopt;

        ParsedUsbDevice dev{};
        dev.bcdUsb = static_cast<uint16_t>(buffer[2] | (static_cast<uint16_t>(buffer[3]) << 8));
        dev.deviceClass = buffer[4];
        dev.deviceSubclass = buffer[5];
        dev.deviceProtocol = buffer[6];
        dev.maxPacketSize0 = buffer[7];
        dev.vendorId = static_cast<uint16_t>(buffer[8] | (static_cast<uint16_t>(buffer[9]) << 8));
        dev.productId = static_cast<uint16_t>(buffer[10] | (static_cast<uint16_t>(buffer[11]) << 8));
        dev.bcdDevice = static_cast<uint16_t>(buffer[12] | (static_cast<uint16_t>(buffer[13]) << 8));

        if (dev.vendorId == 0x0000 || dev.vendorId == 0xFFFF) {
            return std::nullopt;
        }

        return dev;
    }
};
