// cpp — ідіоматична реалізація мовою C++20 з використанням RAII, std::span та std::expected
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <system_error>
#include <cstdlib>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

namespace nvmeof {

// RAII обгортка для файлового дескриптора
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) : fd_(fd) {}
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

// Делегат вирівняного виділення пам'яті для Direct I/O
struct PageAlignedDeleter {
    void operator()(void* ptr) const noexcept {
        ::free(ptr);
    }
};

template <typename T>
using PageAlignedBuffer = std::unique_ptr<T[], PageAlignedDeleter>;

template <typename T>
[[nodiscard]] PageAlignedBuffer<T> allocate_aligned_buffer(size_t count, size_t alignment = 4096) {
    void* ptr = nullptr;
    size_t total_bytes = count * sizeof(T);
    if (::posix_memalign(&ptr, alignment, total_bytes) != 0) {
        throw std::bad_alloc();
    }
    return PageAlignedBuffer<T>(static_cast<T*>(ptr));
}

// Клієнт управління NVMe-oF
class NvmeOfClient {
    static constexpr std::string_view FabricsDevice = "/dev/nvme-fabrics";
public:
    // Підключення до віддаленої підсистеми NVMe-oF
    [[nodiscard]] static std::expected<void, std::error_code> connect(
        std::string_view nqn,
        std::string_view traddr,
        std::string_view trsvcid = "4420",
        std::string_view transport = "tcp") 
    {
        UniqueFd fd(::open(FabricsDevice.data(), O_RDWR));
        if (!fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::string options = std::string("nqn=") + std::string(nqn) +
                              ",transport=" + std::string(transport) +
                              ",traddr=" + std::string(traddr) +
                              ",trsvcid=" + std::string(trsvcid);

        ssize_t ret = ::write(fd.get(), options.data(), options.size());
        if (ret < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

    // Виконання прямого читання логічних блоків LBA
    [[nodiscard]] static std::expected<void, std::error_code> read_lba(
        std::string_view dev_path,
        uint64_t lba,
        std::span<std::byte> buffer) 
    {
        UniqueFd fd(::open(dev_path.data(), O_RDWR | O_DIRECT));
        if (!fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        nvme_user_io io_cmd{};
        io_cmd.opcode = 0x02; // NVMe Read
        io_cmd.addr = reinterpret_cast<uint64_t>(buffer.data());
        io_cmd.slba = lba;
        io_cmd.nblocks = static_cast<uint16_t>((buffer.size() / 512) - 1);

        int ret = ::ioctl(fd.get(), NVME_IOCTL_SUBMIT_IO, &io_cmd);
        if (ret < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }
};

} // namespace nvmeof

int main() {
    std::cout << "[C++20 Client] Підключення до віддаленої підсистеми NVMe-oF...\n";

    constexpr std::string_view target_nqn = "nqn.2024-08.com.example:nvme.target1";
    constexpr std::string_view target_ip = "192.168.1.100";

    auto conn_res = nvmeof::NvmeOfClient::connect(target_nqn, target_ip);
    if (!conn_res) {
        std::cerr << "Помилка підключення: " << conn_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[C++20 Client] Успішно підключено. Читання сектора...\n";

    constexpr size_t buffer_size = 4096;
    auto aligned_buf = nvmeof::allocate_aligned_buffer<std::byte>(buffer_size);
    std::span<std::byte> buf_span(aligned_buf.get(), buffer_size);

    auto read_res = nvmeof::NvmeOfClient::read_lba("/dev/nvme0n1", 0, buf_span);
    if (!read_res) {
        std::cerr << "Помилка читання LBA: " << read_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[C++20 Client] Блок успішно прочитано у RAII буфер!\n";
    return EXIT_SUCCESS;
}
