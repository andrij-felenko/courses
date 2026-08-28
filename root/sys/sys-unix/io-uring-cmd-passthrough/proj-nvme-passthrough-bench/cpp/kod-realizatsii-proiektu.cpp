#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <liburing.h>
#include <linux/nvme_ioctl.h>

namespace nvme_uring {

// RAII обгортка для файлового дескриптора символьного пристрою
class NvmeDevice {
    int fd_{-1};
public:
    explicit NvmeDevice(const char* path) {
        fd_ = ::open(path, O_RDWR);
    }
    ~NvmeDevice() {
        if (fd_ >= 0) ::close(fd_);
    }
    NvmeDevice(const NvmeDevice&) = delete;
    NvmeDevice& operator=(const NvmeDevice&) = delete;
    NvmeDevice(NvmeDevice&& o) noexcept : fd_{o.fd_} { o.fd_ = -1; }

    [[nodiscard]] int fd() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для кільця io_uring
class UringContext {
    struct io_uring ring_{};
    bool active_{false};
public:
    explicit UringContext(unsigned entries) {
        // NVMe passthrough: nvme_uring_cmd займає 72 байти, тож кільце мусить
        // бути створене зі 128-байтовими SQE (IORING_SETUP_SQE128), інакше
        // команда просто не вміститься у 16 байт sqe->cmd звичайного SQE.
        struct io_uring_params params{};
        params.flags = IORING_SETUP_SQE128 | IORING_SETUP_CQE32;
        if (::io_uring_queue_init_params(entries, &ring_, &params) == 0) {
            active_ = true;
        }
    }
    ~UringContext() {
        if (active_) ::io_uring_queue_exit(&ring_);
    }
    UringContext(const UringContext&) = delete;
    UringContext& operator=(const UringContext&) = delete;

    [[nodiscard]] struct io_uring* ring() noexcept { return &ring_; }
    [[nodiscard]] bool valid() const noexcept { return active_; }
};

// RAII буфер з вирівнюванням пам'яті під DMA
class DmaBuffer {
    void* ptr_{nullptr};
    std::size_t size_{0};
public:
    DmaBuffer(std::size_t alignment, std::size_t size) : size_{size} {
        if (::posix_memalign(&ptr_, alignment, size_) != 0) {
            ptr_ = nullptr;
        }
    }
    ~DmaBuffer() {
        if (ptr_) ::free(ptr_);
    }
    DmaBuffer(const DmaBuffer&) = delete;
    DmaBuffer& operator=(const DmaBuffer&) = delete;

    [[nodiscard]] std::span<std::byte> as_bytes() noexcept {
        return {reinterpret_cast<std::byte*>(ptr_), size_};
    }
    [[nodiscard]] void* raw() const noexcept { return ptr_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] bool valid() const noexcept { return ptr_ != nullptr; }
};

// Асинхронна функція відправлення команди NVMe Read
std::expected<std::size_t, std::error_code> read_nvme_block(
    NvmeDevice& dev,
    UringContext& ring_ctx,
    DmaBuffer& buf,
    std::uint64_t lba
) {
    if (!dev.valid() || !ring_ctx.valid() || !buf.valid()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    struct io_uring_sqe* sqe = ::io_uring_get_sqe(ring_ctx.ring());
    if (!sqe) {
        return std::unexpected(std::make_error_code(std::errc::resource_unavailable_try_again));
    }

    ::io_uring_prep_rw(IORING_OP_URING_CMD, sqe, dev.fd(), nullptr, 0, 0);
    sqe->cmd_op = NVME_URING_CMD_IO;

    auto* cmd = reinterpret_cast<struct nvme_uring_cmd*>(sqe->cmd);
    std::memset(cmd, 0, sizeof(*cmd));
    cmd->opcode = 0x02; // NVMe Read opcode
    cmd->nsid = 1;      // Namespace ID 1
    cmd->addr = reinterpret_cast<__u64>(buf.raw());
    cmd->data_len = static_cast<__u32>(buf.size());
    cmd->cdw10 = static_cast<__u32>(lba & 0xFFFFFFFF);
    cmd->cdw11 = static_cast<__u32>(lba >> 32);
    cmd->cdw12 = 0;     // 1 LBA (0-based значення)

    sqe->user_data = 0x100;

    int ret = ::io_uring_submit(ring_ctx.ring());
    if (ret < 0) {
        return std::unexpected(std::error_code(-ret, std::generic_category()));
    }

    struct io_uring_cqe* cqe{nullptr};
    ret = ::io_uring_wait_cqe(ring_ctx.ring(), &cqe);
    if (ret < 0) {
        return std::unexpected(std::error_code(-ret, std::generic_category()));
    }

    int res = cqe->res;
    ::io_uring_cqe_seen(ring_ctx.ring(), cqe);

    if (res < 0) {
        return std::unexpected(std::error_code(-res, std::generic_category()));
    }

    return buf.size();
}

} // namespace nvme_uring

int main(int argc, char* argv[]) {
    const char* dev_path = (argc > 1) ? argv[1] : "/dev/ng0n1";
    nvme_uring::NvmeDevice dev{dev_path};
    nvme_uring::UringContext ring{32};
    nvme_uring::DmaBuffer buffer{4096, 4096};

    auto result = nvme_uring::read_nvme_block(dev, ring, buffer, 0);
    if (result) {
        std::cout << "C++20 NVMe Read успішно виконано! Прочитано " << *result << " байт.\n";
    } else {
        std::cerr << "NVMe Read завершився з помилкою: " << result.error().message() << "\n";
        return 1;
    }

    return 0;
}
