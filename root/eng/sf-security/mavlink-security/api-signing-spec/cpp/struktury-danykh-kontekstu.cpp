#include <cstdint>
#include <array>
#include <span>
#include <functional>

// Стан одного зареєстрованого потоку в C++
struct MavlinkSigningStream {
    uint8_t  link_id{0};
    uint8_t  sysid{0};
    uint8_t  compid{0};
    uint8_t  flags{0};
    uint64_t last_timestamp{0};
};

// Таблиця потоків для запобігання атакам повтору
struct MavlinkSigningStreams {
    static constexpr size_t kMaxStreams = 16;
    uint16_t num_streams{0};
    std::array<MavlinkSigningStream, kMaxStreams> streams{};

    MavlinkSigningStream* findStream(uint8_t sysid, uint8_t compid, uint8_t link_id) noexcept {
        for (uint16_t i = 0; i < num_streams; ++i) {
            if (streams[i].sysid == sysid &&
                streams[i].compid == compid &&
                streams[i].link_id == link_id) {
                return &streams[i];
            }
        }
        return nullptr;
    }

    MavlinkSigningStream* allocateStream(uint8_t sysid, uint8_t compid, uint8_t link_id) noexcept {
        if (num_streams < kMaxStreams) {
            auto& s = streams[num_streams++];
            s.sysid = sysid;
            s.compid = compid;
            s.link_id = link_id;
            s.last_timestamp = 0;
            return &s;
        }
        return nullptr;
    }
};

struct MavlinkStatus;

using AcceptUnsignedCallback = std::function<bool(const MavlinkStatus& status, uint32_t msgid)>;

// Контекст підпису MAVLink в ідіоматичному C++
struct MavlinkSigningContext {
    uint8_t  flags{0};
    uint8_t  link_id{0};
    uint64_t timestamp{0};
    std::array<uint8_t, 32> secret_key{};
    MavlinkSigningStreams*  streams{nullptr};
    AcceptUnsignedCallback  accept_unsigned_fn{nullptr};
};
