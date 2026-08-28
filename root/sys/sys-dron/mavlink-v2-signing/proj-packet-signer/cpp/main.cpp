#include <array>
#include <span>
#include <vector>
#include <chrono>
#include <cstdint>
#include <algorithm>
#include <optional>

class MavlinkPacketSigner {
public:
    static constexpr uint8_t  kStxV2 = 0xFD;
    static constexpr uint8_t  kFlagSigned = 0x01;
    static constexpr size_t   kTrailerLen = 13;
    static constexpr size_t   kMaxStreams = 16;
    using KeyType = std::array<uint8_t, 32>;

    struct StreamEntry {
        uint8_t  link_id{0};
        uint8_t  sysid{0};
        uint8_t  compid{0};
        uint64_t last_timestamp{0};
        std::chrono::steady_clock::time_point last_seen{};
    };

    MavlinkPacketSigner(KeyType key, uint8_t link_id, uint64_t initial_timestamp)
        : secret_key_(key), link_id_(link_id), current_timestamp_(initial_timestamp) {}

    // Підписання вихідного пакета MAVLink v2
    std::vector<uint8_t> signPacket(std::span<const uint8_t> header_and_payload, uint16_t crc) {
        std::vector<uint8_t> frame;
        frame.reserve(header_and_payload.size() + 2 + kTrailerLen);
        
        // Копіюємо заголовок і корисні дані
        frame.insert(frame.end(), header_and_payload.begin(), header_and_payload.end());
        frame[2] |= kFlagSigned; // Виставляємо біт підпису в incompat_flags

        // Додаємо CRC-16 (Little-Endian)
        frame.push_back(static_cast<uint8_t>(crc & 0xFF));
        frame.push_back(static_cast<uint8_t>((crc >> 8) & 0xFF));

        // Формуємо трейлер: Link ID + Timestamp (48-bit)
        ++current_timestamp_;
        frame.push_back(link_id_);
        packUint48(frame, current_timestamp_);

        // Обчислюємо SHA-256 над [Secret Key] + [Frame Bytes Before Signature]
        auto hash = computeSha256(secret_key_, frame);

        // Додаємо перші 6 байтів гешу
        frame.insert(frame.end(), hash.begin(), hash.begin() + 6);
        return frame;
    }

    // Верифікація вхідного кадру
    [[nodiscard]] bool verifyPacket(std::span<const uint8_t> packet) {
        if (packet.size() < 10 + 2 + kTrailerLen || packet[0] != kStxV2 || !(packet[2] & kFlagSigned)) {
            return false;
        }

        const uint8_t payload_len = packet[1];
        const size_t expected_size = 10 + payload_len + 2 + kTrailerLen;
        if (packet.size() != expected_size) {
            return false;
        }

        const uint8_t sysid = packet[5];
        const uint8_t compid = packet[6];
        const size_t trailer_offset = 10 + payload_len + 2;
        const uint8_t incoming_link = packet[trailer_offset];
        const uint64_t incoming_ts = unpackUint48(packet.subspan(trailer_offset + 1, 6));

        // Перевірка монотонності часу в потоці
        auto stream_it = std::find_if(streams_.begin(), streams_.end(), [&](const StreamEntry& s) {
            return s.sysid == sysid && s.compid == compid && s.link_id == incoming_link;
        });

        if (stream_it != streams_.end() && incoming_ts <= stream_it->last_timestamp) {
            return false; // Відхилено: застарілий таймстемп або повтор!
        }

        // Обчислення очікуваного гешу SHA-256
        auto hash = computeSha256(secret_key_, packet.subspan(0, trailer_offset + 7));
        auto incoming_sig = packet.subspan(trailer_offset + 7, 6);

        if (!constantTimeEqual(incoming_sig, std::span<const uint8_t>(hash.data(), 6))) {
            return false; // Недійсний підпис
        }

        // Оновлення або реєстрація джерела в таблиці потоків
        auto now = std::chrono::steady_clock::now();
        if (stream_it != streams_.end()) {
            stream_it->last_timestamp = incoming_ts;
            stream_it->last_seen = now;
        } else {
            if (streams_.size() >= kMaxStreams) {
                // LRU витіснення
                auto oldest = std::min_element(streams_.begin(), streams_.end(),
                    [](const StreamEntry& a, const StreamEntry& b) { return a.last_seen < b.last_seen; });
                *oldest = {incoming_link, sysid, compid, incoming_ts, now};
            } else {
                streams_.push_back({incoming_link, sysid, compid, incoming_ts, now});
            }
        }

        return true;
    }

private:
    static void packUint48(std::vector<uint8_t>& dest, uint64_t val) {
        for (int i = 0; i < 6; ++i) {
            dest.push_back(static_cast<uint8_t>((val >> (i * 8)) & 0xFF));
        }
    }

    static uint64_t unpackUint48(std::span<const uint8_t> src) {
        uint64_t res = 0;
        for (int i = 0; i < 6; ++i) {
            res |= (static_cast<uint64_t>(src[i]) << (i * 8));
        }
        return res;
    }

    static bool constantTimeEqual(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
        if (a.size() != b.size()) return false;
        volatile uint8_t diff = 0;
        for (size_t i = 0; i < a.size(); ++i) {
            diff |= (a[i] ^ b[i]);
        }
        return diff == 0;
    }

    static std::array<uint8_t, 32> computeSha256(const KeyType& key, std::span<const uint8_t> data) {
        // Конкатенація ключа та даних у блоці SHA-256
        sha256_ctx_t sha;
        sha256_init(&sha);
        sha256_update(&sha, key.data(), key.size());
        sha256_update(&sha, data.data(), data.size());
        std::array<uint8_t, 32> out{};
        sha256_final(&sha, out.data());
        return out;
    }

    KeyType secret_key_;
    uint8_t link_id_;
    uint64_t current_timestamp_;
    std::vector<StreamEntry> streams_;
};
