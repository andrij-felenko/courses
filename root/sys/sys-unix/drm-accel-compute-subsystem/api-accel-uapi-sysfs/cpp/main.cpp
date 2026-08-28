#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>
#include <memory>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <drm/drm.h>

namespace accel {

class AccelDevice {
public:
    explicit AccelDevice(std::string_view path) {
        fd_ = ::open(path.data(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити прискорювач Accel");
        }
    }

    ~AccelDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    AccelDevice(const AccelDevice&) = delete;
    AccelDevice& operator=(const AccelDevice&) = delete;

    AccelDevice(AccelDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    AccelDevice& operator=(AccelDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int fd() const noexcept { return fd_; }

    struct DriverInfo {
        std::string name;
        std::string date;
        std::string desc;
    };

    [[nodiscard]] DriverInfo query_version() const {
        std::vector<char> name(32, 0);
        std::vector<char> date(32, 0);
        std::vector<char> desc(64, 0);

        drm_version ver{};
        ver.name_len = name.size() - 1;
        ver.name = name.data();
        ver.date_len = date.size() - 1;
        ver.date = date.data();
        ver.desc_len = desc.size() - 1;
        ver.desc = desc.data();

        if (::ioctl(fd_, DRM_IOCTL_VERSION, &ver) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка DRM_IOCTL_VERSION");
        }

        return DriverInfo{
            .name = std::string(name.data()),
            .date = std::string(date.data()),
            .desc = std::string(desc.data())
        };
    }

    [[nodiscard]] std::uint32_t create_syncobj(bool signaled = true) const {
        drm_syncobj_create req{};
        if (signaled) {
            req.flags = DRM_SYNCOBJ_CREATE_SIGNALED;
        }

        if (::ioctl(fd_, DRM_IOCTL_SYNCOBJ_CREATE, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка DRM_IOCTL_SYNCOBJ_CREATE");
        }
        return req.handle;
    }

    void destroy_syncobj(std::uint32_t handle) const noexcept {
        drm_syncobj_destroy req{.handle = handle};
        ::ioctl(fd_, DRM_IOCTL_SYNCOBJ_DESTROY, &req);
    }

private:
    int fd_{-1};
};

[[nodiscard]] inline std::string read_sysfs_value(std::string_view sysfs_path) {
    std::ifstream file(sysfs_path.data());
    if (!file.is_open()) {
        return "N/A";
    }
    std::string val;
    std::getline(file, val);
    return val;
}

} // namespace accel

int main() {
    try {
        accel::AccelDevice dev("/dev/accel/accel0");

        auto info = dev.query_version();
        std::cout << "[C++ RAII] Драйвер Accel: " << info.name 
                  << " (" << info.date << "), опис: " << info.desc << '\n';

        auto temp = accel::read_sysfs_value("/sys/class/accel/accel0/device/temperature");
        auto usage = accel::read_sysfs_value("/sys/class/accel/accel0/device/engine_usage");
        std::cout << "[sysfs] Температура NPU: " << temp << " mC, завантаження: " << usage << "%\n";

        std::uint32_t sync_handle = dev.create_syncobj(true);
        std::cout << "[C++ RAII] Створено syncobj handle: " << sync_handle << '\n';

        dev.destroy_syncobj(sync_handle);
    } catch (const std::exception& e) {
        std::cerr << "Помилка в програмі: " << e.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
