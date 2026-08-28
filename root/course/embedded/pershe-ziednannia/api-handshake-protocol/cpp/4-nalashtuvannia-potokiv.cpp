struct MavlinkCommandLong {
    float    param1{0.0f};
    float    param2{0.0f};
    float    param3{0.0f};
    float    param4{0.0f};
    float    param5{0.0f};
    float    param6{0.0f};
    float    param7{0.0f};
    uint16_t command{0};
    uint8_t  target_system{1};
    uint8_t  target_component{1};
    uint8_t  confirmation{0};
};
