namespace embedded::audit {

class IFlashStorage {
public:
    virtual ~IFlashStorage() = default;
    virtual std::expected<void, Status> read(uint32_t physical_addr, std::span<uint8_t> dst) noexcept = 0;
    virtual std::expected<void, Status> write_page(uint32_t physical_addr, std::span<const uint8_t> src) noexcept = 0;
    virtual std::expected<void, Status> erase_sector(uint32_t sector_addr) noexcept = 0;
    [[nodiscard]] virtual uint32_t total_size() const noexcept = 0;
    [[nodiscard]] virtual uint32_t sector_size() const noexcept = 0;
};

} // namespace embedded::audit
