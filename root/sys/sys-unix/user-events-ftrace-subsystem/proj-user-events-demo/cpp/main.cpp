#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>
#include <csignal>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/uio.h>
#include <system_error>

#ifndef DIAG_IOCSREG
#define DIAG_IOC_MAGIC 0x82
#define DIAG_IOCSREG _IOWR(DIAG_IOC_MAGIC, 0, struct user_reg)
#endif

struct user_reg {
    std::uint32_t size;
    std::uint8_t  enable_bit;
    std::uint8_t  enable_size;
    std::uint16_t flags;
    std::uint64_t name_args;
    std::uint32_t status_index;
    std::uint32_t write_index;
};

constexpr std::uint32_t make_user_event_loc(std::uint16_t offset, std::uint16_t len) noexcept {
    return (static_cast<std::uint32_t>(len) << 16) | (static_cast<std::uint32_t>(offset) & 0xFFFF);
}

namespace {
    volatile std::sig_atomic_t g_stop_requested = 0;
}

class UserEventsHandle {
    int fd_{-1};
    char* status_map_{static_cast<char*>(MAP_FAILED)};
    std::size_t map_size_{0};
    user_reg reg_{};

public:
    explicit UserEventsHandle(std::string_view event_spec) {
        const char* dev_path = "/sys/kernel/tracing/user_events_data";
        fd_ = ::open(dev_path, O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити user_events_data");
        }

        reg_.size = sizeof(reg_);
        reg_.name_args = reinterpret_cast<std::uint64_t>(event_spec.data());

        if (::ioctl(fd_, DIAG_IOCSREG, &reg_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "ioctl(DIAG_IOCSREG) failed");
        }

        map_size_ = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
        void* ptr = ::mmap(nullptr, map_size_, PROT_READ, MAP_SHARED, fd_, 0);
        if (ptr == MAP_FAILED) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "mmap status page failed");
        }
        status_map_ = static_cast<char*>(ptr);
    }

    ~UserEventsHandle() noexcept {
        if (status_map_ != MAP_FAILED) {
            ::munmap(status_map_, map_size_);
        }
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    UserEventsHandle(const UserEventsHandle&) = delete;
    UserEventsHandle& operator=(const UserEventsHandle&) = delete;

    [[nodiscard]] bool is_enabled() const noexcept {
        return status_map_[reg_.status_index] != 0;
    }

    [[nodiscard]] std::uint32_t write_index() const noexcept {
        return reg_.write_index;
    }

    [[nodiscard]] std::uint32_t status_index() const noexcept {
        return reg_.status_index;
    }

    bool trace_http_request(std::uint32_t status_code, std::uint64_t latency_ns, std::string_view url) {
        if (!is_enabled()) {
            return false;
        }

        struct alignas(4) FixedPayload {
            std::uint32_t status_code;
            std::uint32_t padding;
            std::uint64_t latency_ns;
            std::uint32_t url_loc;
        } header{};

        std::uint16_t url_len = static_cast<std::uint16_t>(url.size()) + 1;
        header.status_code = status_code;
        header.padding = 0;
        header.latency_ns = latency_ns;
        header.url_loc = make_user_event_loc(sizeof(FixedPayload), url_len);

        std::uint32_t w_idx = reg_.write_index;

        std::array<::iovec, 3> iov{};
        iov[0].iov_base = &w_idx;
        iov[0].iov_len = sizeof(w_idx);

        iov[1].iov_base = &header;
        iov[1].iov_len = sizeof(header);

        iov[2].iov_base = const_cast<char*>(url.data());
        iov[2].iov_len = url_len;

        ssize_t written = ::writev(fd_, iov.data(), iov.size());
        return written > 0;
    }
};

int main() {
    std::signal(SIGINT, [](int) { g_stop_requested = 1; });
    std::signal(SIGTERM, [](int) { g_stop_requested = 1; });

    try {
        constexpr std::string_view spec = "app_http_request u32 status_code; u64 latency_ns; __data_loc char[] url";
        UserEventsHandle tracer(spec);

        std::cout << "[C++] Подію успішно зареєстровано!\n"
                  << "      write_index  = " << tracer.write_index() << "\n"
                  << "      status_index = " << tracer.status_index() << std::endl;

        std::uint32_t counter = 0;
        while (!g_stop_requested) {
            if (tracer.is_enabled()) {
                bool ok = tracer.trace_http_request(200, 1200000 + counter * 5000, "/api/v2/orders");
                if (ok) {
                    std::cout << "[C++] [ПОДІЯ НАДІСЛАНА] #" << counter << std::endl;
                }
            } else {
                std::cout << "[C++] [ПРОПУСК] Подію вимкнено (Zero-Overhead check)" << std::endl;
            }

            counter++;
            ::sleep(1);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }

    std::cout << "Завершення роботи C++ програми." << std::endl;
    return EXIT_SUCCESS;
}
