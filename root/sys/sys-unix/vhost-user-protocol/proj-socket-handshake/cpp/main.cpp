#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <array>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/mman.h>

constexpr uint32_t VHOST_USER_SET_MEM_TABLE = 5;
constexpr size_t VHOST_MEMORY_MAX_NREGIONS = 8;
constexpr uint32_t VHOST_USER_VERSION = 0x1;

struct VhostUserMemoryRegion {
    uint64_t guest_phys_addr{0};
    uint64_t memory_size{0};
    uint64_t userspace_addr{0};
    uint64_t mmap_offset{0};
};

struct VhostUserMemory {
    uint32_t nregions{0};
    uint32_t padding{0};
    VhostUserMemoryRegion regions[VHOST_MEMORY_MAX_NREGIONS];
};

struct VhostUserMsg {
    uint32_t request{0};
    uint32_t flags{0};
    uint32_t size{0};
    union {
        uint64_t u64;
        VhostUserMemory memory;
        uint8_t raw[1024];
    } payload;
} __attribute__((packed));

/* RAII обгортка для автоматичного закриття дескриптора */
class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : fd_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }
    void reset(int fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = fd;
    }
};

/* Інкапсуляція відображеної області пам'яті через RAII */
class MappedRegion {
    uint64_t gpa_{0};
    uint64_t size_{0};
    uint64_t qemu_va_{0};
    uint64_t mmap_offset_{0};
    void* mmap_addr_{MAP_FAILED};
    size_t total_mapped_size_{0};

public:
    MappedRegion(uint64_t gpa, uint64_t size, uint64_t qemu_va,
                 uint64_t mmap_offset, int fd)
        : gpa_(gpa), size_(size), qemu_va_(qemu_va), mmap_offset_(mmap_offset) {
        total_mapped_size_ = size + mmap_offset;
        mmap_addr_ = ::mmap(nullptr, total_mapped_size_, PROT_READ | PROT_WRITE,
                            MAP_SHARED, fd, 0);
        if (mmap_addr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap region failed");
        }
    }

    ~MappedRegion() {
        if (mmap_addr_ != MAP_FAILED) {
            ::munmap(mmap_addr_, total_mapped_size_);
        }
    }

    MappedRegion(MappedRegion&& other) noexcept
        : gpa_(other.gpa_), size_(other.size_), qemu_va_(other.qemu_va_),
          mmap_offset_(other.mmap_offset_), mmap_addr_(other.mmap_addr_),
          total_mapped_size_(other.total_mapped_size_) {
        other.mmap_addr_ = MAP_FAILED;
    }

    MappedRegion& operator=(MappedRegion&& other) noexcept {
        if (this != &other) {
            if (mmap_addr_ != MAP_FAILED) ::munmap(mmap_addr_, total_mapped_size_);
            gpa_ = other.gpa_;
            size_ = other.size_;
            qemu_va_ = other.qemu_va_;
            mmap_offset_ = other.mmap_offset_;
            mmap_addr_ = other.mmap_addr_;
            total_mapped_size_ = other.total_mapped_size_;
            other.mmap_addr_ = MAP_FAILED;
        }
        return *this;
    }

    [[nodiscard]] bool contains(uint64_t gpa) const noexcept {
        return gpa >= gpa_ && gpa < (gpa_ + size_);
    }

    [[nodiscard]] std::byte* translate(uint64_t gpa) const noexcept {
        if (!contains(gpa)) return nullptr;
        auto* base = static_cast<std::byte*>(mmap_addr_);
        return base + mmap_offset_ + (gpa - gpa_);
    }

    [[nodiscard]] uint64_t gpa() const noexcept { return gpa_; }
    [[nodiscard]] uint64_t size() const noexcept { return size_; }
};

class VhostUserBackend {
    std::vector<MappedRegion> regions_;

public:
    std::expected<void, std::string> process_mem_table(
        const VhostUserMemory& mem, std::span<const int> fds) {
        if (mem.nregions != fds.size()) {
            return std::unexpected("Кількість регіонів не збігається з кількістю дескрипторів");
        }

        std::vector<MappedRegion> new_regions;
        new_regions.reserve(mem.nregions);

        for (uint32_t i = 0; i < mem.nregions; ++i) {
            const auto& r = mem.regions[i];
            try {
                new_regions.emplace_back(r.guest_phys_addr, r.memory_size,
                                         r.userspace_addr, r.mmap_offset, fds[i]);
            } catch (const std::exception& e) {
                return std::unexpected(std::string("Не вдалося відобразити пам'ять: ") + e.what());
            }
        }

        regions_ = std::move(new_regions);
        return {};
    }

    [[nodiscard]] void* gpa_to_hva(uint64_t gpa) const noexcept {
        for (const auto& r : regions_) {
            if (auto* ptr = r.translate(gpa)) {
                return ptr;
            }
        }
        return nullptr;
    }
};
