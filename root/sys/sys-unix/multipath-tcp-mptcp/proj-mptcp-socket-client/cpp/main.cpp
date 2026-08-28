// MPTCP Client implementation in C++ (C++20 Idiomatic RAII)
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <system_error>
#include <expected>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace mptcp {

constexpr int kProtocolMptcp = 262;
constexpr int kSolMptcp = 284;
constexpr int kMptcpInfo = 1;
constexpr uint32_t kFlagFallback = 0x01;

struct MptcpState {
    uint32_t token{0};
    uint8_t subflows{0};
    uint8_t add_addr_accepted{0};
    bool is_fallback{false};
};

// Безпечна RAII обгортка для сокетного дескриптора
class Socket {
public:
    explicit Socket(int fd) noexcept : fd_(fd) {}
    
    ~Socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    Socket(Socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    static std::expected<Socket, std::error_code> create_mptcp() noexcept {
        int fd = ::socket(AF_INET, SOCK_STREAM, kProtocolMptcp);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return Socket(fd);
    }

    std::expected<void, std::error_code> connect(std::string_view ip, uint16_t port) noexcept {
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        
        std::string ip_null_term(ip);
        if (::inet_pton(AF_INET, ip_null_term.c_str(), &addr.sin_addr) <= 0) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        if (::connect(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    [[nodiscard]] std::expected<MptcpState, std::error_code> get_mptcp_state() const noexcept {
        struct RawMptcpInfo {
            uint8_t  subflows;
            uint8_t  add_addr_accepted;
            uint8_t  subflows_max;
            uint8_t  add_addr_accepted_max;
            uint32_t flags;
            uint32_t token;
            uint32_t write_seq;
            uint32_t snd_una;
            uint32_t rcv_nxt;
        } raw_info{};

        socklen_t len = sizeof(raw_info);
        if (::getsockopt(fd_, kSolMptcp, kMptcpInfo, &raw_info, &len) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        MptcpState state;
        state.token = raw_info.token;
        state.subflows = raw_info.subflows;
        state.add_addr_accepted = raw_info.add_addr_accepted;
        state.is_fallback = (raw_info.flags & kFlagFallback) != 0;
        return state;
    }

    std::expected<size_t, std::error_code> send_data(std::string_view data) noexcept {
        ssize_t res = ::send(fd_, data.data(), data.size(), 0);
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<size_t>(res);
    }

private:
    int fd_{-1};
};

} // namespace mptcp

int main(int argc, char* argv[]) {
    const std::string_view server_ip = (argc > 1) ? argv[1] : "127.0.0.1";
    const uint16_t port = (argc > 2) ? static_cast<uint16_t>(std::stoi(argv[2])) : 8080;

    std::cout << "[+] [C++20] Ініціалізація MPTCP сокета...\n";
    auto socket_res = mptcp::Socket::create_mptcp();
    if (!socket_res) {
        std::cerr << "[-] Помилка створення MPTCP сокета: " << socket_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    mptcp::Socket client_sock = std::move(*socket_res);
    std::cout << "[+] Підключення до сервера " << server_ip << ':' << port << "...\n";

    if (auto conn_res = client_sock.connect(server_ip, port); !conn_res) {
        std::cerr << "[-] Помилка підключення: " << conn_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[+] З'єднання успішно встановлено!\n";

    if (auto state = client_sock.get_mptcp_state(); state) {
        std::cout << "=========================================\n"
                  << "        СТАН MPTCP З'ЄДНАННЯ (C++)      \n"
                  << "=========================================\n"
                  << " Токен          : 0x" << std::hex << state->token << std::dec << '\n'
                  << " Підпотоки       : " << static_cast<int>(state->subflows) << '\n'
                  << " Прийняті адреси : " << static_cast<int>(state->add_addr_accepted) << '\n'
                  << " Режим           : " << (state->is_fallback ? "FALLBACK (Single TCP)" : "MULTIPATH TCP ACTIVE") << '\n'
                  << "=========================================\n";
    }

    constexpr std::string_view kHttpRequest = "GET / HTTP/1.1\r\nHost: mptcp.test\r\nConnection: close\r\n\r\n";
    if (auto sent = client_sock.send_data(kHttpRequest); sent) {
        std::cout << "[+] Надіслано " << *sent << " байт запиту.\n";
    }

    return EXIT_SUCCESS;
}
