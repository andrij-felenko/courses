// incfs_daemon.cpp — Ідіоматична реалізація демона IncFS мовою C++20 (RAII, span, expected)
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <format>
#include <system_error>
#include <filesystem>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <cstdint>

namespace fs = std::filesystem;

// RAII-обгортка для автоматичного закриття файлового дескриптора POSIX
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

constexpr uint32_t kBlockSize = 4096;
constexpr uint8_t kIncfsIoctlBase = 0x67;

struct alignas(8) PendingReadInfo {
    uint64_t file_id_low;
    uint64_t file_id_high;
    uint32_t timestamp_us;
    uint32_t block_index;
};

struct IncfsFillBlock {
    uint32_t block_index;
    uint32_t data_len;
    uint64_t data;
    uint8_t  compression{0};
    uint8_t  flags{0};
    uint16_t reserved{0};
};

struct IncfsFillBlocks {
    uint64_t count;
    uint64_t fill_blocks;
};

#define INCFS_IOC_FILL_BLOCKS _IOW(kIncfsIoctlBase, 2, IncfsFillBlocks)

class IncfsDaemon {
    UniqueFd pending_fd_;
    UniqueFd dir_fd_;

public:
    static std::expected<IncfsDaemon, std::error_code> create(const fs::path& incfs_root) {
        const auto pending_path = incfs_root / ".pending_reads";
        
        int pfd = ::open(pending_path.c_str(), O_RDONLY | O_CLOEXEC);
        if (pfd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int dfd = ::open(incfs_root.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
        if (dfd < 0) {
            ::close(pfd);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return IncfsDaemon(UniqueFd(pfd), UniqueFd(dfd));
    }

    std::expected<void, std::error_code> fill_block(const PendingReadInfo& req, std::span<const uint8_t> data) {
        // Заповнення подають на дескриптор самого файлу: IncfsFillBlock не містить File ID.
        // Тому файл відкриваємо за його ідентифікатором у каталозі .index.
        const auto id_path = std::format(".index/{:016x}{:016x}", req.file_id_high, req.file_id_low);
        UniqueFd file_fd{::openat(dir_fd_.get(), id_path.c_str(), O_RDWR | O_CLOEXEC)};
        if (!file_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        const uint32_t block_index = req.block_index;
        IncfsFillBlock fb{
            .block_index = block_index,
            .data_len = static_cast<uint32_t>(data.size()),
            .data = reinterpret_cast<uint64_t>(data.data())
        };

        IncfsFillBlocks fbs{
            .count = 1,
            .fill_blocks = reinterpret_cast<uint64_t>(&fb)
        };

        if (::ioctl(file_fd.get(), INCFS_IOC_FILL_BLOCKS, &fbs) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::cout << "[IncFS Daemon C++] Успішно заповнено блок " << block_index 
                  << " (" << data.size() << " байт)\n";
        return {};
    }

    void run_event_loop() {
        std::cout << "[IncFS Daemon C++] Цикл подій запущено...\n";
        
        std::vector<uint8_t> dummy_payload(kBlockSize, 'B');
        pollfd pfd{.fd = pending_fd_.get(), .events = POLLIN, .revents = 0};

        while (true) {
            int ret = ::poll(&pfd, 1, 5000); // 5 сек таймаут
            if (ret < 0) {
                if (errno == EINTR) continue;
                std::cerr << "[IncFS Daemon C++] Помилка poll(): " 
                          << std::generic_category().message(errno) << '\n';
                break;
            } else if (ret == 0) {
                std::cout << "[IncFS Daemon C++] Таймаут очікування подій...\n";
                continue;
            }

            if (pfd.revents & POLLIN) {
                PendingReadInfo req{};
                ssize_t nread = ::read(pending_fd_.get(), &req, sizeof(req));
                if (nread == sizeof(req)) {
                    std::cout << "[IncFS Daemon C++] Запит блоку: Index=" << req.block_index 
                              << ", Timestamp=" << req.timestamp_us << "us\n";

                    if (auto res = fill_block(req, dummy_payload); !res) {
                        std::cerr << "[IncFS Daemon C++] Не вдалося заповнити блок: " 
                                  << res.error().message() << '\n';
                    }
                }
            }
        }
    }

private:
    IncfsDaemon(UniqueFd pfd, UniqueFd dfd) 
        : pending_fd_(std::move(pfd)), dir_fd_(std::move(dfd)) {}
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_кореню_incfs>\n";
        return EXIT_FAILURE;
    }

    auto daemon_res = IncfsDaemon::create(argv[1]);
    if (!daemon_res) {
        std::cerr << "Не вдалося ініціалізувати демон: " 
                  << daemon_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    daemon_res->run_event_loop();
    return EXIT_SUCCESS;
}
