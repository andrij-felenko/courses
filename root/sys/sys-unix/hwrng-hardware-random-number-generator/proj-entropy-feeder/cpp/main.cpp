#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <numeric>
#include <bit>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/random.h>

class PosixFd {
    int m_fd{-1};
public:
    explicit PosixFd(int fd) noexcept : m_fd(fd) {}
    ~PosixFd() { if (m_fd >= 0) ::close(m_fd); }
    
    PosixFd(const PosixFd&) = delete;
    PosixFd& operator=(const PosixFd&) = delete;
    
    PosixFd(PosixFd&& other) noexcept : m_fd(other.m_fd) { other.m_fd = -1; }
    PosixFd& operator=(PosixFd&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

enum class FeederError {
    OpenFailed,
    ReadFailed,
    FipsTestFailed,
    IoctlFailed
};

constexpr size_t BlockBytes = 2500;
constexpr size_t BlockBits = BlockBytes * 8;
constexpr size_t MonobitMin = 9725;
constexpr size_t MonobitMax = 10275;

[[nodiscard]] bool verify_monobit(std::span<const uint8_t> data) noexcept {
    size_t ones = 0;
    for (uint8_t byte : data) {
        ones += std::popcount(byte);
    }
    return ones >= MonobitMin && ones <= MonobitMax;
}

std::expected<void, FeederError> feed_entropy() {
    PosixFd hwrng{::open("/dev/hwrng", O_RDONLY)};
    if (!hwrng.valid()) return std::unexpected(FeederError::OpenFailed);

    PosixFd random_dev{::open("/dev/random", O_WRONLY)};
    if (!random_dev.valid()) return std::unexpected(FeederError::OpenFailed);

    std::vector<uint8_t> buffer(BlockBytes);
    size_t total_read = 0;
    while (total_read < BlockBytes) {
        ssize_t bytes = ::read(hwrng.get(), buffer.data() + total_read, BlockBytes - total_read);
        if (bytes <= 0) {
            return std::unexpected(FeederError::ReadFailed);
        }
        total_read += static_cast<size_t>(bytes);
    }

    if (!verify_monobit(buffer)) {
        return std::unexpected(FeederError::FipsTestFailed);
    }

    size_t info_size = sizeof(struct rand_pool_info) + buffer.size();
    auto storage = std::make_unique<uint8_t[]>(info_size);
    auto* info = reinterpret_cast<struct rand_pool_info*>(storage.get());

    info->entropy_count = static_cast<int>(BlockBits);
    info->buf_size = static_cast<int>(buffer.size());
    std::copy(buffer.begin(), buffer.end(), reinterpret_cast<uint8_t*>(info->buf));

    if (::ioctl(random_dev.get(), RNDADDENTROPY, info) < 0) {
        return std::unexpected(FeederError::IoctlFailed);
    }

    return {};
}

int main() {
    auto result = feed_entropy();
    if (!result) {
        std::cerr << "Помилка передачі ентропії у ядро Linux!\n";
        return EXIT_FAILURE;
    }

    std::cout << "Успішно перевірено та додано " << BlockBits << " біт ентропії.\n";
    return EXIT_SUCCESS;
}
