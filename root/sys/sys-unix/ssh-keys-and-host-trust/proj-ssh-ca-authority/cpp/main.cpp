#include <iostream>
#include <string_view>
#include <vector>
#include <span>
#include <cstdint>
#include <chrono>
#include <format>
#include <expected>
#include <bit>

enum class ParseError {
    UnexpectedEndOfBuffer,
    InvalidCertificateFormat,
};

class WireReader {
public:
    explicit WireReader(std::span<const uint8_t> buffer) : buffer_(buffer), offset_(0) {}

    std::expected<uint32_t, ParseError> read_uint32() {
        if (offset_ + 4 > buffer_.size()) return std::unexpected(ParseError::UnexpectedEndOfBuffer);
        uint32_t val = (static_cast<uint32_t>(buffer_[offset_]) << 24) |
                       (static_cast<uint32_t>(buffer_[offset_ + 1]) << 16) |
                       (static_cast<uint32_t>(buffer_[offset_ + 2]) << 8) |
                       static_cast<uint32_t>(buffer_[offset_ + 3]);
        offset_ += 4;
        return val;
    }

    std::expected<uint64_t, ParseError> read_uint64() {
        auto high = read_uint32();
        if (!high) return std::unexpected(high.error());
        auto low = read_uint32();
        if (!low) return std::unexpected(low.error());
        return (static_cast<uint64_t>(*high) << 32) | static_cast<uint64_t>(*low);
    }

    std::expected<std::string_view, ParseError> read_string() {
        auto len = read_uint32();
        if (!len) return std::unexpected(len.error());
        if (offset_ + *len > buffer_.size()) return std::unexpected(ParseError::UnexpectedEndOfBuffer);
        
        std::string_view view(reinterpret_cast<const char*>(buffer_.data() + offset_), *len);
        offset_ += *len;
        return view;
    }

    std::expected<std::span<const uint8_t>, ParseError> read_blob() {
        auto len = read_uint32();
        if (!len) return std::unexpected(len.error());
        if (offset_ + *len > buffer_.size()) return std::unexpected(ParseError::UnexpectedEndOfBuffer);

        std::span<const uint8_t> sub(buffer_.data() + offset_, *len);
        offset_ += *len;
        return sub;
    }

    [[nodiscard]] bool empty() const noexcept { return offset_ >= buffer_.size(); }

private:
    std::span<const uint8_t> buffer_;
    size_t offset_;
};

struct SshCertificate {
    std::string_view key_type;
    uint64_t serial{};
    uint32_t cert_type{};
    std::string_view key_id;
    std::vector<std::string_view> principals;
    std::chrono::system_clock::time_point valid_after;
    std::chrono::system_clock::time_point valid_before;
};

std::expected<SshCertificate, ParseError> parse_ssh_certificate(std::span<const uint8_t> raw_bytes) {
    WireReader reader(raw_bytes);
    SshCertificate cert;

    auto key_type = reader.read_string();
    if (!key_type) return std::unexpected(key_type.error());
    cert.key_type = *key_type;

    if (!reader.read_blob()) return std::unexpected(ParseError::UnexpectedEndOfBuffer); // nonce
    if (!reader.read_blob()) return std::unexpected(ParseError::UnexpectedEndOfBuffer); // pubkey

    auto serial = reader.read_uint64();
    if (!serial) return std::unexpected(serial.error());
    cert.serial = *serial;

    auto ctype = reader.read_uint32();
    if (!ctype) return std::unexpected(ctype.error());
    cert.cert_type = *ctype;

    auto kid = reader.read_string();
    if (!kid) return std::unexpected(kid.error());
    cert.key_id = *kid;

    auto princ_blob = reader.read_blob();
    if (!princ_blob) return std::unexpected(princ_blob.error());

    WireReader princ_reader(*princ_blob);
    while (!princ_reader.empty()) {
        auto p = princ_reader.read_string();
        if (!p) break;
        cert.principals.push_back(*p);
    }

    auto after = reader.read_uint64();
    auto before = reader.read_uint64();
    if (!after || !before) return std::unexpected(ParseError::UnexpectedEndOfBuffer);

    cert.valid_after = std::chrono::system_clock::time_point(std::chrono::seconds(*after));
    cert.valid_before = std::chrono::system_clock::time_point(std::chrono::seconds(*before));

    return cert;
}

void print_certificate_info(const SshCertificate& cert) {
    std::cout << "Тип сертифіката: " << cert.key_type << "\n"
              << "Серійний номер: " << cert.serial << "\n"
              << "Призначення: " << (cert.cert_type == 1 ? "USER" : "HOST") << "\n"
              << "Key ID: " << cert.key_id << "\n"
              << "Principals:\n";
    for (const auto& p : cert.principals) {
        std::cout << "  - " << p << "\n";
    }
}
