// uevent_monitor.cpp — Ідіоматичний монітор uevent на C++23
#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <format>
#include <expected>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <linux/netlink.h>

namespace netlink {

// Безпечна RAII обгортка для володіння файловим дескриптором
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct UeventRecord {
    std::string_view action{"N/A"};
    std::string_view devpath{"N/A"};
    std::string_view subsystem{"N/A"};
    std::string_view devname{};
    std::string_view modalias{};
    std::string_view seqnum{"N/A"};
    std::string_view major{};
    std::string_view minor{};
    std::string_view driver{};
};

class UeventListener {
    UniqueFd socket_;
    static constexpr size_t kBufferSize = 16384;
    static constexpr int kSocketRecvBuffer = 2 * 1024 * 1024;

public:
    static std::expected<UeventListener, std::string> create() {
        int raw_fd = ::socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
        if (raw_fd < 0) {
            return std::unexpected(std::format("Не вдалося створити сокет Netlink: {}", std::strerror(errno)));
        }

        UniqueFd sock(raw_fd);

        int buf_size = kSocketRecvBuffer;
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_pid = 0;
        sa.nl_groups = 1;

        if (::bind(sock.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected(std::format("Помилка bind() до групи Netlink: {}", std::strerror(errno)));
        }

        return UeventListener(std::move(sock));
    }

    void run(const volatile std::sig_atomic_t& stop_flag) {
        std::println("================================================================");
        std::println(" Монітор Netlink uevent на C++23 запущено (Ctrl+C для виходу)");
        std::println(" Очікування пакетів ядра у реальному часі...");
        std::println("================================================================");

        std::array<char, kBufferSize> buffer{};
        pollfd pfd{
            .fd = socket_.get(),
            .events = POLLIN,
            .revents = 0
        };

        while (!stop_flag) {
            int ret = ::poll(&pfd, 1, 500);
            if (ret < 0) {
                if (errno == EINTR) continue;
                std::println(stderr, "Помилка poll(): {}", std::strerror(errno));
                break;
            }
            if (ret == 0) continue;

            if (pfd.revents & POLLIN) {
                ssize_t len = ::recv(socket_.get(), buffer.data(), buffer.size() - 1, MSG_DONTWAIT);
                if (len < 0) {
                    if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) continue;
                    if (errno == ENOBUFS) {
                        std::println(stderr, "УВАГА: переповнення буфера сокета ядра (ENOBUFS)!");
                        continue;
                    }
                    std::println(stderr, "Помилка читання recv(): {}", std::strerror(errno));
                    break;
                }
                if (len == 0) continue;

                buffer[len] = '\0';
                process_payload(std::string_view(buffer.data(), static_cast<size_t>(len)));
            }
        }

        std::println("\nЗавершення роботи. Дескриптор сокета закривається автоматично через RAII.");
    }

private:
    explicit UeventListener(UniqueFd sock) noexcept : socket_(std::move(sock)) {}

    void process_payload(std::string_view data) {
        UeventRecord record;
        size_t offset = 0;

        // Пропускаємо початковий рядок заголовка ("add@/devices/...")
        size_t first_null = data.find('\0');
        if (first_null != std::string_view::npos) {
            offset = first_null + 1;
        }

        while (offset < data.size()) {
            size_t next_null = data.find('\0', offset);
            size_t token_len = (next_null == std::string_view::npos) ? (data.size() - offset) : (next_null - offset);

            if (token_len == 0) break;

            std::string_view token = data.substr(offset, token_len);
            parse_token(token, record);

            if (next_null == std::string_view::npos) break;
            offset = next_null + 1;
        }

        render_record(record);
    }

    void parse_token(std::string_view token, UeventRecord& rec) {
        if (token.starts_with("ACTION=")) rec.action = token.substr(7);
        else if (token.starts_with("DEVPATH=")) rec.devpath = token.substr(8);
        else if (token.starts_with("SUBSYSTEM=")) rec.subsystem = token.substr(10);
        else if (token.starts_with("DEVNAME=")) rec.devname = token.substr(8);
        else if (token.starts_with("MODALIAS=")) rec.modalias = token.substr(9);
        else if (token.starts_with("SEQNUM=")) rec.seqnum = token.substr(7);
        else if (token.starts_with("MAJOR=")) rec.major = token.substr(6);
        else if (token.starts_with("MINOR=")) rec.minor = token.substr(6);
        else if (token.starts_with("DRIVER=")) rec.driver = token.substr(7);
    }

    void render_record(const UeventRecord& r) {
        std::println("────────────────────────────────────────────────────────────────");
        std::println("[UEVENT #{:<6}] ДІЯ: {:<8} | ПІДСИСТЕМА: {}", r.seqnum, r.action, r.subsystem);
        std::println("  Шлях у sysfs:  /sys{}", r.devpath);

        if (!r.devname.empty()) {
            if (!r.major.empty() && !r.minor.empty()) {
                std::println("  Нода у /dev:   /dev/{} (major:minor = {}:{})", r.devname, r.major, r.minor);
            } else {
                std::println("  Нода у /dev:   /dev/{}", r.devname);
            }
        }

        if (!r.driver.empty()) {
            std::println("  Драйвер ядра:  {}", r.driver);
        }

        if (!r.modalias.empty()) {
            std::println("  MODALIAS:      {}", r.modalias);
        }
    }
};

} // namespace netlink

static volatile std::sig_atomic_t g_terminate = 0;

static void on_signal(int) {
    g_terminate = 1;
}

int main() {
    std::signal(SIGINT, on_signal);
    std::signal(SIGTERM, on_signal);

    auto listener = netlink::UeventListener::create();
    if (!listener) {
        std::println(stderr, "Критична помилка: {}", listener.error());
        return 1;
    }

    listener->run(g_terminate);
    return 0;
}
