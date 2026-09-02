#pragma once
// Фаза 5: кінцевий автомат, що зшиває всі фази в один неблокувальний рушій.
#include "mission_sync.h"
#include "param_sync.h"
#include "serial_link.h"
#include "telemetry_budget.h"
#include "vehicle_registry.h"

enum class GcsState {
    WaitHeartbeat,
    Capabilities,
    ParamDownload,
    ConfigureStreams,
    MissionDownload,
    Operational,
    LinkLost,
};

const char* stateName(GcsState state);

class HandshakeEngine {
public:
    HandshakeEngine(SerialLink& link, std::uint8_t gcs_sysid = 255,
                    std::uint8_t gcs_compid = MAV_COMP_ID_MISSIONPLANNER);

    void onMessage(const mavlink_message_t& msg, Clock::time_point now);
    void tick(Clock::time_point now);
    GcsState state() const { return state_; }

private:
    void enter(GcsState state, Clock::time_point now);
    void requestCapabilities(Clock::time_point now);
    void beginParams(Clock::time_point now);
    void sendGcsHeartbeat(Clock::time_point now);
    void updatePacing(Clock::time_point now);
    void showTelemetry(const mavlink_message_t& msg, Clock::time_point now);

    SerialLink& link_;
    std::uint8_t gcs_sysid_, gcs_compid_;

    VehicleRegistry registry_;
    ParamSync params_;
    TelemetrySetup telemetry_;
    MissionSync mission_;

    GcsState state_ = GcsState::WaitHeartbeat;
    GcsState resume_ = GcsState::WaitHeartbeat;  // куди повернутись після LINK_LOST
    std::uint8_t tsys_ = 0, tcomp_ = 0;

    int caps_attempts_ = 0;
    Clock::time_point caps_tx_{};
    Clock::time_point last_gcs_hb_{};
    Clock::time_point last_pacing_{};
    Clock::time_point last_hud_{};
};
