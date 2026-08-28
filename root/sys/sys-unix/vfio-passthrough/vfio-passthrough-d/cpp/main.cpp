#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <linux/vfio.h>
#include <string>
#include <utility>
#include <cerrno>
#include <system_error>
#include <expected>

struct VfioHandles {
    int container_fd{-1};
    int group_fd{-1};
    int device_fd{-1};

    VfioHandles() noexcept = default;
    VfioHandles(const VfioHandles&) = delete;
    VfioHandles& operator=(const VfioHandles&) = delete;
    VfioHandles(VfioHandles&& o) noexcept
        : container_fd(std::exchange(o.container_fd, -1)),
          group_fd(std::exchange(o.group_fd, -1)),
          device_fd(std::exchange(o.device_fd, -1)) {}

    ~VfioHandles() {
        if (device_fd >= 0) ::close(device_fd);
        if (group_fd >= 0) ::close(group_fd);
        if (container_fd >= 0) ::close(container_fd);
    }
};

std::expected<VfioHandles, std::error_code> init_vfio_device(int group_id, const char* pci_bdf) {
    VfioHandles h;
    h.container_fd = ::open("/dev/vfio/vfio", O_RDWR);
    if (h.container_fd < 0) return std::unexpected(std::error_code(errno, std::generic_category()));

    std::string group_path = "/dev/vfio/" + std::to_string(group_id);
    h.group_fd = ::open(group_path.c_str(), O_RDWR);
    if (h.group_fd < 0) return std::unexpected(std::error_code(errno, std::generic_category()));

    vfio_group_status status{.argsz = sizeof(status)};
    if (::ioctl(h.group_fd, VFIO_GROUP_GET_STATUS, &status) < 0 || !(status.flags & VFIO_GROUP_FLAGS_VIABLE)) {
        return std::unexpected(std::make_error_code(std::errc::device_or_resource_busy));
    }

    if (::ioctl(h.group_fd, VFIO_GROUP_SET_CONTAINER, &h.container_fd) < 0 ||
        ::ioctl(h.container_fd, VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    h.device_fd = ::ioctl(h.group_fd, VFIO_GROUP_GET_DEVICE_FD, pci_bdf);
    if (h.device_fd < 0) return std::unexpected(std::error_code(errno, std::generic_category()));

    return h;
}
