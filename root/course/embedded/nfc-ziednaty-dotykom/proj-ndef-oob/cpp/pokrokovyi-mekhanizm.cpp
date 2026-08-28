#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>
#include <algorithm>

namespace embedded::nfc {

enum class Tnf : uint8_t {
    Empty      = 0x00,
    WellKnown  = 0x01,
    MimeMedia  = 0x02,
    AbsoluteUri= 0x03,
    External   = 0x04
};

enum class Status {
    Ok,
    BufferOverflow,
    InvalidParam
};

namespace flags {
    inline constexpr uint8_t MessageBegin = 0x80;
    inline constexpr uint8_t MessageEnd   = 0x40;
    inline constexpr uint8_t ShortRecord  = 0x10;
}

namespace ble_ad {
    inline constexpr uint8_t Flags       = 0x01;
    inline constexpr uint8_t Name        = 0x09;
    inline constexpr uint8_t SecurityTk  = 0x10;
    inline constexpr uint8_t LeAddress   = 0x1B;
    inline constexpr uint8_t LeRole      = 0x1C;
}

class NdefMessageBuilder {
public:
    explicit constexpr NdefMessageBuilder(std::span<uint8_t> storage) noexcept
        : buffer_(storage), length_(0), record_count_(0) {}

    [[nodiscard]] size_t size() const noexcept { return length_; }
    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return buffer_.subspan(0, length_);
    }

    Status addUri(uint8_t prefixCode, std::string_view uri, bool isLast) noexcept {
        const size_t payloadLen = 1 + uri.size();
        constexpr size_t recordOverhead = 4; // Header, TypeLen, PayloadLen, Type('U')

        if (length_ + recordOverhead + payloadLen > buffer_.size()) {
            return Status::BufferOverflow;
        }

        uint8_t header = flags::ShortRecord | static_cast<uint8_t>(Tnf::WellKnown);
        if (record_count_ == 0) header |= flags::MessageBegin;
        if (isLast) header |= flags::MessageEnd;

        auto* ptr = buffer_.data() + length_;
        *ptr++ = header;
        *ptr++ = 0x01; // Type Length = 1
        *ptr++ = static_cast<uint8_t>(payloadLen);
        *ptr++ = 'U';
        *ptr++ = prefixCode;
        std::copy_n(uri.data(), uri.size(), ptr);

        length_ += (recordOverhead + payloadLen);
        record_count_++;
        return Status::Ok;
    }

    Status addBleOob(std::span<const uint8_t, 6> macLe, 
                     uint8_t addrType, 
                     std::span<const uint8_t, 16> tk, 
                     std::string_view deviceName, 
                     bool isLast) noexcept {
        constexpr std::string_view mimeType = "application/vnd.bluetooth.ep.oob";
        const size_t nameLen = deviceName.size();
        
        // 3B (Flags) + 9B (LE Addr) + 3B (LE Role) + 18B (TK) + (Name)
        const size_t payloadLen = 3 + 9 + 3 + 18 + (nameLen > 0 ? (2 + nameLen) : 0);
        const size_t recordOverhead = 3 + mimeType.size();

        if (length_ + recordOverhead + payloadLen > buffer_.size()) {
            return Status::BufferOverflow;
        }

        uint8_t header = flags::ShortRecord | static_cast<uint8_t>(Tnf::MimeMedia);
        if (record_count_ == 0) header |= flags::MessageBegin;
        if (isLast) header |= flags::MessageEnd;

        auto* ptr = buffer_.data() + length_;
        *ptr++ = header;
        *ptr++ = static_cast<uint8_t>(mimeType.size());
        *ptr++ = static_cast<uint8_t>(payloadLen);
        ptr = std::copy_n(mimeType.data(), mimeType.size(), ptr);

        // 1. Flags
        *ptr++ = 0x02;
        *ptr++ = ble_ad::Flags;
        *ptr++ = 0x06;

        // 2. LE Device Address
        *ptr++ = 0x08;
        *ptr++ = ble_ad::LeAddress;
        ptr = std::copy_n(macLe.data(), 6, ptr);
        *ptr++ = addrType;

        // 3. LE Role
        *ptr++ = 0x02;
        *ptr++ = ble_ad::LeRole;
        *ptr++ = 0x00; // Peripheral only

        // 4. Security Manager TK
        *ptr++ = 0x11;
        *ptr++ = ble_ad::SecurityTk;
        ptr = std::copy_n(tk.data(), 16, ptr);

        // 5. Complete Local Name
        if (nameLen > 0) {
            *ptr++ = static_cast<uint8_t>(1 + nameLen);
            *ptr++ = ble_ad::Name;
            std::copy_n(deviceName.data(), nameLen, ptr);
        }

        length_ += (recordOverhead + payloadLen);
        record_count_++;
        return Status::Ok;
    }

private:
    std::span<uint8_t> buffer_;
    size_t length_;
    size_t record_count_;
};

} // namespace embedded::nfc
