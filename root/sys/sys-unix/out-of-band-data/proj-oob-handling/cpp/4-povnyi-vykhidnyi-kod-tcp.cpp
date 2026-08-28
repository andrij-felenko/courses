#include <iostream>
#include <array>
#include <string_view>
#include <system_error>
#include <memory>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <poll.h>

// RAII обгортка для файлового дескриптора сокета
class SocketFd {
    int fd_{-1};
public:
    explicit SocketFd(int fd = -1) : fd_(fd) {}
    ~SocketFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketFd(const SocketFd&) = delete;
    SocketFd& operator=(const SocketFd&) = delete;
    SocketFd(SocketFd&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketFd& operator=(SocketFd&& other) noexcept {
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

static int g_client_fd = -1;

static void handle_sigurg(int sig) {
    (void)sig;
    char oob_byte = 0;
    int saved_errno = errno;

    ssize_t n = ::recv(g_client_fd, &oob_byte, 1, MSG_OOB);
    if (n > 0) {
        constexpr std::string_view msg{"\n[SIGURG Handler C++] OOB byte received: "};
        ::write(STDOUT_FILENO, msg.data(), msg.size());
        ::write(STDOUT_FILENO, &oob_byte, 1);
        ::write(STDOUT_FILENO, "\n", 1);
    }

    errno = saved_errno;
}

int main() {
    try {
        SocketFd listen_fd{::socket(AF_INET, SOCK_STREAM, 0)};
        if (!listen_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "socket creation failed");
        }

        int reuse = 1;
        if (::setsockopt(listen_fd.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt SO_REUSEADDR failed");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(9099);

        if (::bind(listen_fd.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            throw std::system_error(errno, std::generic_category(), "bind failed");
        }

        if (::listen(listen_fd.get(), 5) < 0) {
            throw std::system_error(errno, std::generic_category(), "listen failed");
        }

        std::cout << "C++ Server listening on port 9099...\n";

        SocketFd client_fd{::accept(listen_fd.get(), nullptr, nullptr)};
        if (!client_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "accept failed");
        }

        std::cout << "Client connected, fd=" << client_fd.get() << "\n";
        g_client_fd = client_fd.get();

        struct sigaction sa{};
        sa.sa_handler = handle_sigurg;
        sa.sa_flags = SA_RESTART;
        ::sigaction(SIGURG, &sa, nullptr);

        if (::fcntl(client_fd.get(), F_SETOWN, ::getpid()) < 0) {
            throw std::system_error(errno, std::generic_category(), "fcntl F_SETOWN failed");
        }

        std::array<pollfd, 1> fds{};
        fds[0].fd = client_fd.get();
        fds[0].events = POLLIN | POLLPRI;

        std::array<char, 128> buf{};

        while (true) {
            int ret = ::poll(fds.data(), fds.size(), -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "poll failed");
            }

            if (fds[0].revents & POLLPRI) {
                std::cout << "[poll C++] POLLPRI event detected!\n";
                char oob_c = 0;
                ssize_t res = ::recv(client_fd.get(), &oob_c, 1, MSG_OOB);
                if (res > 0) {
                    std::cout << "[poll C++] OOB Byte read: '" << oob_c << "'\n";
                }
            }

            if (fds[0].revents & POLLIN) {
                int atmark = 0;
                if (::ioctl(client_fd.get(), SIOCATMARK, &atmark) == 0 && atmark != 0) {
                    std::cout << "[poll C++] Socket is currently at OOB mark!\n";
                }

                ssize_t n = ::recv(client_fd.get(), buf.data(), buf.size() - 1, 0);
                if (n <= 0) {
                    if (n == 0) std::cout << "Client disconnected.\n";
                    else perror("recv");
                    break;
                }
                buf[n] = '\0';
                std::cout << "Received normal data (" << n << " bytes): " << buf.data();
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
