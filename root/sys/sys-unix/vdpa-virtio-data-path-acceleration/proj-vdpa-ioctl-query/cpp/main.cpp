#include <iostream>
#include <format>
#include <span>
#include <array>
#include <string_view>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/vhost.h>
#include <linux/virtio_ids.h>

class ScopedFd {
public:
    explicit ScopedFd(int fd) noexcept : fd_(fd) {}
    ~ScopedFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_ = -1;
};

int main() {
    constexpr const char* dev_path = "/dev/vhost-vdpa-0";
    ScopedFd dev{::open(dev_path, O_RDWR)};

    if (!dev.valid()) {
        std::cerr << std::format("Не вдалося відкрити {}: {}\n",
                                 dev_path, std::generic_category().message(errno));
        return EXIT_FAILURE;
    }

    std::uint32_t device_id = 0;
    if (::ioctl(dev.get(), VHOST_VDPA_GET_DEVICE_ID, &device_id) < 0) {
        std::cerr << "Помилка VHOST_VDPA_GET_DEVICE_ID\n";
        return EXIT_FAILURE;
    }

    std::string_view type_str = (device_id == VIRTIO_ID_NET)   ? "virtio-net" :
                                (device_id == VIRTIO_ID_BLOCK) ? "virtio-blk" : "інший";

    std::cout << std::format("[+] vDPA Device ID: {} ({})\n", device_id, type_str);

    std::uint64_t features = 0;
    if (::ioctl(dev.get(), VHOST_GET_FEATURES, &features) < 0) {
        std::cerr << "Помилка VHOST_GET_FEATURES\n";
        return EXIT_FAILURE;
    }
    std::cout << std::format("[+] HW Feature Bits: {:#x}\n", features);

    std::uint8_t status = 0;
    if (::ioctl(dev.get(), VHOST_VDPA_GET_STATUS, &status) < 0) {
        std::cerr << "Помилка VHOST_VDPA_GET_STATUS\n";
        return EXIT_FAILURE;
    }
    std::cout << std::format("[+] Device Status Byte: {:#04x}\n", status);

    if (device_id == VIRTIO_ID_NET) {
        struct ConfigHeader {
            std::uint32_t off;
            std::uint32_t len;
            std::array<std::uint8_t, 6> mac;
        } cfg{.off = 0, .len = 6, .mac = {}};

        if (::ioctl(dev.get(), VHOST_VDPA_GET_CONFIG, &cfg) < 0) {
            std::cerr << "Помилка VHOST_VDPA_GET_CONFIG\n";
            return EXIT_FAILURE;
        }

        std::span<const std::uint8_t, 6> mac_span{cfg.mac};
        std::cout << std::format("[+] Hardware MAC Address: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}\n",
                                 mac_span[0], mac_span[1], mac_span[2],
                                 mac_span[3], mac_span[4], mac_span[5]);
    }

    return EXIT_SUCCESS;
}
