struct MavlinkMissionItemInt {
    float   param1{0.0f};
    float   param2{0.0f};
    float   param3{0.0f};
    float   param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float   z{0.0f};
    uint16_t seq{0};
    uint16_t command{0};
    uint8_t target_system{0};
    uint8_t target_component{0};
    uint8_t frame{0};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};
};
