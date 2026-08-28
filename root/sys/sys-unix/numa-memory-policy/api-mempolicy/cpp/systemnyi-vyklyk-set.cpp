[[nodiscard]] inline std::expected<void, std::error_code> set_home_node(
    std::span<std::byte> buffer,
    unsigned long home_node,
    unsigned long flags = 0) noexcept
{
    long ret = ::set_mempolicy_home_node(
        reinterpret_cast<unsigned long>(buffer.data()),
        buffer.size(), home_node, flags);
    if (ret != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
