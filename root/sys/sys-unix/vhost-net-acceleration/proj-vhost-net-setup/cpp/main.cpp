#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <span>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/eventfd.h>
#include <net/if.h>
#include <linux/if_tun.h>
#include <linux/vhost.h>

namespace vhost {

class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.release()) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old_fd = fd_;
        fd_ = -1;
        return old_fd;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

class GuestMemory {
public:
    static std::expected<GuestMemory, std::error_code> allocate(size_t size) {
        void* addr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (addr == MAP_FAILED) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return GuestMemory(addr, size);
    }

    ~GuestMemory() {
        if (addr_ && size_ > 0) {
            ::munmap(addr_, size_);
        }
    }

    GuestMemory(const GuestMemory&) = delete;
    GuestMemory& operator=(const GuestMemory&) = delete;

    GuestMemory(GuestMemory&& other) noexcept : addr_(other.addr_), size_(other.size_) {
        other.addr_ = nullptr;
        other.size_ = 0;
    }

    GuestMemory& operator=(GuestMemory&& other) noexcept {
        if (this != &other) {
            if (addr_ && size_ > 0) ::munmap(addr_, size_);
            addr_ = other.addr_;
            size_ = other.size_;
            other.addr_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] void* data() const noexcept { return addr_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }

private:
    GuestMemory(void* addr, size_t size) : addr_(addr), size_(size) {}
    void* addr_{nullptr};
    size_t size_{0};
};

class VhostNetBackend {
public:
    static std::expected<VhostNetBackend, std::error_code> create(std::string_view tap_name, const GuestMemory& memory) {
        FileDescriptor tap_fd(::open("/dev/net/tun", O_RDWR));
        if (!tap_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct ifreq ifr{};
        ifr.ifr_flags = IFF_TAP | IFF_NO_PI;
        std::strncpy(ifr.ifr_name, tap_name.data(), std::min(tap_name.size(), sizeof(ifr.ifr_name) - 1));

        if (::ioctl(tap_fd.get(), TUNSETIFF, &ifr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        FileDescriptor vhost_fd(::open("/dev/vhost-net", O_RDWR));
        if (!vhost_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(vhost_fd.get(), VHOST_SET_OWNER, nullptr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // Передача карти пам'яті
        std::vector<uint8_t> mem_buf(sizeof(vhost_memory) + sizeof(vhost_memory_region));
        auto* mem = reinterpret_cast<vhost_memory*>(mem_buf.data());
        mem->nregions = 1;
        mem->regions[0].guest_phys_addr = 0x0;
        mem->regions[0].memory_size = memory.size();
        mem->regions[0].userspace_addr = reinterpret_cast<uint64_t>(memory.data());

        if (::ioctl(vhost_fd.get(), VHOST_SET_MEM_TABLE, mem) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        VhostNetBackend backend(std::move(tap_fd), std::move(vhost_fd));
        if (auto res = backend.configure_queues(memory); !res) {
            return std::unexpected(res.error());
        }

        return backend;
    }

private:
    VhostNetBackend(FileDescriptor tap_fd, FileDescriptor vhost_fd)
        : tap_fd_(std::move(tap_fd)), vhost_fd_(std::move(vhost_fd)) {}

    std::expected<void, std::error_code> configure_queues(const GuestMemory& memory) {
        auto* base_vring = reinterpret_cast<uint8_t*>(memory.data()) + 0x10000;

        for (uint32_t q = 0; q < 2; ++q) {
            vhost_vring_state state{.index = q, .num = 256};
            if (::ioctl(vhost_fd_.get(), VHOST_SET_VRING_NUM, &state) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            vhost_vring_addr addr{
                .index = q,
                .flags = 0,
                .desc_user_addr = reinterpret_cast<uint64_t>(base_vring + q * 0x4000),
                .used_user_addr = reinterpret_cast<uint64_t>(base_vring + q * 0x4000 + 0x2000),
                .avail_user_addr = reinterpret_cast<uint64_t>(base_vring + q * 0x4000 + 0x1000),
                .log_guest_addr = 0
            };

            if (::ioctl(vhost_fd_.get(), VHOST_SET_VRING_ADDR, &addr) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            FileDescriptor kick_fd(::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC));
            FileDescriptor call_fd(::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC));

            vhost_vring_file kick_file{.index = q, .fd = kick_fd.get()};
            vhost_vring_file call_file{.index = q, .fd = call_fd.get()};

            if (::ioctl(vhost_fd_.get(), VHOST_SET_VRING_KICK, &kick_file) < 0 ||
                ::ioctl(vhost_fd_.get(), VHOST_SET_VRING_CALL, &call_file) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            vhost_vring_file backend{.index = q, .fd = tap_fd_.get()};
            if (::ioctl(vhost_fd_.get(), VHOST_NET_SET_BACKEND, &backend) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            kick_fds_.push_back(std::move(kick_fd));
            call_fds_.push_back(std::move(call_fd));
        }
        return {};
    }

    FileDescriptor tap_fd_;
    FileDescriptor vhost_fd_;
    std::vector<FileDescriptor> kick_fds_;
    std::vector<FileDescriptor> call_fds_;
};

} // namespace vhost

int main() {
    auto guest_mem = vhost::GuestMemory::allocate(64 * 1024 * 1024);
    if (!guest_mem) {
        std::cerr << "Помилка виділення пам'яті: " << guest_mem.error().message() << '\n';
        return 1;
    }

    auto backend = vhost::VhostNetBackend::create("vhost-tap0", *guest_mem);
    if (!backend) {
        std::cerr << "Помилка налаштування vhost-net: " << backend.error().message() << '\n';
        return 1;
    }

    std::cout << "vhost-net успішно ініціалізовано на C++20 (RAII, std::expected)!\n";
    std::cout << "Натисніть Enter для виходу...\n";
    std::cin.get();

    return 0;
}
