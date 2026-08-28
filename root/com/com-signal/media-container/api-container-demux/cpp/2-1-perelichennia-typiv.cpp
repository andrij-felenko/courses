enum class MediaStreamType : std::uint8_t {
    Unknown = 0,
    Video,
    Audio,
    Subtitle
};

enum class MediaCodecID : std::uint16_t {
    Unknown = 0,
    H264,
    HevcH265,
    Av1,
    Aac,
    Opus,
    PcmS16LE
};
