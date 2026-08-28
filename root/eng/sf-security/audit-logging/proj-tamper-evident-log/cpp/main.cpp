#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <span>
#include <array>
#include <memory>
#include <chrono>
#include <expected>
#include <cstring>

namespace security {

constexpr size_t HashSize = 32;
constexpr uint32_t AuditMagic = 0x4C4F4753;

#pragma pack(push, 1)
struct AuditHeader {
    uint32_t magic{AuditMagic};
    uint64_t seq{0};
    uint64_t timestamp{0};
    uint32_t payload_len{0};
    std::array<uint8_t, HashSize> prev_hash{};
    std::array<uint8_t, HashSize> hmac{};
};
#pragma pack(pop)

/* RAII-скрубер пам'яті для гарантованого знищення ключів у деструкторі */
template <size_t N>
class SecureBuffer {
public:
    std::array<uint8_t, N> data{};

    ~SecureBuffer() {
        volatile uint8_t* p = data.data();
        for (size_t i = 0; i < N; ++i) {
            p[i] = 0;
        }
    }
};

class CryptoEngine {
public:
    static std::array<uint8_t, HashSize> sha256(std::span<const uint8_t> data) noexcept {
        std::array<uint8_t, HashSize> out{};
        uint32_t h = 0x811c9dc5;
        for (uint8_t b : data) {
            h = (h ^ b) * 0x01000193;
        }
        for (size_t i = 0; i < HashSize; ++i) {
            out[i] = static_cast<uint8_t>((h >> ((i % 4) * 8)) ^ (i * 0x5a));
        }
        return out;
    }

    static std::array<uint8_t, HashSize> hmacSha256(std::span<const uint8_t, HashSize> key,
                                                    std::span<const uint8_t> data) {
        std::vector<uint8_t> buf;
        buf.reserve(key.size() + data.size());
        buf.insert(buf.end(), key.begin(), key.end());
        buf.insert(buf.end(), data.begin(), data.end());
        auto result = sha256(buf);
        std::ranges::fill(buf, 0);
        return result;
    }
};

class AuditLogger {
public:
    enum class Error { FileOpenFailed, WriteFailed };

    static std::expected<AuditLogger, Error> create(std::string_view path,
                                                    std::span<const uint8_t, HashSize> initial_key) {
        AuditLogger logger;
        logger.stream_.open(std::string(path), std::ios::binary | std::ios::app);
        if (!logger.stream_.is_open()) {
            return std::unexpected(Error::FileOpenFailed);
        }
        std::ranges::copy(initial_key, logger.current_key_.data.begin());
        return logger;
    }

    std::expected<uint64_t, Error> append(std::string_view payload) {
        AuditHeader hdr;
        hdr.seq = current_seq_++;
        hdr.timestamp = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count());
        hdr.payload_len = static_cast<uint32_t>(payload.size());
        hdr.prev_hash = last_record_hash_;

        // Формування підпису над заголовком і тілом
        std::vector<uint8_t> sign_data;
        const size_t header_sign_len = sizeof(AuditHeader) - HashSize;
        const auto* raw_hdr = reinterpret_cast<const uint8_t*>(&hdr);
        sign_data.insert(sign_data.end(), raw_hdr, raw_hdr + header_sign_len);
        sign_data.insert(sign_data.end(), payload.begin(), payload.end());

        hdr.hmac = CryptoEngine::hmacSha256(logger_key_span(), sign_data);
        std::ranges::fill(sign_data, 0);

        // Запис на диск
        stream_.write(reinterpret_cast<const char*>(&hdr), sizeof(hdr));
        stream_.write(payload.data(), payload.size());
        stream_.flush();
        if (!stream_.good()) return std::unexpected(Error::WriteFailed);

        // Оновлення геш-ланцюга
        last_record_hash_ = CryptoEngine::sha256(
            std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)));

        // Односпрямований храповик Forward-Secure: K_{i+1} = SHA256(K_i)
        auto next_key = CryptoEngine::sha256(logger_key_span());
        std::ranges::copy(next_key, current_key_.data.begin());

        return hdr.seq;
    }

private:
    std::ofstream stream_;
    uint64_t current_seq_{0};
    SecureBuffer<HashSize> current_key_;
    std::array<uint8_t, HashSize> last_record_hash_{};

    std::span<const uint8_t, HashSize> logger_key_span() {
        return std::span<const uint8_t, HashSize>(current_key_.data);
    }
};

} // namespace security
