#include <iostream>
#include <memory>
#include <cstring>
#include <cstdlib>
#include <utility>
#include <string>
#include <string_view>
#include <span>
#include <system_error>
#include <expected>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/eventfd.h>
#include <linux/vfio.h>

namespace vfio {

// RAII обгортка для файлових дескрипторів POSIX
class FileDescriptor {
    int fd_{-1};
public:
    constexpr FileDescriptor() noexcept = default;
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
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
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// RAII обгортка для MMIO відображень через mmap
class MmioRegion {
    void* addr_{MAP_FAILED};
    size_t size_{0};
public:
    MmioRegion() noexcept = default;
    MmioRegion(void* addr, size_t size) noexcept : addr_(addr), size_(size) {}
    ~MmioRegion() {
        if (addr_ != MAP_FAILED && size_ > 0) {
            ::munmap(addr_, size_);
        }
    }

    MmioRegion(const MmioRegion&) = delete;
    MmioRegion& operator=(const MmioRegion&) = delete;

    MmioRegion(MmioRegion&& other) noexcept
        : addr_(other.addr_), size_(other.size_) {
        other.addr_ = MAP_FAILED;
        other.size_ = 0;
    }

    [[nodiscard]] bool valid() const noexcept { return addr_ != MAP_FAILED; }
    [[nodiscard]] std::span<volatile uint32_t> as_uint32_span() const noexcept {
        return { static_cast<volatile uint32_t*>(addr_), size_ / sizeof(uint32_t) };
    }
};

class VfioDevice {
    FileDescriptor container_fd_;
    FileDescriptor group_fd_;
    FileDescriptor device_fd_;
    void* dma_buffer_{nullptr};
    size_t dma_size_{0};
    uint64_t iova_base_{0};

public:
    VfioDevice() noexcept = default;
    VfioDevice(const VfioDevice&) = delete;
    VfioDevice& operator=(const VfioDevice&) = delete;
    VfioDevice(VfioDevice&& other) noexcept
        : container_fd_(std::move(other.container_fd_)),
          group_fd_(std::move(other.group_fd_)),
          device_fd_(std::move(other.device_fd_)),
          dma_buffer_(std::exchange(other.dma_buffer_, nullptr)),
          dma_size_(other.dma_size_),
          iova_base_(other.iova_base_) {}

    static std::expected<VfioDevice, std::error_code> create(
        std::string_view group_id, std::string_view pci_bdf, size_t dma_size) {
        
        // 1. Налаштовуємо ліміти MEMLOCK
        struct rlimit rlim{RLIM_INFINITY, RLIM_INFINITY};
        if (::setrlimit(RLIMIT_MEMLOCK, &rlim) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 2. Відкриваємо контейнер
        FileDescriptor container{::open("/dev/vfio/vfio", O_RDWR)};
        if (!container.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(container.get(), VFIO_GET_API_VERSION) != VFIO_API_VERSION ||
            !::ioctl(container.get(), VFIO_CHECK_EXTENSION, VFIO_TYPE1_IOMMU)) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        // 3. Відкриваємо групу
        std::string group_path = "/dev/vfio/" + std::string(group_id);
        FileDescriptor group{::open(group_path.c_str(), O_RDWR)};
        if (!group.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct vfio_group_status status{.argsz = sizeof(status)};
        if (::ioctl(group.get(), VFIO_GROUP_GET_STATUS, &status) < 0 ||
            !(status.flags & VFIO_GROUP_FLAGS_VIABLE)) {
            return std::unexpected(std::make_error_code(std::errc::device_or_resource_busy));
        }

        int raw_container_fd = container.get();
        if (::ioctl(group.get(), VFIO_GROUP_SET_CONTAINER, &raw_container_fd) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(container.get(), VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 4. Отримуємо пристрій
        FileDescriptor device{::ioctl(group.get(), VFIO_GROUP_GET_DEVICE_FD, pci_bdf.data())};
        if (!device.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        VfioDevice dev;
        dev.container_fd_ = std::move(container);
        dev.group_fd_ = std::move(group);
        dev.device_fd_ = std::move(device);
        dev.dma_size_ = dma_size;

        return dev;
    }

    ~VfioDevice() {
        if (dma_buffer_ && container_fd_.valid()) {
            struct vfio_iommu_type1_dma_unmap unmap{.argsz = sizeof(unmap), .flags = 0, .iova = iova_base_, .size = dma_size_};
            ::ioctl(container_fd_.get(), VFIO_IOMMU_UNMAP_DMA, &unmap);
            ::free(dma_buffer_);
        }
    }

    std::expected<uint64_t, std::error_code> map_dma_buffer(uint64_t iova) {
        void* buf = nullptr;
        if (::posix_memalign(&buf, ::sysconf(_SC_PAGESIZE), dma_size_) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        std::memset(buf, 0, dma_size_);

        struct vfio_iommu_type1_dma_map dma_map{
            .argsz = sizeof(dma_map),
            .flags = VFIO_DMA_MAP_FLAG_READ | VFIO_DMA_MAP_FLAG_WRITE,
            .vaddr = reinterpret_cast<uint64_t>(buf),
            .iova = iova,
            .size = dma_size_
        };

        if (::ioctl(container_fd_.get(), VFIO_IOMMU_MAP_DMA, &dma_map) < 0) {
            ::free(buf);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        dma_buffer_ = buf;
        iova_base_ = iova;
        return iova;
    }

    std::expected<MmioRegion, std::error_code> map_bar(uint32_t bar_index) {
        struct vfio_region_info reg_info{.argsz = sizeof(reg_info), .index = bar_index};
        if (::ioctl(device_fd_.get(), VFIO_DEVICE_GET_REGION_INFO, &reg_info) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        void* addr = ::mmap(nullptr, reg_info.size, PROT_READ | PROT_WRITE, MAP_SHARED, device_fd_.get(), reg_info.offset);
        if (addr == MAP_FAILED) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return MmioRegion{addr, reg_info.size};
    }
};

} // namespace vfio

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <group_id> <pci_bdf>\n";
        return EXIT_FAILURE;
    }

    auto dev_result = vfio::VfioDevice::create(argv[1], argv[2], 2 * 1024 * 1024);
    if (!dev_result) {
        std::cerr << "Помилка ініціалізації VFIO: " << dev_result.error().message() << "\n";
        return EXIT_FAILURE;
    }

    auto& dev = *dev_result;
    auto dma_res = dev.map_dma_buffer(0x10000000);
    if (dma_res) {
        std::cout << "DMA буфер зареєстровано за IOVA 0x" << std::hex << *dma_res << std::dec << "\n";
    }

    auto bar0_res = dev.map_bar(VFIO_PCI_BAR0_REGION_INDEX);
    if (bar0_res && bar0_res->valid()) {
        auto regs = bar0_res->as_uint32_span();
        std::cout << "BAR0 відображено. Кількість 32-бітних регістрів: " << regs.size() << "\n";
        if (!regs.empty()) {
            std::cout << "Значення BAR0[0]: 0x" << std::hex << regs[0] << std::dec << "\n";
        }
    }

    return EXIT_SUCCESS;
}
