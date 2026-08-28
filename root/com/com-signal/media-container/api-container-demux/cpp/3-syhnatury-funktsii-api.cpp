class IDemuxer {
public:
    virtual ~IDemuxer() = default;

    virtual std::expected<void, std::string> open(std::string_view url) = 0;
    virtual std::uint32_t getStreamCount() const noexcept = 0;
    virtual std::expected<StreamInfo, std::string> getStreamInfo(std::uint32_t streamIndex) const = 0;
    virtual std::expected<MediaPacket, std::string> readPacket() = 0;
    virtual std::expected<void, std::string> seek(std::uint32_t streamIndex, std::int64_t targetPts, bool seekBackward) = 0;
};
