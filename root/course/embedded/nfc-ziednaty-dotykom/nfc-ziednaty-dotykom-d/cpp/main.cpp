#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>
#include <algorithm>

namespace embedded::nfc {

enum class Tnf : uint8_t {
    WellKnown = 0x01,
    MimeMedia = 0x02
};

namespace flag {
    inline constexpr uint8_t Mb = 0x80;
    inline constexpr uint8_t Me = 0x40;
    inline constexpr uint8_t Sr = 0x10;
}

class NdefStreamBuilder {
public:
    explicit constexpr NdefStreamBuilder(std::span<uint8_t> buffer) noexcept
        : buf_(buffer), offset_(0), count_(0) {}

    [[nodiscard]] size_t length() const noexcept { return offset_; }
    [[nodiscard]] std::span<const uint8_t> payload() const noexcept {
        return buf_.subspan(0, offset_);
    }

    bool appendUri(uint8_t prefixCode, std::string_view url, bool isLast) noexcept {
        const size_t payloadLen = 1 + url.size();
        const size_t totalLen = 4 + payloadLen;
        
        if (offset_ + totalLen > buf_.size()) return false;

        uint8_t header = flag::Sr | static_cast<uint8_t>(Tnf::WellKnown);
        if (count_ == 0) header |= flag::Mb;
        if (isLast) header |= flag::Me;

        buf_[offset_++] = header;
        buf_[offset_++] = 0x01; // Type Length = 1
        buf_[offset_++] = static_cast<uint8_t>(payloadLen);
        buf_[offset_++] = 'U';
        buf_[offset_++] = prefixCode;
        std::copy(url.begin(), url.end(), buf_.begin() + offset_);
        offset_ += url.size();

        count_++;
        return true;
    }

    bool appendBleOob(std::span<const uint8_t, 6> macLe, 
                     std::span<const uint8_t, 16> tk, 
                     bool isLast) noexcept {
        constexpr std::string_view mime = "application/vnd.bluetooth.ep.oob";
        constexpr size_t payloadLen = 3 + 9 + 18; // Flags (3B) + Addr (9B) + TK (18B)
        const size_t totalLen = 3 + mime.size() + payloadLen;

        if (offset_ + totalLen > buf_.size()) return false;

        uint8_t header = flag::Sr | static_cast<uint8_t>(Tnf::MimeMedia);
        if (count_ == 0) header |= flag::Mb;
        if (isLast) header |= flag::Me;

        buf_[offset_++] = header;
        buf_[offset_++] = static_cast<uint8_t>(mime.size());
        buf_[offset_++] = static_cast<uint8_t>(payloadLen);
        std::copy(mime.begin(), mime.end(), buf_.begin() + offset_);
        offset_ += mime.size();

        // 1. Flags AD
        buf_[offset_++] = 0x02;
        buf_[offset_++] = 0x01;
        buf_[offset_++] = 0x06;

        // 2. LE Device Address AD
        buf_[offset_++] = 0x08;
        buf_[offset_++] = 0x1B;
        std::copy(macLe.begin(), macLe.end(), buf_.begin() + offset_);
        offset_ += 6;
        buf_[offset_++] = 0x00; // Public

        // 3. TK AD
        buf_[offset_++] = 0x11;
        buf_[offset_++] = 0x10;
        std::copy(tk.begin(), tk.end(), buf_.begin() + offset_);
        offset_ += 16;

        count_++;
        return true;
    }

private:
    std::span<uint8_t> buf_;
    size_t offset_;
    size_t count_;
};

} // namespace embedded::nfc
