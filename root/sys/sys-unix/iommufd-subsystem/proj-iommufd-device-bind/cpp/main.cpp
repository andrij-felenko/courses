#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <system_error>
#include <expected>
#include <format>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/vfio.h>
#include <linux/iommufd.h>

namespace iommufd {

// RAII обгортка для безпечного володіння дескриптором Linux
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// RAII буфер пам'яті, вирівняний по межі сторінки для прямого DMA
class AlignedDmaBuffer {
    void* data_{nullptr};
    size_t size_{0};
public:
    AlignedDmaBuffer(size_t size, size_t alignment = 4096) : size_(size) {
        void* ptr = nullptr;
        int res = ::posix_memalign(&ptr, alignment, size);
        if (res != 0 || !ptr) {
            throw std::system_error(res, std::generic_category(), "Не вдалося виділити DMA буфер");
        }
        data_ = ptr;
        std::memset(data_, 0, size_);
    }

    ~AlignedDmaBuffer() {
        if (data_) {
            ::free(data_);
        }
    }

    AlignedDmaBuffer(const AlignedDmaBuffer&) = delete;
    AlignedDmaBuffer& operator=(const AlignedDmaBuffer&) = delete;
    AlignedDmaBuffer(AlignedDmaBuffer&& other) noexcept 
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    [[nodiscard]] void* data() const noexcept { return data_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] std::span<std::byte> as_span() noexcept {
        return {static_cast<std::byte*>(data_), size_};
    }
};

// Клас контексту IOMMUFD
class IommuContext {
    UniqueFd fd_;
public:
    static std::expected<IommuContext, std::error_code> open() noexcept {
        int fd = ::open("/dev/iommufd", O_RDWR | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return IommuContext(UniqueFd(fd));
    }

    explicit IommuContext(UniqueFd fd) noexcept : fd_(std::move(fd)) {}

    [[nodiscard]] int native_handle() const noexcept { return fd_.get(); }

    std::expected<uint32_t, std::error_code> allocate_ioas() noexcept {
        struct iommu_ioas_alloc cmd = {
            .size = sizeof(cmd),
            .flags = 0,
            .out_ioas_id = 0,
        };
        if (::ioctl(fd_.get(), IOMMU_IOAS_ALLOC, &cmd) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return cmd.out_ioas_id;
    }

    std::expected<uint64_t, std::error_code> map_dma(
        uint32_t ioas_id, uint64_t target_iova, const AlignedDmaBuffer& buffer) noexcept {
        struct iommu_ioas_map cmd = {
            .size = sizeof(cmd),
            .flags = IOMMU_IOAS_MAP_FIXED_IOVA | IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE,
            .ioas_id = ioas_id,
            .__reserved = 0,
            .user_va = reinterpret_cast<uint64_t>(buffer.data()),
            .length = buffer.size(),
            .iova = target_iova,
        };
        if (::ioctl(fd_.get(), IOMMU_IOAS_MAP, &cmd) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return cmd.iova;
    }

    std::error_code unmap_dma(uint32_t ioas_id, uint64_t iova, size_t length) noexcept {
        struct iommu_ioas_unmap cmd = {
            .size = sizeof(cmd),
            .ioas_id = ioas_id,
            .iova = iova,
            .length = length,
        };
        if (::ioctl(fd_.get(), IOMMU_IOAS_UNMAP, &cmd) < 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }
};

// Клас прив'язаного пристрою VFIO
class VfioDevice {
    UniqueFd fd_;
    uint32_t dev_id_{0};
public:
    static std::expected<VfioDevice, std::error_code> open_and_bind(
        std::string_view dev_path, const IommuContext& ctx) noexcept {
        int dev_fd = ::open(dev_path.data(), O_RDWR | O_CLOEXEC);
        if (dev_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct vfio_device_bind_iommufd bind_cmd = {
            .argsz = sizeof(bind_cmd),
            .flags = 0,
            .iommufd = ctx.native_handle(),
            .dev_id = 0,
        };
        if (::ioctl(dev_fd, VFIO_DEVICE_BIND_IOMMUFD, &bind_cmd) < 0) {
            ::close(dev_fd);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return VfioDevice(UniqueFd(dev_fd), bind_cmd.dev_id);
    }

    VfioDevice(UniqueFd fd, uint32_t dev_id) noexcept 
        : fd_(std::move(fd)), dev_id_(dev_id) {}

    [[nodiscard]] uint32_t dev_id() const noexcept { return dev_id_; }

    std::error_code attach_ioas(uint32_t ioas_id) noexcept {
        struct vfio_device_attach_iommufd_pt attach_cmd = {
            .argsz = sizeof(attach_cmd),
            .flags = 0,
            .pt_id = ioas_id,
        };
        if (::ioctl(fd_.get(), VFIO_DEVICE_ATTACH_IOMMUFD_PT, &attach_cmd) < 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }

    std::error_code detach_ioas() noexcept {
        struct vfio_device_detach_iommufd_pt detach_cmd = {
            .argsz = sizeof(detach_cmd),
            .flags = 0,
        };
        if (::ioctl(fd_.get(), VFIO_DEVICE_DETACH_IOMMUFD_PT, &detach_cmd) < 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }
};

} // namespace iommufd

int main(int argc, char* argv[]) {
    const std::string_view dev_path = (argc > 1) ? argv[1] : "/dev/vfio/devices/0000:01:00.0";
    constexpr size_t BUFFER_SIZE = 2 * 1024 * 1024; // 2 MB
    constexpr uint64_t TARGET_IOVA = 0x10000000;

    auto ctx_res = iommufd::IommuContext::open();
    if (!ctx_res) {
        std::cerr << std::format("Помилка відкриття /dev/iommufd: {}\n", ctx_res.error().message());
        return 1;
    }
    auto& ctx = *ctx_res;

    std::cout << std::format("Відкриття та прив'язка пристрою {}...\n", dev_path);
    auto dev_res = iommufd::VfioDevice::open_and_bind(dev_path, ctx);
    if (!dev_res) {
        std::cerr << std::format("Помилка прив'язки VFIO пристрою: {}\n", dev_res.error().message());
        return 1;
    }
    auto& dev = *dev_res;
    std::cout << std::format("-> Отримано dev_id: {}\n", dev.dev_id());

    auto ioas_res = ctx.allocate_ioas();
    if (!ioas_res) {
        std::cerr << std::format("Помилка виділення IOAS: {}\n", ioas_res.error().message());
        return 1;
    }
    uint32_t ioas_id = *ioas_res;
    std::cout << std::format("-> Створено IOAS: {}\n", ioas_id);

    iommufd::AlignedDmaBuffer buffer(BUFFER_SIZE);
    auto map_res = ctx.map_dma(ioas_id, TARGET_IOVA, buffer);
    if (!map_res) {
        std::cerr << std::format("Помилка відображення пам'яті DMA: {}\n", map_res.error().message());
        return 1;
    }
    std::cout << std::format("-> Відображено IOVA 0x{:X} (розмір {} байтів)\n", *map_res, BUFFER_SIZE);

    auto attach_err = dev.attach_ioas(ioas_id);
    if (attach_err) {
        std::cerr << std::format("Помилка підключення пристрою до IOAS: {}\n", attach_err.message());
        return 1;
    }
    std::cout << "-> Пристрій успішно підключено до апаратного домену IOMMU!\n";

    // Акуратне відключення
    dev.detach_ioas();
    ctx.unmap_dma(ioas_id, TARGET_IOVA, BUFFER_SIZE);
    std::cout << "-> Очищення ресурсів виконано штатно.\n";

    return 0;
}
