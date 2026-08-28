#include <sys/socket.h>
#include <linux/if_xdp.h>
#include <unistd.h>
#include <cstdlib>
#include <system_error>
#include <memory>
#include <span>

class UmemArea {
    void* addr_{nullptr};
    size_t size_{0};
    uint32_t chunk_size_{2048};
public:
    UmemArea(int xsk_fd, size_t size, uint32_t chunk_size = 2048, uint32_t headroom = 0)
        : size_(size), chunk_size_(chunk_size) {
        if (posix_memalign(&addr_, getpagesize(), size_) != 0) {
            throw std::bad_alloc();
        }

        struct xdp_umem_reg mr{};
        mr.addr = reinterpret_cast<uint64_t>(addr_);
        mr.len = size_;
        mr.chunk_size = chunk_size_;
        mr.headroom = headroom;
        mr.flags = 0;

        if (::setsockopt(xsk_fd, SOL_XDP, XDP_UMEM_REG, &mr, sizeof(mr)) < 0) {
            ::free(addr_);
            throw std::system_error(errno, std::generic_category(), "setsockopt(XDP_UMEM_REG) failed");
        }
    }

    ~UmemArea() {
        if (addr_) ::free(addr_);
    }

    UmemArea(const UmemArea&) = delete;
    UmemArea& operator=(const UmemArea&) = delete;
    UmemArea(UmemArea&& o) noexcept : addr_(o.addr_), size_(o.size_), chunk_size_(o.chunk_size_) {
        o.addr_ = nullptr;
    }

    [[nodiscard]] void* data() const noexcept { return addr_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] uint32_t chunk_size() const noexcept { return chunk_size_; }

    [[nodiscard]] std::span<uint8_t> get_frame(uint64_t offset) const {
        return std::span<uint8_t>(static_cast<uint8_t*>(addr_) + offset, chunk_size_);
    }
};
