// Dom0 Backend Mapper у стилі ідіоматичного C++20 (RAII, std::span, std::expected)
#include <iostream>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

#include <xen/gntdev.h>
#include <xen/evtchn.h>

namespace xen {

constexpr std::size_t PageSize = 4096;

// RAII обгортка для файлового дескриптора
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для відображеної сторінки гранту
class MappedGrant {
    UniqueFd& gntdev_fd_;
    std::uint64_t map_index_{0};
    void* addr_{MAP_FAILED};

public:
    MappedGrant(UniqueFd& gntdev_fd, std::uint32_t domid, std::uint32_t gref)
        : gntdev_fd_(gntdev_fd) {

        ioctl_gntdev_map_grant_ref map_req{};
        map_req.count = 1;
        map_req.refs[0].domid = domid;
        map_req.refs[0].ref = gref;

        if (::ioctl(gntdev_fd_.get(), IOCTL_GNTDEV_MAP_GRANT_REF, &map_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "IOCTL_GNTDEV_MAP_GRANT_REF failed");
        }

        map_index_ = map_req.index;
        addr_ = ::mmap(nullptr, PageSize, PROT_READ | PROT_WRITE, MAP_SHARED,
                       gntdev_fd_.get(), map_index_);

        if (addr_ == MAP_FAILED) {
            // Очищення через ioctl у разі збою mmap
            ioctl_gntdev_unmap_grant_ref unmap_req{map_index_, 1};
            ::ioctl(gntdev_fd_.get(), IOCTL_GNTDEV_UNMAP_GRANT_REF, &unmap_req);
            throw std::system_error(errno, std::generic_category(), "mmap failed for grant page");
        }
    }

    ~MappedGrant() {
        if (addr_ != MAP_FAILED) {
            ::munmap(addr_, PageSize);
            ioctl_gntdev_unmap_grant_ref unmap_req{map_index_, 1};
            ::ioctl(gntdev_fd_.get(), IOCTL_GNTDEV_UNMAP_GRANT_REF, &unmap_req);
        }
    }

    MappedGrant(const MappedGrant&) = delete;
    MappedGrant& operator=(const MappedGrant&) = delete;

    [[nodiscard]] std::span<std::byte> buffer() noexcept {
        return {static_cast<std::byte*>(addr_), PageSize};
    }

    [[nodiscard]] std::span<const std::byte> buffer() const noexcept {
        return {static_cast<const std::byte*>(addr_), PageSize};
    }
};

// Функція обробки гранту з поверненням std::expected
std::expected<void, std::string> process_grant(std::uint32_t domid, std::uint32_t gref, std::uint32_t port) {
    UniqueFd gntdev{::open("/dev/xen/gntdev", O_RDWR)};
    if (!gntdev.valid()) {
        return std::unexpected("Cannot open /dev/xen/gntdev");
    }

    try {
        MappedGrant grant{gntdev, domid, gref};
        auto buf = grant.buffer();
        
        const char* raw = reinterpret_cast<const char*>(buf.data());
        std::string_view message{raw, ::strnlen(raw, buf.size())};
        std::cout << "[Dom0 C++] Data from DomU: " << message << std::endl;

        // Сповіщення через Event Channel
        UniqueFd evtchn{::open("/dev/xen/evtchn", O_RDWR)};
        if (evtchn.valid()) {
            ioctl_evtchn_notify notify{port};
            if (::ioctl(evtchn.get(), IOCTL_EVTCHN_NOTIFY, &notify) == 0) {
                std::cout << "[Dom0 C++] Sent notify to port " << port << std::endl;
            }
        }
        return {};
    } catch (const std::exception& ex) {
        return std::unexpected(ex.what());
    }
}

} // namespace xen

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <domid> <gref> <evtchn_port>\n";
        return 1;
    }

    auto domid = static_cast<std::uint32_t>(std::stoul(argv[1]));
    auto gref  = static_cast<std::uint32_t>(std::stoul(argv[2]));
    auto port  = static_cast<std::uint32_t>(std::stoul(argv[3]));

    auto result = xen::process_grant(domid, gref, port);
    if (!result) {
        std::cerr << "[Error] " << result.error() << std::endl;
        return 1;
    }

    return 0;
}
