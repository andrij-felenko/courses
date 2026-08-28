enum class GoalType : uint8_t {
    None = 0,
    Waypoint,
    HoldHeading,
    StationKeep,
    InspectScan,
    PayloadDrop
};

enum class GoalStatus : uint8_t {
    Pending = 0,
    Active,
    Succeeded,
    Timeout,
    Aborted
};

struct WaypointArgs {
    int32_t target_x_mm{0};
    int32_t target_y_mm{0};
    float cruise_speed_mps{1.0f};
    float acceptance_radius_mm{200.0f};
};

struct HoldArgs {
    uint32_t duration_ms{0};
    float target_yaw_rad{0.0f};
};

struct ScanArgs {
    uint8_t pattern_id{0};
    uint16_t sample_count{0};
};

using GoalArgs = std::variant<std::monostate, WaypointArgs, HoldArgs, ScanArgs>;

struct Goal {
    GoalType type{GoalType::None};
    GoalStatus status{GoalStatus::Pending};
    uint16_t goal_id{0};
    uint32_t timeout_ms{0};
    uint32_t start_time_ms{0};
    GoalArgs args{};
    void (*on_abort_cleanup)(void* context){nullptr};
};
