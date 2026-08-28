// qmp_autoballoon.cpp — ідіоматична реалізація на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <expected>
#include <system_error>
#include <algorithm>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

class QmpConnection {
    int fd_{-1};

public:
    explicit QmpConnection(int fd) noexcept : fd_(fd) {}
    ~QmpConnection() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    QmpConnection(const QmpConnection &) = delete;
    QmpConnection &operator=(const QmpConnection &) = delete;

    QmpConnection(QmpConnection &&other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    QmpConnection &operator=(QmpConnection &&other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    static std::expected<QmpConnection, std::error_code> connect(std::string_view socket_path) {
        int sock = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (sock < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        if (socket_path.size() >= sizeof(addr.sun_path)) {
            ::close(sock);
            return std::unexpected(std::make_error_code(std::errc::filename_too_long));
        }
        std::copy(socket_path.begin(), socket_path.end(), addr.sun_path);

        if (::connect(sock, reinterpret_cast<sockaddr *>(&addr), sizeof(addr)) < 0) {
            int err = errno;
            ::close(sock);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return QmpConnection(sock);
    }

    std::expected<std::string, std::error_code> execute(std::string_view command) {
        if (::write(fd_, command.data(), command.size()) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::vector<char> buffer(4096);
        ssize_t bytes_read = ::read(fd_, buffer.data(), buffer.size() - 1);
        if (bytes_read < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return std::string(buffer.data(), static_cast<size_t>(bytes_read));
    }
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_qmp_сокета>\n";
        return 1;
    }

    auto conn_res = QmpConnection::connect(argv[1]);
    if (!conn_res) {
        std::cerr << "Помилка підключення: " << conn_res.error().message() << '\n';
        return 1;
    }
    auto conn = std::move(*conn_res);

    // Ініціалізація сесії QMP
    std::vector<char> greeting_buf(2048);
    auto _ = conn.execute("{\"execute\": \"qmp_capabilities\"}\n");

    // Встановлення інтервалу збору статистики в 2 секунди
    conn.execute("{\"execute\": \"qom-set\", \"arguments\": "
                 "{\"path\": \"/machine/peripheral/balloon0\", "
                 "\"property\": \"guest-stats-polling-interval\", \"value\": 2}}\n");

    std::cout << "[autoballoon] Керування пам'яттю запущено.\n";

    constexpr uint64_t min_ram = 2ULL * 1024 * 1024 * 1024; // 2 ГБ
    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(3));

        auto stats_res = conn.execute("{\"execute\": \"qom-get\", \"arguments\": "
                                     "{\"path\": \"/machine/peripheral/balloon0\", "
                                     "\"property\": \"guest-stats\"}}\n");
        if (!stats_res) break;

        const std::string &raw = *stats_res;
        auto pos_tot = raw.find("\"stat-total-memory\":");
        auto pos_avail = raw.find("\"stat-available-memory\":");

        if (pos_tot != std::string::npos && pos_avail != std::string::npos) {
            uint64_t total = std::stoull(raw.substr(pos_tot + 20));
            uint64_t avail = std::stoull(raw.substr(pos_avail + 24));

            if (total > 0 && avail > 0) {
                uint64_t used = total - avail;
                uint64_t safety = total * 20 / 100;
                uint64_t target = std::clamp(used + safety, min_ram, total);

                std::cout << "[autoballoon] Total: " << (total >> 20)
                          << " MB, Avail: " << (avail >> 20)
                          << " MB -> New target: " << (target >> 20) << " MB\n";

                std::string cmd = "{\"execute\": \"balloon\", \"arguments\": {\"value\": " +
                                  std::to_string(target) + "}}\n";
                conn.execute(cmd);
            }
        }
    }
    return 0;
}
