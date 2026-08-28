MAVPACKED(
typedef struct __mavlink_perimeter_beacon_status_t {
    uint64_t time_usec;         // зсув 0
    float    range_m;           // зсув 8
    uint16_t beacon_id;         // зсув 12
    uint8_t  quality;           // зсув 14
    uint8_t  target_system;     // зсув 15
    uint8_t  target_component;  // зсув 16
    float    bearing_deg;       // зсув 17 — розширення
}) mavlink_perimeter_beacon_status_t;
