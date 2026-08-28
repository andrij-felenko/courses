/* cpp */
#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <expected>
#include <algorithm>
#include <cstring>

namespace dh::security {

constexpr std::size_t MaxPayloadSize = 256;
constexpr std::size_t MaxSensorIdLen = 32;
constexpr std::size_t HmacLen = 32;
constexpr float MinAllowedTemp = -40.0f;
constexpr float MaxAllowedTemp = 85.0f;
constexpr std::uint32_t MaxPacketsPerSec = 10;

enum class GatewayError {
    BufferTooSmall,
    InvalidHmac,
    ReplayAttack,
    OutOfBounds,
    RateLimited
};

struct SensorPacket {
    std::array<std::uint8_t, MaxSensorIdLen> sensor_id{};
    std::size_t sensor_id_len{0};
    std::uint64_t sequence_num{0};
    float temperature{0.0f};
};

class SensorSession {
public:
    explicit SensorSession(std::span<const std::uint8_t, 32> secret_key) 
        : key_(secret_key) {}

    [[nodiscard]] std::uint64_t last_sequence() const noexcept { return last_sequence_; }
    [[nodiscard]] std::span<const std::uint8_t, 32> key() const noexcept { return key_; }

    void update_sequence(std::uint64_t new_seq) noexcept { last_sequence_ = new_seq; }

    [[nodiscard]] bool check_rate_limit(std::uint64_t current_time_sec) noexcept {
        if (current_time_sec == last_window_sec_) {
            if (packet_count_current_sec_ >= MaxPacketsPerSec) {
                return false;
            }
            packet_count_current_sec_++;
        } else {
            last_window_sec_ = current_time_sec;
            packet_count_current_sec_ = 1;
        }
        return true;
    }

private:
    std::uint64_t last_sequence_{0};
    std::uint32_t packet_count_current_sec_{0};
    std::uint64_t last_window_sec_{0};
    std::span<const std::uint8_t, 32> key_;
};

// Порівняння за сталий час у сучасній C++20 реалізації
[[nodiscard]] inline bool constant_time_compare(
    std::span<const std::uint8_t> a, 
    std::span<const std::uint8_t> b) noexcept 
{
    if (a.size() != b.size()) return false;
    std::uint8_t result = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

[[nodiscard]] inline bool verify_hmac(
    std::span<const std::uint8_t> payload,
    std::span<const std::uint8_t, 32> key,
    std::span<const std::uint8_t, HmacLen> expected_hmac) noexcept 
{
    std::array<std::uint8_t, HmacLen> computed_hmac{};
    computed_hmac.fill(0xAB); // Симуляція обчислення HMAC
    (void)payload; (void)key;
    return constant_time_compare(computed_hmac, expected_hmac);
}

[[nodiscard]] std::expected<SensorPacket, GatewayError> process_sensor_packet(
    std::span<const std::uint8_t> raw_bytes,
    SensorSession& session,
    std::uint64_t current_time_sec) noexcept
{
    // 1. Валідація розмірів через std::span
    constexpr std::size_t min_header_size = sizeof(std::uint32_t) + 1 + sizeof(std::uint64_t) + sizeof(float) + HmacLen;
    if (raw_bytes.size() < min_header_size || raw_bytes.size() > MaxPayloadSize) {
        return std::unexpected(GatewayError::BufferTooSmall);
    }

    std::uint32_t id_len = 0;
    std::memcpy(&id_len, raw_bytes.data(), sizeof(std::uint32_t));
    if (id_len == 0 || id_len > MaxSensorIdLen) {
        return std::unexpected(GatewayError::BufferTooSmall);
    }

    const std::size_t total_expected = sizeof(std::uint32_t) + id_len + sizeof(std::uint64_t) + sizeof(float) + HmacLen;
    if (raw_bytes.size() < total_expected) {
        return std::unexpected(GatewayError::BufferTooSmall);
    }

    SensorPacket pkt;
    pkt.sensor_id_len = id_len;
    std::copy_n(raw_bytes.begin() + sizeof(std::uint32_t), id_len, pkt.sensor_id.begin());

    std::size_t offset = sizeof(std::uint32_t) + id_len;
    std::memcpy(&pkt.sequence_num, raw_bytes.data() + offset, sizeof(std::uint64_t));
    offset += sizeof(std::uint64_t);

    std::memcpy(&pkt.temperature, raw_bytes.data() + offset, sizeof(float));
    offset += sizeof(float);

    auto hmac_span = raw_bytes.subspan(offset, HmacLen);
    std::array<std::uint8_t, HmacLen> expected_hmac_arr{};
    std::copy_n(hmac_span.begin(), HmacLen, expected_hmac_arr.begin());

    // 2. Захист від повторів (Replay Protection)
    if (pkt.sequence_num <= session.last_sequence()) {
        return std::unexpected(GatewayError::ReplayAttack);
    }

    // 3. Криптографічна повна медіація з порівнянням за сталий час
    auto payload_span = raw_bytes.first(offset);
    if (!verify_hmac(payload_span, session.key(), expected_hmac_arr)) {
        return std::unexpected(GatewayError::InvalidHmac);
    }

    // 4. Rate Limiting на рівні шлюзу
    if (!session.check_rate_limit(current_time_sec)) {
        return std::unexpected(GatewayError::RateLimited);
    }

    // 5. Інваріанти домену
    if (pkt.temperature < MinAllowedTemp || pkt.temperature > MaxAllowedTemp) {
        return std::unexpected(GatewayError::OutOfBounds);
    }

    // Атомарне оновлення лічильника сесії
    session.update_sequence(pkt.sequence_num);
    return pkt;
}

} // namespace dh::security
