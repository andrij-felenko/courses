// Ідіоматичний C++20 Syslog-клієнт та парсер RFC 5424
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <format>
#include <chrono>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

namespace syslog {

enum class Facility : uint8_t {
    Kern = 0, User = 1, Mail = 2, Daemon = 3, Auth = 4, AuthPriv = 10, Local0 = 16
};

enum class Severity : uint8_t {
    Emerg = 0, Alert = 1, Crit = 2, Error = 3, Warning = 4, Notice = 5, Info = 6, Debug = 7
};

struct Message {
    uint8_t facility;
    uint8_t severity;
    uint8_t version;
    std::string timestamp;
    std::string hostname;
    std::string app_name;
    std::string procid;
    std::string msgid;
    std::string structured_data;
    std::string payload;
};

// RAII обгортка над Unix сокетом
class SocketClient {
public:
    explicit SocketClient(std::string_view socket_path = "/dev/log") {
        m_fd = ::socket(AF_UNIX, SOCK_DGRAM, 0);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити сокет");
        }

        m_addr.sun_family = AF_UNIX;
        std::copy_n(socket_path.data(), 
                    std::min(socket_path.size(), sizeof(m_addr.sun_path) - 1), 
                    m_addr.sun_path);
    }

    ~SocketClient() {
        if (m_fd >= 0) ::close(m_fd);
    }

    SocketClient(const SocketClient&) = delete;
    SocketClient& operator=(const SocketClient&) = delete;

    void send(Facility fac, Severity sev, std::string_view app_name, std::string_view msg) const {
        uint16_t prival = static_cast<uint8_t>(fac) * 8 + static_cast<uint8_t>(sev);
        
        auto now = std::chrono::system_clock::now();
        std::string time_str = std::format("{:%Y-%m-%dT%H:%M:%S%z}", std::chrono::floor<std::chrono::seconds>(now));
        
        std::string frame = std::format("<{}>1 {} localhost {} {} ID1 - {}",
                                        prival, time_str, app_name, ::getpid(), msg);

        ssize_t res = ::sendto(m_fd, frame.data(), frame.size(), 0,
                               reinterpret_cast<const sockaddr*>(&m_addr), sizeof(m_addr));
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відправки у syslog сокет");
        }
    }

private:
    int m_fd{-1};
    sockaddr_un m_addr{};
};

// Zero-copy парсер за допомогою std::string_view
class Parser {
public:
    static std::optional<Message> parse(std::string_view raw) {
        if (raw.empty() || raw.front() != '<') return std::nullopt;

        size_t close_bracket = raw.find('>');
        if (close_bracket == std::string_view::npos) return std::nullopt;

        uint16_t prival = 0;
        for (char c : raw.substr(1, close_bracket - 1)) {
            if (c < '0' || c > '9') return std::nullopt;
            prival = prival * 10 + (c - '0');
        }

        Message msg;
        msg.facility = prival / 8;
        msg.severity = prival % 8;

        std::string_view rest = raw.substr(close_bracket + 1);
        
        // Читаємо версію
        size_t space_pos = rest.find(' ');
        if (space_pos == std::string_view::npos) return std::nullopt;
        msg.version = static_cast<uint8_t>(rest[0] - '0');
        rest.remove_prefix(space_pos + 1);

        // Читаємо поля: timestamp, hostname, app_name, procid, msgid
        auto extract_token = [&rest]() -> std::string_view {
            size_t p = rest.find(' ');
            if (p == std::string_view::npos) {
                std::string_view token = rest;
                rest = {};
                return token;
            }
            std::string_view token = rest.substr(0, p);
            rest.remove_prefix(p + 1);
            return token;
        };

        msg.timestamp = std::string(extract_token());
        msg.hostname  = std::string(extract_token());
        msg.app_name  = std::string(extract_token());
        msg.procid    = std::string(extract_token());
        msg.msgid     = std::string(extract_token());

        // Structured data або '-'
        msg.structured_data = std::string(extract_token());
        msg.payload = std::string(rest);

        return msg;
    }
};

} // namespace syslog

int main() {
    try {
        syslog::SocketClient client;
        client.send(syslog::Facility::User, syslog::Severity::Error, "cpp_app", "Тестова подія RFC 5424");
        std::cout << "Повідомлення успішно надіслано в /dev/log\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка клієнта: " << e.what() << '\n';
    }

    std::string_view raw_frame = "<165>1 2026-08-14T13:36:16.003Z server.corp network_daemon 8812 EVT01 [meta ip=\"10.0.0.1\"] З'єднання скинуто";
    auto parsed = syslog::Parser::parse(raw_frame);

    if (parsed) {
        std::cout << "\nРезультат розбору RFC 5424:\n";
        std::cout << std::format("Facility: {} (local4), Severity: {} (notice)\n", 
                                 parsed->facility, parsed->severity);
        std::cout << std::format("Програма: {} [PID: {}]\n", parsed->app_name, parsed->procid);
        std::cout << std::format("Структуровані дані: {}\n", parsed->structured_data);
        std::cout << std::format("Текст: {}\n", parsed->payload);
    }

    return 0;
}
