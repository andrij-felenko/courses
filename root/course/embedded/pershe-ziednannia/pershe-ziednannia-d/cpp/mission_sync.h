#pragma once
// Фаза 4: транзакційна вичитка польотного завдання з борту.
#include <vector>

#include "serial_link.h"

struct MissionItem {
    std::uint16_t seq = 0;
    std::uint16_t command = 0;   // MAV_CMD_NAV_*
    std::uint8_t frame = 0;      // MAV_FRAME: як тлумачити висоту
    double lat_deg = 0.0;        // з int32 × 1e-7 — дискретність 1.1 см
    double lon_deg = 0.0;
    float alt_m = 0.0f;
    float hold_s = 0.0f;         // param1
    float accept_radius_m = 0.0f;  // param2
};

const char* frameName(std::uint8_t frame);
const char* navCommandName(std::uint16_t command);

class MissionSync {
public:
    static constexpr auto kItemTimeout = std::chrono::milliseconds(1500);
    static constexpr int kMaxRetries = 5;

    MissionSync(SerialLink& link, std::uint8_t gcs_sysid, std::uint8_t gcs_compid);

    void start(std::uint8_t tsys, std::uint8_t tcomp, Clock::time_point now);
    void onMessage(const mavlink_message_t& msg, Clock::time_point now);
    void tick(Clock::time_point now);

    bool done() const { return state_ == State::Done; }
    bool failed() const { return state_ == State::Failed; }
    void setPacing(std::chrono::milliseconds gap) { pacing_ = gap; }
    const std::vector<MissionItem>& items() const { return items_; }

private:
    enum class State { Idle, WaitCount, WaitItem, Done, Failed };

    void sendRequestList(Clock::time_point now);
    void sendRequestItem(Clock::time_point now);
    void sendAck(std::uint8_t type);

    SerialLink& link_;
    std::uint8_t gcs_sysid_, gcs_compid_;
    std::uint8_t tsys_ = 0, tcomp_ = 0;

    State state_ = State::Idle;
    std::uint16_t count_ = 0;
    std::uint16_t expected_ = 0;  // номер точки, яку чекаємо просто зараз
    int retries_ = 0;
    std::vector<MissionItem> items_;
    Clock::time_point last_tx_{};
    std::chrono::milliseconds pacing_{0};
};
