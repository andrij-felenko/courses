/* Ідіоматична реалізація створення мапінгу IOAS у C++20 */
[[nodiscard]] std::expected<void, std::error_code> map_ioas_region_cpp(
    int iommufd_fd,
    std::uint32_t ioas_id,
    std::uint64_t hva_address,
    std::uint64_t l1_gpa_address,
    std::uint64_t memory_region_size) noexcept
{
    iommu_ioas_map map_cmd{};
    map_cmd.size = sizeof(map_cmd);
    map_cmd.ioas_id = ioas_id;
    map_cmd.flags = IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE |
                    IOMMU_IOAS_MAP_FIXED_IOVA; // IOVA задає викликач, а не ядро
    map_cmd.user_va = hva_address;
    map_cmd.iova = l1_gpa_address;
    map_cmd.length = memory_region_size;

    if (::ioctl(iommufd_fd, IOMMU_IOAS_MAP, &map_cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
