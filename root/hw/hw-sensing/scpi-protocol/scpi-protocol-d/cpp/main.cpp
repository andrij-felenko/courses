#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <optional>
#include <chrono>
#include <format>
#include <charconv>
#include <system_error>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    using socket_handle_t = SOCKET;
    constexpr socket_handle_t kInvalidSocket = INVALID_SOCKET;
    inline void close_socket(socket_handle_t s) noexcept { closesocket(s); }
#else
    #include <unistd.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/tcp.h>
    #include <arpa/inet.h>
    #include <sys/time.h>
    using socket_handle_t = int;
    constexpr socket_handle_t kInvalidSocket = -1;
    inline void close_socket(socket_handle_t s) noexcept { close(s); }
#endif

namespace bench::scpi {

enum class ErrorCode {
    NetworkInitFailed,
    ConnectionFailed,
    SendFailed,
    ReceiveTimeout,
    InvalidResponse,
    DeviceError
};

struct DeviceErrorInfo {
    int code{0};
    std::string message;
};

class NetworkRuntime {
public:
    NetworkRuntime() {
#ifdef _WIN32
        WSADATA wsa;
        valid_ = (WSAStartup(MAKEWORD(2, 2), &wsa) == 0);
#else
        valid_ = true;
#endif
    }
    ~NetworkRuntime() {
#ifdef _WIN32
        if (valid_) WSACleanup();
#endif
    }
    [[nodiscard]] bool is_valid() const noexcept { return valid_; }
private:
    bool valid_{false};
};

class InstrumentSession {
public:
    InstrumentSession() = default;
    ~InstrumentSession() { disconnect(); }

    InstrumentSession(const InstrumentSession&) = delete;
    InstrumentSession& operator=(const InstrumentSession&) = delete;

    InstrumentSession(InstrumentSession&& other) noexcept 
        : sock_(other.sock_), ip_(std::move(other.ip_)), port_(other.port_) {
        other.sock_ = kInvalidSocket;
    }

    InstrumentSession& operator=(InstrumentSession&& other) noexcept {
        if (this != &other) {
            disconnect();
            sock_ = other.sock_;
            ip_ = std::move(other.ip_);
            port_ = other.port_;
            other.sock_ = kInvalidSocket;
        }
        return *this;
    }

    [[nodiscard]] std::expected<void, ErrorCode> connect(
        std::string_view ip, uint16_t port, std::chrono::milliseconds timeout = std::chrono::seconds(2)) {
        
        disconnect();
        ip_ = ip;
        port_ = port;

        sock_ = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock_ == kInvalidSocket) {
            return std::unexpected(ErrorCode::ConnectionFailed);
        }

