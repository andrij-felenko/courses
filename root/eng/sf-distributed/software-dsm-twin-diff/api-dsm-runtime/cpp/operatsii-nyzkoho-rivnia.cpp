class IDsmDiffEngine {
public:
    virtual ~IDsmDiffEngine() = default;
    virtual size_t computeDiff(std::span<const std::byte, DsmPageSize> page,
                               std::span<const std::byte, DsmPageSize> twin,
                               DiffPacket& packetOut) noexcept = 0;
    virtual std::expected<void, DsmErrorCode> applyDiff(std::span<std::byte, DsmPageSize> targetPage,
                                                        const DiffPacket& packetIn) noexcept = 0;
    virtual std::expected<void, DsmErrorCode> consolidatePage(uint32_t pageId) noexcept = 0;
};
