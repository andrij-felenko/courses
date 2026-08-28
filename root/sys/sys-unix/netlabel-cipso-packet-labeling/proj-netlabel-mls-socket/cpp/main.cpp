#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/*
 * RAII-клас для безпечного володіння файловим дескриптором сокета.
 */
class [[nodiscard]] UniqueSocket {
public:
    UniqueSocket() noexcept : fd_{-1} {}
    explicit UniqueSocket(int fd) noexcept : fd_{fd} {}
    
    ~UniqueSocket() noexcept {
        reset();
    }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return isValid(); }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    [[nodiscard]] int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

private:
    int fd_;
};

/*
 * Сервіс для обслуговування MLS-з'єднань та видобування контекстів безпеки.
 */
class MlsPeerSecService {
public:
    static constexpr uint16_t kDefaultPort = 8443;
    static constexpr size_t kMaxSecContextLen = 512;

    /*
     * Отримує текстовий контекст безпеки SO_PEERSEC за допомогою getsockopt.
     */
    static std::expected<std::string, std::error_code> getPeerContext(int socketFd) {
        std::vector<char> buffer(kMaxSecContextLen, '\0');
        auto optlen = static_cast<socklen_t>(buffer.size());

        if (::getsockopt(socketFd, SOL_SOCKET, SO_PEERSEC, buffer.data(), &optlen) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (optlen > 0 && optlen <= buffer.size()) {
            size_t string_len = (buffer[optlen - 1] == '\0') ? optlen - 1 : optlen;
            return std::string(buffer.data(), string_len);
        }
        return std::string(buffer.data());
    }

    /*
     * Ініціалізує слухаючий сокет TCP-сервера.
     */
    static std::expected<UniqueSocket, std::error_code> createListener(uint16_t port = kDefaultPort) {
        int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        UniqueSocket serverSock(raw_fd);

        int opt = 1;
        if (::setsockopt(serverSock.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sockaddr_in server_addr{};
        server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = ::htonl(INADDR_ANY);
        server_addr.sin_port = ::htons(port);

        if (::bind(serverSock.get(), reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::listen(serverSock.get(), 10) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return serverSock;
    }
};

int main() {
    auto listenerResult = MlsPeerSecService::createListener();
    if (!listenerResult) {
        std::cerr << "[ПОМИЛКА] Не вдалося створити MLS-сервер: " 
                  << listenerResult.error().message() << '\n';
        return 1;
    }

    UniqueSocket serverSocket = std::move(*listenerResult);
    std::cout << "[INFO] C++ MLS TCP-сервер слухає порт " << MlsPeerSecService::kDefaultPort << "...\n";

    while (true) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        
        int raw_client = ::accept(serverSocket.get(), reinterpret_cast<sockaddr*>(&client_addr), &client_len);
        if (raw_client < 0) {
            if (errno == EINTR) continue;
            std::cerr << "[ПОМИЛКА] Помилка accept: " << std::strerror(errno) << '\n';
            break;
        }

        UniqueSocket clientSocket(raw_client);
        char ipBuf[INET_ADDRSTRLEN];
        ::inet_ntop(AF_INET, &client_addr.sin_addr, ipBuf, sizeof(ipBuf));
        std::cout << "\n[CONNECT] З'єднання від " << ipBuf << ':' << ::ntohs(client_addr.sin_port) << '\n';

        auto contextResult = MlsPeerSecService::getPeerContext(clientSocket.get());
        if (contextResult) {
            std::cout << "[NETLABEL/LSM] Контекст SO_PEERSEC: " << *contextResult << '\n';
        } else {
            std::cout << "[NETLABEL/LSM] Не вдалося отримати мітку: " 
                      << contextResult.error().message() << '\n';
        }

        std::string_view reply = "HTTP/1.1 200 OK\r\nContent-Length: 18\r\n\r\nMLS-CPP ACK SUCESS";
        [[maybe_unused]] auto bytesWritten = ::write(clientSocket.get(), reply.data(), reply.size());
    }

    return 0;
}
