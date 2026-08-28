#include <iostream>
#include <expected>
#include <system_error>
#include <cstdint>
#include <span>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* Інвалідація IOTLB у C++20 з використанням std::span */
[[nodiscard]] std::expected<void, std::error_code> invalidate_stage1_iotlb_cpp(
    int iommufd_fd, 
    std::uint32_t nested_hwpt_id,
    std::span<const iommu_hwpt_vtd_s1_invalidate> entries) noexcept
{
    iommu_hwpt_invalidate inv_cmd{};
    inv_cmd.size = sizeof(inv_cmd);
    inv_cmd.hwpt_id = nested_hwpt_id;
    inv_cmd.data_type = IOMMU_HWPT_INVALIDATE_DATA_VTD_S1;
    inv_cmd.entry_len = sizeof(iommu_hwpt_vtd_s1_invalidate);
    inv_cmd.entry_num = static_cast<std::uint32_t>(entries.size());
    inv_cmd.inv_data_uptr = reinterpret_cast<std::uint64_t>(entries.data());

    if (::ioctl(iommufd_fd, IOMMU_HWPT_INVALIDATE, &inv_cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