        int nodelay = 1;
        setsockopt(sock_, IPPROTO_TCP, TCP_NODELAY, reinterpret_cast<const char*>(&nodelay), sizeof(int));

#ifdef _WIN32
        DWORD tv = static_cast<DWORD>(timeout.count());
        setsockopt(sock_, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<const char*>(&tv), sizeof(tv));
        setsockopt(sock_, SOL_SOCKET, SO_SNDTIMEO, reinterpret_cast<const char*>(&tv), sizeof(tv));
#else
        struct timeval tv;
        tv.tv_sec = timeout.count() / 1000;
        tv.tv_usec = (timeout.count() % 1000) * 1000;
        setsockopt(sock_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        setsockopt(sock_, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
#endif

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        if (inet_pton(AF_INET, ip_.c_str(), &addr.sin_addr) <= 0) {
            disconnect();
            return std::unexpected(ErrorCode::ConnectionFailed);
        }

        if (::connect(sock_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            disconnect();
            return std::unexpected(ErrorCode::ConnectionFailed);
        }

        return {};
    }

    void disconnect() noexcept {
        if (sock_ != kInvalidSocket) {
            close_socket(sock_);
            sock_ = kInvalidSocket;
        }
    }

    [[nodiscard]] std::expected<void, ErrorCode> send(std::string_view command) const {
        if (sock_ == kInvalidSocket) return std::unexpected(ErrorCode::SendFailed);

        std::string formatted{command};
        if (!formatted.ends_with('\n')) {
            formatted.push_back('\n');
        }

        size_t total_sent = 0;
        while (total_sent < formatted.size()) {
            auto sent = ::send(sock_, formatted.data() + total_sent, 
                               static_cast<int>(formatted.size() - total_sent), 0);
            if (sent <= 0) return std::unexpected(ErrorCode::SendFailed);
            total_sent += static_cast<size_t>(sent);
        }
        return {};
    }

    [[nodiscard]] std::expected<std::string, ErrorCode> receive_line() const {
        if (sock_ == kInvalidSocket) return std::unexpected(ErrorCode::ReceiveTimeout);

        std::string response;
        response.reserve(128);
        char ch = 0;

        while (true) {
            int rec = ::recv(sock_, &ch, 1, 0);
            if (rec <= 0) {
                if (!response.empty()) break;
                return std::unexpected(ErrorCode::ReceiveTimeout);
            }
            if (ch == '\r') continue;
            if (ch == '\n') break;
            response.push_back(ch);
        }
        return response;
    }

    [[nodiscard]] std::expected<std::string, ErrorCode> query(std::string_view req) const {
        if (auto res = send(req); !res) return std::unexpected(res.error());
        return receive_line();
    }

    [[nodiscard]] std::expected<double, ErrorCode> query_double(std::string_view req) const {
        auto str_res = query(req);
        if (!str_res) return std::unexpected(str_res.error());

        double val = 0.0;
        auto [ptr, ec] = std::from_chars(str_res->data(), str_res->data() + str_res->size(), val);
        if (ec != std::errc()) {
            return std::unexpected(ErrorCode::InvalidResponse);
        }
        return val;
    }

    [[nodiscard]] std::expected<std::vector<DeviceErrorInfo>, ErrorCode> drain_error_queue() const {
        std::vector<DeviceErrorInfo> errors;
        while (true) {
            auto res = query(":SYSTem:ERRor?");
            if (!res) return std::unexpected(res.error());

            int code = 0;
            std::string msg;
            
            auto comma_pos = res->find(',');
            if (comma_pos != std::string::npos) {
                std::from_chars(res->data(), res->data() + comma_pos, code);
                msg = res->substr(comma_pos + 1);
                if (msg.starts_with('"') && msg.ends_with('"')) {
                    msg = msg.substr(1, msg.size() - 2);
                }
            } else {
                std::from_chars(res->data(), res->data() + res->size(), code);
            }

            if (code == 0) break;
            errors.push_back(DeviceErrorInfo{code, std::move(msg)});
        }
        return errors;
    }

private:
    socket_handle_t sock_{kInvalidSocket};
    std::string     ip_;
    uint16_t        port_{5025};
};

} // namespace bench::scpi

int main() {
    bench::scpi::NetworkRuntime runtime;
    if (!runtime.is_valid()) {
        std::cerr << "Збій мережевої підсистеми!\n";
        return 1;
    }

    bench::scpi::InstrumentSession psu;
    std::cout << "Підключення до джерела живлення 192.168.1.110:5025...\n";
    
    if (auto res = psu.connect("192.168.1.110", 5025); !res) {
        std::cerr << "Не вдалося з'єднатися з приладом!\n";
        return 1;
    }

    if (auto idn = psu.query("*IDN?"); idn) {
        std::cout << std::format("Прилад: {}\n", *idn);
    }

    // Безпечна ініціалізація
    (void)psu.send("*RST");
    (void)psu.send("*CLS");
    (void)psu.send(":SOURce:VOLTage 12.000");
    (void)psu.send(":SOURce:CURRent:PROTection 1.500");
    (void)psu.send(":OUTPut:STATe ON");

    // Перевірка помилок
    if (auto errs = psu.drain_error_queue(); errs && !errs->empty()) {
        for (const auto& err : *errs) {
            std::cerr << std::format("Помилка приладу [{}]: {}\n", err.code, err.message);
        }
    } else {
        std::cout << "Параметри успішно встановлено, вихід увімкнено.\n";
        if (auto meas = psu.query_double(":MEASure:VOLTage:DC?"); meas) {
            std::cout << std::format("Фактична напруга: {:.4f} В\n", *meas);
        }
    }

    return 0;
}
