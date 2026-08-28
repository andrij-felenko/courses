#include <iostream>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <utility>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* RAII-обгортка для управління файловим дескриптором IOMMUFD */
class UniqueFd {
    int fd_ = -1;
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
};

/* Специфічна конфігурація Intel VT-d Stage 1 */
struct VtdStage1Config {
    std::uint64_t flags{0};
    std::uint64_t pgtbl_pptr{0};
    std::uint32_t addr_width{48};
    std::uint32_t pad{0};
};

/* Ідіоматична реалізація створення вкладеної HWPT Стадії 1 у C++20 */
[[nodiscard]] std::expected<std::uint32_t, std::error_code> create_nested_stage1_hwpt_cpp(
    int iommufd,
    std::uint32_t dev_id,
    std::uint32_t stage2_hwpt_id,
    std::uint64_t l1_page_table_root) noexcept
{
    if (iommufd < 0) {
        return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
    }

    VtdStage1Config vtd_cfg{
        .flags = 0,
        .pgtbl_pptr = l1_page_table_root,
        .addr_width = 48,
        .pad = 0
    };

    iommu_hwpt_alloc alloc_cmd{};
    alloc_cmd.size = sizeof(alloc_cmd);
    alloc_cmd.flags = 0; // вкладеність задає не прапорець, а батьківський pt_id
    alloc_cmd.dev_id = dev_id;
    alloc_cmd.pt_id = stage2_hwpt_id;
    alloc_cmd.data_type = IOMMU_HWPT_DATA_VTD_S1;
    alloc_cmd.data_len = sizeof(vtd_cfg);
    alloc_cmd.data_uptr = reinterpret_cast<std::uint64_t>(&vtd_cfg);

    if (::ioctl(iommufd, IOMMU_HWPT_ALLOC, &alloc_cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return alloc_cmd.out_hwpt_id;
}
