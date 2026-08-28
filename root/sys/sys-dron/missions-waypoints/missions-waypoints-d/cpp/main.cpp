#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <optional>
#include <algorithm>

#pragma pack(push, 1)
struct MissionItem {
    float param1{0.0f};
    float param2{0.0f};
    float param3{0.0f};
    float param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float z{0.0f};
    uint16_t seq{0};
    uint16_t command{16};
    uint8_t frame{3};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};
};
#pragma pack(pop)

enum class MissionState : uint8_t {
    Idle,
    Uploading,
    Downloading,
    Active,
    Paused
};

enum class MissionAckResult : uint8_t {
    Accepted = 0,
    Error = 1,
    UnsupportedFrame = 2,
    Unsupported = 3,
    NoSpace = 4,
    Invalid = 5,
    InvalidSequence = 13,
    Cancelled = 15
};

class IMavlinkMissionMessenger {
public:
    virtual ~IMavlinkMissionMessenger() = default;
    virtual void send_request_int(uint8_t sysid, uint8_t compid, uint16_t seq) = 0;
    virtual void send_ack(uint8_t sysid, uint8_t compid, MissionAckResult result) = 0;
    virtual void send_current(uint16_t current_seq) = 0;
    virtual void send_item_reached(uint16_t reached_seq) = 0;
};

class MissionManager {
public:
    static constexpr size_t MAX_ITEMS = 500;
    static constexpr uint32_t TIMEOUT_MS = 1500;
    static constexpr uint8_t MAX_RETRIES = 5;

    explicit MissionManager(IMavlinkMissionMessenger& messenger)
        : m_messenger(messenger) {}

    void on_mission_count(uint8_t sysid, uint8_t compid, uint16_t count, uint32_t now_ms) noexcept {
        if (count > MAX_ITEMS) {
            m_messenger.send_ack(sysid, compid, MissionAckResult::NoSpace);
            return;
        }

        if (count == 0) {
            m_active_count = 0;
            m_current_active_seq = 0;
            m_state = MissionState::Idle;
            m_messenger.send_ack(sysid, compid, MissionAckResult::Accepted);
            return;
        }

        m_state = MissionState::Uploading;
        m_staging_count = count;
        m_transfer_seq = 0;
        m_retry_count = 0;
        m_partner_sysid = sysid;
        m_partner_compid = compid;
        m_last_transfer_time_ms = now_ms;

        m_messenger.send_request_int(sysid, compid, 0);
    }

    void on_mission_item(const MissionItem& item, uint32_t now_ms) noexcept {
        if (m_state != MissionState::Uploading) {
            return;
        }

        if (item.seq != m_transfer_seq) {
            m_messenger.send_request_int(m_partner_sysid, m_partner_compid, m_transfer_seq);
            return;
        }

        m_staging_buffer[m_transfer_seq] = item;
        m_transfer_seq++;
        m_retry_count = 0;
        m_last_transfer_time_ms = now_ms;

        if (m_transfer_seq < m_staging_count) {
            m_messenger.send_request_int(m_partner_sysid, m_partner_compid, m_transfer_seq);
        } else {
            // Атомарна фіксація місії
            std::copy_n(m_staging_buffer.begin(), m_staging_count, m_active_buffer.begin());
            m_active_count = m_staging_count;
            m_current_active_seq = (m_active_count > 1) ? 1 : 0;
            m_state = MissionState::Idle;

            m_messenger.send_ack(m_partner_sysid, m_partner_compid, MissionAckResult::Accepted);
            m_messenger.send_current(m_current_active_seq);
        }
    }

    void tick(uint32_t now_ms) noexcept {
        if (m_state != MissionState::Uploading) {
            return;
        }

        if ((now_ms - m_last_transfer_time_ms) >= TIMEOUT_MS) {
            if (m_retry_count < MAX_RETRIES) {
                m_retry_count++;
                m_last_transfer_time_ms = now_ms;
                m_messenger.send_request_int(m_partner_sysid, m_partner_compid, m_transfer_seq);
            } else {
                m_state = MissionState::Idle;
                m_messenger.send_ack(m_partner_sysid, m_partner_compid, MissionAckResult::Cancelled);
            }
        }
    }

    [[nodiscard]] bool advance_waypoint() noexcept {
        if (m_active_count == 0 || m_current_active_seq >= m_active_count - 1) {
            return false;
        }

        m_messenger.send_item_reached(m_current_active_seq);
        m_current_active_seq++;
        m_messenger.send_current(m_current_active_seq);
        return true;
    }

    [[nodiscard]] std::optional<MissionItem> current_item() const noexcept {
        if (m_active_count == 0 || m_current_active_seq >= m_active_count) {
            return std::nullopt;
        }
        return m_active_buffer[m_current_active_seq];
    }

    [[nodiscard]] uint16_t active_count() const noexcept { return m_active_count; }
    [[nodiscard]] uint16_t current_seq() const noexcept { return m_current_active_seq; }
    [[nodiscard]] MissionState state() const noexcept { return m_state; }

private:
    IMavlinkMissionMessenger& m_messenger;
    MissionState m_state{MissionState::Idle};
    std::array<MissionItem, MAX_ITEMS> m_active_buffer{};
    std::array<MissionItem, MAX_ITEMS> m_staging_buffer{};
    uint16_t m_active_count{0};
    uint16_t m_staging_count{0};
    uint16_t m_transfer_seq{0};
    uint16_t m_current_active_seq{0};
    uint32_t m_last_transfer_time_ms{0};
    uint8_t m_retry_count{0};
    uint8_t m_partner_sysid{0};
    uint8_t m_partner_compid{0};
};
