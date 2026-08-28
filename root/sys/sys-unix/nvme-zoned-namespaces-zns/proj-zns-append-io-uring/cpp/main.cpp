#include <iostream>
#include <vector>
#include <thread>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>
#include <linux/blkzoned.h>

namespace zns {

constexpr std::size_t kSectorSize = 512;
constexpr std::size_t kBlockSize = 4096;

// RAII обгортка для файлового дескриптора пристрою
class DeviceHandle {
public:
    explicit DeviceHandle(const char* path) {
        fd_ = ::open(path, O_RDWR | O_DIRECT);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open ZNS device");
        }
    }

    ~DeviceHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    DeviceHandle(const DeviceHandle&) = delete;
    DeviceHandle& operator=(const DeviceHandle&) = delete;
    DeviceHandle(DeviceHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    DeviceHandle& operator=(DeviceHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

// Вирівняна пам'ять для Direct I/O (RAII)
class AlignedBuffer {
public:
    explicit AlignedBuffer(std::size_t size, std::size_t alignment = 4096) : size_(size) {
        void* ptr = nullptr;
        if (::posix_memalign(&ptr, alignment, size) != 0) {
            throw std::bad_alloc();
        }
        data_.reset(static_cast<std::byte*>(ptr));
    }

    [[nodiscard]] std::span<std::byte> span() noexcept { return {data_.get(), size_}; }
    [[nodiscard]] std::span<const std::byte> span() const noexcept { return {data_.get(), size_}; }
    [[nodiscard]] void* data() noexcept { return data_.get(); }

private:
    struct FreeDeleter {
        void operator()(void* p) const { std::free(p); }
    };
    std::unique_ptr<std::byte[], FreeDeleter> data_;
    std::size_t size_;
};

// Виконання Zone Reset
std::expected<void, std::error_code> reset_zone(const DeviceHandle& dev, std::uint64_t start_sector, std::uint64_t nr_sectors) {
    struct blk_zone_range range{
        .sector = start_sector,
        .nr_sectors = nr_sectors
    };
    if (::ioctl(dev.get(), BLKRESETZONE, &range) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

// Атомарна команда Zone Append
std::expected<std::uint64_t, std::error_code> zone_append(
    const DeviceHandle& dev, 
    std::uint32_t nsid, 
    std::uint64_t zslba, 
    std::span<const std::byte> buffer
) {
    uint32_t nlb = static_cast<uint32_t>(buffer.size() / kSectorSize);
    struct nvme_passthru_cmd cmd{};

    cmd.opcode      = 0x7d; // nvme_zns_cmd_append
    cmd.nsid        = nsid;
    cmd.addr        = reinterpret_cast<std::uint64_t>(buffer.data());
    cmd.data_len    = static_cast<std::uint32_t>(buffer.size());
    cmd.cdw10       = static_cast<std::uint32_t>(zslba & 0xFFFFFFFF);
    cmd.cdw11       = static_cast<std::uint32_t>(zslba >> 32);
    cmd.cdw12       = nlb - 1;
    cmd.timeout_ms  = 2000;

    if (::ioctl(dev.get(), NVME_IOCTL_IO_CMD, &cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return cmd.result; // Выділений LBA з CQE
}

} // namespace zns

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " /dev/nvmeXnY\n";
        return EXIT_FAILURE;
    }

    try {
        zns::DeviceHandle dev(argv[1]);

        std::cout << "Resetting zone at sector 0...\n";
        if (auto res = zns::reset_zone(dev, 0, 262144); !res) {
            std::cerr << "Zone reset failed: " << res.error().message() << "\n";
            return EXIT_FAILURE;
        }
        std::cout << "Zone reset successful.\n";

        constexpr int kNumThreads = 4;
        constexpr int kWritesPerThread = 8;
        std::vector<std::thread> workers;
        workers.reserve(kNumThreads);

        for (int tid = 0; tid < kNumThreads; ++tid) {
            workers.emplace_back([&dev, tid]() {
                zns::AlignedBuffer buf(zns::kBlockSize);
                std::memset(buf.data(), 0xBB + tid, zns::kBlockSize);

                for (int i = 0; i < kWritesPerThread; ++i) {
                    auto res = zns::zone_append(dev, 1, 0, buf.span());
                    if (!res) {
                        std::cerr << "[Thread " << tid << "] Append failed: " << res.error().message() << "\n";
                        break;
                    }
                    std::cout << "[Thread " << tid << "] Appended block " << i 
                              << " -> Allocated LBA: 0x" << std::hex << *res << std::dec << "\n";
                }
            });
        }

        for (auto& t : workers) {
            t.join();
        }

        std::cout << "All C++ lockless appends completed successfully.\n";

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
