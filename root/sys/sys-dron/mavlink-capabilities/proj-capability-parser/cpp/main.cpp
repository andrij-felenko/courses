#include <cstdint>
#include <string>
#include <string_view>
#include <array>
#include <format>
#include <chrono>
#include <iostream>
#include <span>
#include <optional>

enum class ReleaseType : uint8_t {
    Dev      = 0,
    Alpha    = 64,
    Beta     = 128,
    Rc       = 192,
    Official = 255
};

enum class NegotiatorState {
    Idle,
    Requesting,
    WaitingResponse,
    Negotiated,
    FallbackDegraded
};

struct VehicleCapabilities {
    uint8_t major{0};
    uint8_t minor{0};
    uint8_t patch{0};
    ReleaseType release_type{ReleaseType::Dev};
    std::string version_string;
    std::string git_hash;
    std::string uid2_formatted;

    bool supports_mission_int{false};
    bool supports_ftp{false};
    bool supports_param_union{false};
    bool supports_mavlink2{false};
    bool supports_offboard_ned{false};
    bool supports_compass_calibration{false};
    bool supports_terrain{false};
    bool supports_flight_info{false};
};

class CapabilityNegotiator {
public:
    static constexpr uint64_t CAP_MISSION_INT = (1ULL << 2);
    static constexpr uint64_t CAP_PARAM_UNION = (1ULL << 4);
    static constexpr uint64_t CAP_FTP         = (1ULL << 5);
    static constexpr uint64_t CAP_SET_POS_NED = (1ULL << 7);
    static constexpr uint64_t CAP_TERRAIN     = (1ULL << 9);
    static constexpr uint64_t CAP_COMPASS_CAL = (1ULL << 11);
    static constexpr uint64_t CAP_MAVLINK2    = (1ULL << 12);
    static constexpr uint64_t CAP_FLIGHT_INFO = (1ULL << 15);

    CapabilityNegotiator(uint8_t sysid, uint8_t compid)
        : target_sysid_(sysid), target_compid_(compid) {}

    void on_heartbeat_detected(std::chrono::steady_clock::time_point now) {
        if (state_ == NegotiatorState::Idle) {
            state_ = NegotiatorState::Requesting;
            retry_count_ = 0;
            last_request_time_ = now;
        }
    }

    void update(std::chrono::steady_clock::time_point now) {
        using namespace std::chrono_literals;

        if (state_ == NegotiatorState::Requesting) {
            std::cout << std::format("[CPP-Negotiator] Відправка MAV_CMD_REQUEST_MESSAGE(148) до sysid={} compid={} (спроба {})\n",
                                     target_sysid_, target_compid_, retry_count_ + 1);
            last_request_time_ = now;
            state_ = NegotiatorState::WaitingResponse;
        } else if (state_ == NegotiatorState::WaitingResponse) {
            if (now - last_request_time_ > 1000ms) {
                retry_count_++;
                if (retry_count_ >= 3) {
                    std::cout << "[CPP-Negotiator] Досягнуто ліміт спроб. Перехід у FallbackDegraded.\n";
                    state_ = NegotiatorState::FallbackDegraded;
                    caps_ = VehicleCapabilities{}; // Базові нульові можливості
                } else {
                    state_ = NegotiatorState::Requesting;
                }
            }
        }
    }

    void handle_autopilot_version(uint64_t capabilities,
                                  uint32_t flight_sw_version,
                                  std::span<const uint8_t, 8> custom_version,
                                  std::span<const uint8_t, 18> uid2_bytes) {
        if (state_ != NegotiatorState::WaitingResponse && state_ != NegotiatorState::Requesting) {
            return;
        }

        VehicleCapabilities c;
        c.major = static_cast<uint8_t>((flight_sw_version >> 24) & 0xFF);
        c.minor = static_cast<uint8_t>((flight_sw_version >> 16) & 0xFF);
        c.patch = static_cast<uint8_t>((flight_sw_version >> 8) & 0xFF);
        c.release_type = static_cast<ReleaseType>(flight_sw_version & 0xFF);

        std::string_view suffix;
        switch (c.release_type) {
            case ReleaseType::Dev:      suffix = "-dev"; break;
            case ReleaseType::Alpha:    suffix = "-alpha"; break;
            case ReleaseType::Beta:     suffix = "-beta"; break;
            case ReleaseType::Rc:       suffix = "-rc"; break;
            case ReleaseType::Official: suffix = ""; break;
        }
        c.version_string = std::format("v{}.{}.{}{}", c.major, c.minor, c.patch, suffix);

        // Форматування Git SHA
        for (uint8_t b : custom_version) {
            c.git_hash += std::format("{:02x}", b);
        }

        // Форматування UID2
        for (size_t i = 0; i < uid2_bytes.size(); ++i) {
            c.uid2_formatted += std::format("{:02X}", uid2_bytes[i]);
            if (i + 1 < uid2_bytes.size()) c.uid2_formatted += '-';
        }

        // Бітова маска
        c.supports_mission_int        = (capabilities & CAP_MISSION_INT) != 0;
        c.supports_ftp                = (capabilities & CAP_FTP) != 0;
        c.supports_param_union        = (capabilities & CAP_PARAM_UNION) != 0;
        c.supports_mavlink2           = (capabilities & CAP_MAVLINK2) != 0;
        c.supports_offboard_ned       = (capabilities & CAP_SET_POS_NED) != 0;
        c.supports_compass_calibration = (capabilities & CAP_COMPASS_CAL) != 0;
        c.supports_terrain            = (capabilities & CAP_TERRAIN) != 0;
        c.supports_flight_info        = (capabilities & CAP_FLIGHT_INFO) != 0;

        caps_ = std::move(c);
        state_ = NegotiatorState::Negotiated;

        std::cout << std::format("[CPP-Negotiator] Узгодження успішне!\n"
                                 "  Версія: {} (Git: {})\n"
                                 "  UID2: {}\n"
                                 "  MISSION_INT: {}, FTP: {}, MAVLink2: {}, Terrain: {}, FlightInfo: {}\n",
                                 caps_->version_string, caps_->git_hash,
                                 caps_->uid2_formatted, caps_->supports_mission_int,
                                 caps_->supports_ftp, caps_->supports_mavlink2,
                                 caps_->supports_terrain, caps_->supports_flight_info);
    }

    [[nodiscard]] NegotiatorState state() const noexcept { return state_; }
    [[nodiscard]] const std::optional<VehicleCapabilities>& capabilities() const noexcept { return caps_; }

private:
    NegotiatorState state_{NegotiatorState::Idle};
    uint8_t target_sysid_{1};
    uint8_t target_compid_{1};
    uint8_t retry_count_{0};
    std::chrono::steady_clock::time_point last_request_time_{};
    std::optional<VehicleCapabilities> caps_{std::nullopt};
};
