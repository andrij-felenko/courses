struct ChannelDescriptor {
    enum class Type { Pressure, Temperature };
    Type type;
    uint32_t infoMask;
};

inline constexpr std::array bmp280Channels = {
    ChannelDescriptor{ ChannelDescriptor::Type::Pressure, 0x07 },
    ChannelDescriptor{ ChannelDescriptor::Type::Temperature, 0x03 }
};
