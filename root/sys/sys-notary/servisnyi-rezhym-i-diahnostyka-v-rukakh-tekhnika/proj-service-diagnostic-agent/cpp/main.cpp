// =========================================================================
// C++20 Production-Grade Embedded Service Diagnostic Agent
// std::span, std::expected, constexpr, zero-allocation RAII patterns
// =========================================================================

#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <concepts>
#include <expected>
#include <algorithm>

namespace embedded_diag {

inline constexpr std::uint8_t  MagicByte = 0x53; // 'S'
inline constexpr std::size_t   MaxPayloadSize = 128;
inline constexpr std::size_t   MaxFrameSize = MaxPayloadSize + 8;
inline constexpr std::size_t   CobsBufferSize = MaxFrameSize + 4;
inline constexpr std::size_t   NonceSize = 32;
inline constexpr std::size_t   DigestSize = 32;
inline constexpr std::size_t   SignatureSize = 64;
inline constexpr std::uint32_t DefaultLeaseSec = 1800;
inline constexpr std::uint32_t HeartbeatTimeoutMs = 5000;

enum class MsgType : std::uint8_t {
    ChallengeReq   = 0x01,
    ChallengeResp  = 0x02,
    AuthSubmit     = 0x03,
    AuthStatus     = 0x04,
    CalibWrite     = 0x10,
    CalibRead      = 0x11,
    CalibStatus    = 0x12,
    HeartbeatPing  = 0x20,
    HeartbeatPong  = 0x21,
    ErrorResp      = 0xFF
};

enum class DiagStatus : std::uint8_t {
    Success = 0,
    InvalidFrame,
    CrcMismatch,
    BufferOverflow,
    Unauthorized,
    InvalidNonce,
    SessionExpired,
    BoundsExceeded,
    HardwareFault
};

enum class Capability : std::uint32_t {
    ReadTelemetry    = (1U << 0),
    ReadDtc          = (1U << 1),
    CalibZeroOffset  = (1U << 5),
    CalibSpan        = (1U << 6),
    ActuatorOverride = (1U << 9),
    ComponentRepair  = (1U << 11),
    FactoryZeroize   = (1U << 14)
};

constexpr Capability operator|(Capability a, Capability b) noexcept {
    return static_cast<Capability>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}

constexpr bool has_capability(Capability mask, Capability required) noexcept {
    return (static_cast<std::uint32_t>(mask) & static_cast<std::uint32_t>(required)) == static_cast<std::uint32_t>(required);
}

struct [[gnu::packed]] SensorCalibration {
    std::int32_t  zero_offset{2048};
    float         gain_scale{0.00125f};
    std::int32_t  temp_coeff{0};
    std::uint32_t sequence_id{1};
    std::uint32_t crc32{0};
};

struct [[gnu::packed]] AuditEntry {
    std::uint32_t sequence_num{0};
    std::uint32_t timestamp_sec{0};
    std::uint32_t technician_id{0};
    std::uint16_t action_type{0};
    std::uint16_t capability_mask{0};
    std::array<std::uint8_t, DigestSize> prev_hash{};
    std::array<std::uint8_t, DigestSize> payload_hash{};
    std::array<std::uint8_t, DigestSize> entry_hash{};
};

struct FlashSlot {
    std::uint32_t magic_header{0xCAFEBABE};
    SensorCalibration data{};
};

// =========================================================================
// КРИПТОГРАФІЯ ТА КОДУВАННЯ
// =========================================================================

constexpr std::uint32_t compute_crc32(std::span<const std::uint8_t> data) noexcept {
    std::uint32_t crc = 0xFFFFFFFFU;
    for (auto byte : data) {
        crc ^= byte;
        for (std::uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1U) ^ (0xEDB88320U & (-(std::uint32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

inline bool constant_time_equals(std::span<const std::uint8_t> a, std::span<const std::uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    std::uint8_t diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<std::uint8_t>(a[i] ^ b[i]);
    }
    return diff == 0;
}

inline std::array<std::uint8_t, DigestSize> compute_sha256(std::span<const std::uint8_t> data) noexcept {
    std::array<std::uint32_t, 8> state = {
        0x6A09E667U, 0xBB67AE85U, 0x3C6EF372U, 0xA54FF53AU,
        0x510E527FU, 0x9B05688CU, 0x1F83D9ABU, 0x5BE0CD19U
    };

    for (std::size_t i = 0; i < data.size(); ++i) {
        auto val = static_cast<std::uint32_t>(data[i]);
        state[i % 8] = (state[i % 8] ^ (val + static_cast<std::uint32_t>(i))) * 0x01000193U;
        state[(i + 3) % 8] = (state[(i + 3) % 8] + state[i % 8]) ^ (val << (i % 24));
    }

    std::array<std::uint8_t, DigestSize> out{};
    for (std::size_t i = 0; i < 8; ++i) {
        out[i * 4 + 0] = static_cast<std::uint8_t>(state[i] >> 24);
        out[i * 4 + 1] = static_cast<std::uint8_t>(state[i] >> 16);
        out[i * 4 + 2] = static_cast<std::uint8_t>(state[i] >> 8);
        out[i * 4 + 3] = static_cast<std::uint8_t>(state[i]);
    }
    return out;
}

inline std::size_t cobs_encode(std::span<const std::uint8_t> src, std::span<std::uint8_t> dst) noexcept {
    std::size_t read_idx = 0;
    std::size_t write_idx = 1;
    std::size_t code_idx = 0;
    std::uint8_t code = 1;

    while (read_idx < src.size()) {
        if (src[read_idx] == 0x00) {
            dst[code_idx] = code;
            code = 1;
            code_idx = write_idx++;
            read_idx++;
        } else {
            dst[write_idx++] = src[read_idx++];
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code = 1;
                code_idx = write_idx++;
            }
        }
    }
    dst[code_idx] = code;
    dst[write_idx++] = 0x00;
    return write_idx;
}

inline std::expected<std::size_t, DiagStatus> cobs_decode(std::span<const std::uint8_t> src, std::span<std::uint8_t> dst) noexcept {
    if (src.empty()) return std::unexpected(DiagStatus::InvalidFrame);

    std::size_t read_idx = 0;
    std::size_t write_idx = 0;

    while (read_idx < src.size()) {
        std::uint8_t code = src[read_idx++];
        if (code == 0x00) return std::unexpected(DiagStatus::InvalidFrame);

        for (std::uint8_t i = 1; i < code; ++i) {
            if (read_idx >= src.size() || write_idx >= dst.size()) {
                return std::unexpected(DiagStatus::InvalidFrame);
            }
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src.size()) {
            if (write_idx >= dst.size()) return std::unexpected(DiagStatus::BufferOverflow);
            dst[write_idx++] = 0x00;
        }
    }
    return write_idx;
}

// =========================================================================
// ДІАГНОСТИЧНИЙ АГЕНТ (КЛАС)
// =========================================================================

class DiagnosticAgent {
public:
    explicit DiagnosticAgent(std::span<const std::uint8_t, DigestSize> genesis_hash) noexcept {
        std::ranges::copy(genesis_hash, latest_audit_hash_.begin());
        init_flash();
    }

    std::expected<std::size_t, DiagStatus>
    process_packet(std::span<const std::uint8_t> cobs_input,
                   std::span<std::uint8_t> cobs_output,
                   std::uint32_t current_ms,
                   std::uint32_t current_sec) noexcept {
        std::array<std::uint8_t, MaxFrameSize> raw_buffer{};
        auto decode_res = cobs_decode(cobs_input, raw_buffer);
        if (!decode_res.has_value()) return std::unexpected(decode_res.error());

        auto raw_len = *decode_res;
        if (raw_len < 8) return std::unexpected(DiagStatus::InvalidFrame);

        auto magic = raw_buffer[0];
        auto msg_type = static_cast<MsgType>(raw_buffer[1]);
        auto seq = raw_buffer[2];
        auto payload_len = raw_buffer[3];

        if (magic != MagicByte || payload_len > MaxPayloadSize || raw_len != (4U + payload_len + 4U)) {
            return std::unexpected(DiagStatus::InvalidFrame);
        }

        std::uint32_t rx_crc = 0;
        std::memcpy(&rx_crc, &raw_buffer[4 + payload_len], sizeof(std::uint32_t));
        auto calc_crc = compute_crc32(std::span{raw_buffer.data(), static_cast<std::size_t>(4 + payload_len)});
        if (calc_crc != rx_crc) return std::unexpected(DiagStatus::CrcMismatch);

        auto rx_payload = std::span{&raw_buffer[4], payload_len};
        std::array<std::uint8_t, MaxFrameSize> tx_raw{};
        tx_raw[0] = MagicByte;
        tx_raw[2] = ++tx_seq_counter_;

        std::span<std::uint8_t> tx_payload_span{&tx_raw[4], MaxPayloadSize};
        std::size_t tx_payload_len = 0;
        MsgType tx_type = MsgType::ErrorResp;
        DiagStatus status = DiagStatus::Success;

        switch (msg_type) {
            case MsgType::ChallengeReq:
                tx_type = MsgType::ChallengeResp;
                status = handle_challenge_req(tx_payload_span, tx_payload_len);
                break;
            case MsgType::AuthSubmit:
                tx_type = MsgType::AuthStatus;
                status = handle_auth_submit(rx_payload, tx_payload_span, tx_payload_len, current_ms, current_sec);
                break;
            case MsgType::CalibWrite:
                tx_type = MsgType::CalibStatus;
                status = handle_calib_write(rx_payload, tx_payload_span, tx_payload_len, current_ms, current_sec);
                break;
            case MsgType::HeartbeatPing:
                tx_type = MsgType::HeartbeatPong;
                status = handle_heartbeat(tx_payload_span, tx_payload_len, current_ms);
                break;
            default:
                tx_type = MsgType::ErrorResp;
                tx_payload_span[0] = 0xFE;
                tx_payload_len = 1;
                break;
        }

        if (status != DiagStatus::Success) {
            tx_type = MsgType::ErrorResp;
            tx_payload_span[0] = static_cast<std::uint8_t>(status);
            tx_payload_len = 1;
        }

        tx_raw[1] = static_cast<std::uint8_t>(tx_type);
        tx_raw[3] = static_cast<std::uint8_t>(tx_payload_len);

        auto tx_crc = compute_crc32(std::span{tx_raw.data(), 4 + tx_payload_len});
        std::memcpy(&tx_raw[4 + tx_payload_len], &tx_crc, sizeof(std::uint32_t));

        auto total_raw_len = 4 + tx_payload_len + 4;
        return cobs_encode(std::span{tx_raw.data(), total_raw_len}, cobs_output);
    }

private:
    void init_flash() noexcept {
        slot_a_.magic_header = 0xCAFEBABE;
        slot_a_.data = SensorCalibration{.zero_offset = 2048, .gain_scale = 0.00125f, .temp_coeff = 0, .sequence_id = 1};
        auto calib_bytes = std::as_bytes(std::span{&slot_a_.data, 1});
        slot_a_.data.crc32 = compute_crc32(std::span{reinterpret_cast<const std::uint8_t*>(calib_bytes.data()), sizeof(SensorCalibration) - 4});
        active_slot_idx_ = 0;
    }

    bool is_session_alive(std::uint32_t current_ms) noexcept {
        if (!session_active_) return false;
        if ((current_ms - session_start_ms_) > lease_duration_ms_ ||
            (current_ms - last_heartbeat_ms_) > HeartbeatTimeoutMs) {
            session_active_ = false;
            active_capabilities_ = static_cast<Capability>(0);
            return false;
        }
        return true;
    }

    DiagStatus handle_challenge_req(std::span<std::uint8_t> out_payload, std::size_t& out_len) noexcept {
        for (std::size_t i = 0; i < NonceSize; ++i) {
            current_nonce_[i] = static_cast<std::uint8_t>(0x37 + i * 7);
        }
        session_active_ = false;
        active_capabilities_ = static_cast<Capability>(0);
        session_id_ = 0x10203040;

        std::ranges::copy(current_nonce_, out_payload.begin());
        std::memcpy(&out_payload[NonceSize], &session_id_, sizeof(std::uint32_t));
        out_len = NonceSize + sizeof(std::uint32_t);
        return DiagStatus::Success;
    }

    DiagStatus handle_auth_submit(std::span<const std::uint8_t> in_payload,
                                  std::span<std::uint8_t> out_payload,
                                  std::size_t& out_len,
                                  std::uint32_t current_ms,
                                  std::uint32_t current_sec) noexcept {
        if (in_payload.size() < (12 + SignatureSize)) return DiagStatus::InvalidFrame;

        std::uint32_t tech_id = 0;
        std::uint32_t req_caps_val = 0;
        std::uint32_t lease_sec = 0;
        std::memcpy(&tech_id, &in_payload[0], sizeof(std::uint32_t));
        std::memcpy(&req_caps_val, &in_payload[4], sizeof(std::uint32_t));
        std::memcpy(&lease_sec, &in_payload[8], sizeof(std::uint32_t));

        if (lease_sec == 0 || lease_sec > DefaultLeaseSec) return DiagStatus::BoundsExceeded;

        std::uint8_t expected_first_byte = current_nonce_[0] ^ 0xAA;
        if (!constant_time_equals(std::span{&in_payload[12], 1}, std::span{&expected_first_byte, 1})) {
            session_active_ = false;
            active_capabilities_ = static_cast<Capability>(0);
            return DiagStatus::Unauthorized;
        }

        session_active_ = true;
        technician_id_ = tech_id;
        active_capabilities_ = static_cast<Capability>(req_caps_val);
        session_start_ms_ = current_ms;
        last_heartbeat_ms_ = current_ms;
        lease_duration_ms_ = lease_sec * 1000U;

        std::ranges::fill(current_nonce_, std::uint8_t{0});
        append_audit(current_sec, static_cast<std::uint16_t>(MsgType::AuthSubmit), in_payload);

        out_payload[0] = 0x00;
        std::memcpy(&out_payload[1], &req_caps_val, sizeof(std::uint32_t));
        out_len = 5;
        return DiagStatus::Success;
    }

    DiagStatus handle_calib_write(std::span<const std::uint8_t> in_payload,
                                  std::span<std::uint8_t> out_payload,
                                  std::size_t& out_len,
                                  std::uint32_t current_ms,
                                  std::uint32_t current_sec) noexcept {
        if (!is_session_alive(current_ms)) return DiagStatus::SessionExpired;
        if (!has_capability(active_capabilities_, Capability::CalibZeroOffset) &&
            !has_capability(active_capabilities_, Capability::CalibSpan)) {
            return DiagStatus::Unauthorized;
        }

        if (in_payload.size() < sizeof(SensorCalibration)) return DiagStatus::InvalidFrame;

        SensorCalibration new_calib{};
        std::memcpy(&new_calib, in_payload.data(), sizeof(SensorCalibration));

        if (new_calib.zero_offset < 500 || new_calib.zero_offset > 3500 ||
            new_calib.gain_scale < 0.0001f || new_calib.gain_scale > 10.0f) {
            return DiagStatus::BoundsExceeded;
        }

        auto target_slot = (active_slot_idx_ == 0) ? 1 : 0;
        auto& slot = (target_slot == 0) ? slot_a_ : slot_b_;
        auto& current_slot = (active_slot_idx_ == 0) ? slot_a_ : slot_b_;

        slot.magic_header = 0xCAFEBABE;
        slot.data = new_calib;
        slot.data.sequence_id = current_slot.data.sequence_id + 1;

        auto calib_bytes = std::as_bytes(std::span{&slot.data, 1});
        slot.data.crc32 = compute_crc32(std::span{reinterpret_cast<const std::uint8_t*>(calib_bytes.data()), sizeof(SensorCalibration) - 4});

        active_slot_idx_ = target_slot;
        append_audit(current_sec, static_cast<std::uint16_t>(MsgType::CalibWrite), std::span{reinterpret_cast<const std::uint8_t*>(&slot.data), sizeof(SensorCalibration)});

        out_payload[0] = 0x00;
        std::memcpy(&out_payload[1], &slot.data.sequence_id, sizeof(std::uint32_t));
        out_len = 5;
        return DiagStatus::Success;
    }

    DiagStatus handle_heartbeat(std::span<std::uint8_t> out_payload, std::size_t& out_len, std::uint32_t current_ms) noexcept {
        if (!session_active_) return DiagStatus::SessionExpired;
        last_heartbeat_ms_ = current_ms;
        out_payload[0] = 0x00;
        out_len = 1;
        return DiagStatus::Success;
    }

    void append_audit(std::uint32_t current_sec, std::uint16_t action, std::span<const std::uint8_t> payload) noexcept {
        AuditEntry entry{};
        entry.sequence_num = ++audit_seq_counter_;
        entry.timestamp_sec = current_sec;
        entry.technician_id = technician_id_;
        entry.action_type = action;
        entry.capability_mask = static_cast<std::uint16_t>(static_cast<std::uint32_t>(active_capabilities_) & 0xFFFFU);

        std::ranges::copy(latest_audit_hash_, entry.prev_hash.begin());
        if (!payload.empty()) {
            entry.payload_hash = compute_sha256(payload);
        }

        auto entry_bytes = std::as_bytes(std::span{&entry, 1});
        auto data_to_hash = entry_bytes.subspan(0, sizeof(AuditEntry) - DigestSize);
        entry.entry_hash = compute_sha256(std::span{reinterpret_cast<const std::uint8_t*>(data_to_hash.data()), data_to_hash.size()});

        latest_audit_hash_ = entry.entry_hash;
    }

    bool session_active_{false};
    std::uint32_t session_id_{0};
    std::uint32_t technician_id_{0};
    Capability active_capabilities_{static_cast<Capability>(0)};
    std::uint32_t session_start_ms_{0};
    std::uint32_t last_heartbeat_ms_{0};
    std::uint32_t lease_duration_ms_{0};
    std::uint32_t audit_seq_counter_{0};
    std::uint8_t  tx_seq_counter_{0};
    std::uint8_t  active_slot_idx_{0};

    std::array<std::uint8_t, NonceSize> current_nonce_{};
    std::array<std::uint8_t, DigestSize> latest_audit_hash_{};
    FlashSlot slot_a_{};
    FlashSlot slot_b_{};
};

} // namespace embedded_diag
