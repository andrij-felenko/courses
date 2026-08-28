#include <iostream>
#include <vector>
#include <chrono>
#include <optional>
#include <span>
#include <algorithm>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace happy_eyeballs {

using namespace std::chrono_literals;

/* Безпечна RAII-обгортка для керування життєвим циклом файлового дескриптора */
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

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
    [[nodiscard]] int release() noexcept {
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

private:
    int fd_;
};

struct Endpoint {
    sockaddr_storage addr{};
    socklen_t addr_len{sizeof(sockaddr_storage)};
    int family{AF_INET6};
};

struct ConnectionAttempt {
    UniqueFd socket_fd;
    size_t endpoint_index{0};
    bool connected{false};
};

class ConnectionRacer {
public:
    static constexpr auto kAttemptDelay = 250ms;
    static constexpr auto kTotalTimeout = 10000ms;

    /* Створення черги із суворим чергуванням адрес IPv6 та IPv4 */
    static std::vector<Endpoint> interleave(std::span<const Endpoint> v6_addrs,
                                            std::span<const Endpoint> v4_addrs) {
        std::vector<Endpoint> result;
        result.reserve(v6_addrs.size() + v4_addrs.size());

        size_t i = 0, j = 0;
        while (i < v6_addrs.size() || j < v4_addrs.size()) {
            if (i < v6_addrs.size()) {
                result.push_back(v6_addrs[i++]);
            }
            if (j < v4_addrs.size()) {
                result.push_back(v4_addrs[j++]);
            }
        }
        return result;
    }

    /* Запуск гонки з'єднань над чергою адрес */
    static std::optional<UniqueFd> connect(std::span<const Endpoint> endpoints) {
        if (endpoints.empty()) {
            return std::nullopt;
        }

        std::vector<ConnectionAttempt> active_attempts;
        size_t next_idx = 0;

        const auto start_time = std::chrono::steady_clock::now();
        auto next_attempt_time = start_time;

        while (true) {
            const auto now = std::chrono::steady_clock::now();
            if (now - start_time >= kTotalTimeout) {
                return std::nullopt; /* Загальний таймаут вичерпано */
            }

            /* Перевірка потреби запуску наступної паралельної спроби */
            if (now >= next_attempt_time && next_idx < endpoints.size()) {
                const auto& ep = endpoints[next_idx];
                UniqueFd fd{::socket(ep.family, SOCK_STREAM, 0)};

                if (fd.valid()) {
                    set_nonblocking(fd.get());
                    int rc = ::connect(fd.get(), reinterpret_cast<const sockaddr*>(&ep.addr), ep.addr_len);

                    if (rc == 0) {
                        /* Миттєве встановлення зв'язку */
                        return fd;
                    }

                    if (rc < 0 && errno == EINPROGRESS) {
                        active_attempts.push_back(ConnectionAttempt{
                            .socket_fd = std::move(fd),
                            .endpoint_index = next_idx,
                            .connected = false
                        });
                        next_attempt_time = now + kAttemptDelay;
                    } else {
                        /* Швидка помилка маршруту — перехід до наступної адреси без затримки */
                        next_attempt_time = now;
                    }
                }
                next_idx++;
            }

            /* Підготовка списку дескрипторів для системного виклику poll */
            std::vector<pollfd> poll_fds;
            poll_fds.reserve(active_attempts.size());
            for (const auto& att : active_attempts) {
                if (att.socket_fd.valid()) {
                    poll_fds.push_back(pollfd{
                        .fd = att.socket_fd.get(),
                        .events = POLLOUT,
                        .revents = 0
                    });
                }
            }

            if (poll_fds.empty() && next_idx >= endpoints.size()) {
                return std::nullopt; /* Усі варіанти вичерпано без успіху */
            }

            int timeout_ms = 10;
            if (next_idx < endpoints.size()) {
                auto time_left = std::chrono::duration_cast<std::chrono::milliseconds>(next_attempt_time - now).count();
                timeout_ms = std::max(0, static_cast<int>(time_left));
                timeout_ms = std::min(timeout_ms, 25);
            }

            int prc = ::poll(poll_fds.data(), static_cast<nfds_t>(poll_fds.size()), timeout_ms);
            if (prc > 0) {
                for (size_t i = 0; i < poll_fds.size(); ++i) {
                    if (poll_fds[i].revents & (POLLOUT | POLLERR | POLLHUP)) {
                        int current_fd = poll_fds[i].fd;
                        int sock_err = 0;
                        socklen_t len = sizeof(sock_err);

                        if (::getsockopt(current_fd, SOL_SOCKET, SO_ERROR, &sock_err, &len) == 0 && sock_err == 0) {
                            /* Знайдено переможця: повертаємо дескриптор, решта сокетів закривається автоматично деструкторами RAII */
                            for (auto& att : active_attempts) {
                                if (att.socket_fd.get() == current_fd) {
                                    return std::move(att.socket_fd);
                                }
                            }
                        } else {
                            /* Збій на сокеті — скидаємо та закриваємо відповідний дескриптор */
                            for (auto& att : active_attempts) {
                                if (att.socket_fd.get() == current_fd) {
                                    att.socket_fd.reset();
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

private:
    static bool set_nonblocking(int fd) noexcept {
        int flags = ::fcntl(fd, F_GETFL, 0);
        if (flags == -1) return false;
        return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) != -1;
    }
};

} // namespace happy_eyeballs
