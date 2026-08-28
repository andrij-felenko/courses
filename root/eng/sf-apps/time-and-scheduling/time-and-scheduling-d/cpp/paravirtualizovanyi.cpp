struct alignas(32) PvclockVcpuTimeInfo {
    uint32_t version{0};
    uint32_t pad0{0};
    uint64_t tsc_timestamp{0};
    uint64_t system_time{0};
    uint32_t tsc_to_system_mul{0};
    int8_t   tsc_shift{0};
    uint8_t  flags{0};
    std::array<uint8_t, 2> pad{};
};
