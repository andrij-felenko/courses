enum class PacketFlags : std::uint32_t {
    None     = 0,
    Keyframe = 1 << 0,
    Corrupt  = 1 << 1
};

struct MediaPacket {
    std::uint32_t stream_index{0};
    std::vector<std::uint8_t> data;
    std::int64_t pts{0};
    std::int64_t dts{0};
    std::int64_t duration{0};
    PacketFlags flags{PacketFlags::None};
};
