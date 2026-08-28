namespace embedded::config {

struct FlashHal {
    std::uint32_t slot_a_base_addr;
    std::uint32_t slot_b_base_addr;
    std::uint32_t sector_size;

    bool (*flash_erase_sector)(std::uint32_t sector_addr) noexcept = nullptr;
    bool (*flash_write_page)(std::uint32_t dest_addr, std::span<const std::uint8_t> src) noexcept = nullptr;
    bool (*flash_read_data)(std::uint32_t src_addr, std::span<std::uint8_t> dest) noexcept = nullptr;
};

} // namespace embedded::config
