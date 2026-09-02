// Той самий демон, зібраний засобами C++: власність дескрипторів тримає RAII,
// помилки налаштування летять винятками, буфер клієнта — це std::string,
// а список клієнтів — вектор, який чиститься одним std::erase_if після пакета
// подій. Логіка контракту з systemd лишається тією самою.
#include "listen_socket.hpp"
#include "notify.hpp"
#include "unique_fd.hpp"

#include <systemd/sd-daemon.h>

#include <csignal>
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/signalfd.h>
#include <sys/socket.h>
#include <sys/timerfd.h>
#include <unistd.h>

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <exception>
#include <filesystem>
#include <format>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {

using namespace std::chrono_literals;
namespace chrono = std::chrono;

constexpr std::size_t kMaxClients = 16;
constexpr std::size_t kRequestMax = 512;
constexpr auto kStuckLimit = 30s;
constexpr std::string_view kDefaultSocketPath = "/run/app-worker/worker.sock";

[[noreturn]] void throw_errno(std::string_view what) {
    throw std::system_error{errno, std::system_category(), std::string{what}};
}

struct Client {
    UniqueFd fd;
    std::string pending;                       // недорозібраний хвіст запиту
    chrono::steady_clock::time_point since{};  // коли прийшов його перший байт
};

class Server {
public:
    explicit Server(ListenSocket listen)
        : listen_{std::move(listen)}, epoll_{make_epoll()}, signals_{make_signalfd()} {
        if (const auto interval = notify::watchdog_interval()) {
            // Половина інтервалу — запас на затримки планувальника.
            ping_ = *interval / 2;
            watchdog_ = make_timerfd(ping_);
        }

        clients_.reserve(kMaxClients);
        watch(listen_.fd());
        watch(signals_.get());
        if (watchdog_) {
            watch(watchdog_.get());
        }
    }

    void run() {
        std::cerr << SD_INFO
                  << std::format("сокет {}, пульс кожні {} мкс\n", listen_.source_name(),
                                 ping_.count());

        // Аж тепер юніт переходить у active: усе потрібне вже підняте, тож
        // залежні служби стартують не в порожнечу.
        notify::ready(std::format("Слухаю сокет ({}), клієнтів максимум {}",
                                  listen_.source_name(), kMaxClients));

        std::array<epoll_event, 8> events{};
        while (running_) {
            const int n = ::epoll_wait(epoll_.get(), events.data(),
                                       static_cast<int>(events.size()), -1);
            if (n < 0) {
                if (errno == EINTR) {
                    continue;
                }
                throw_errno("epoll_wait");
            }

            for (const auto& event : std::span{events.data(), static_cast<std::size_t>(n)}) {
                dispatch(event.data.fd);
            }

            // Закритий дескриптор вибуває з epoll сам; нам лишається прибрати
            // порожні записи вектора.
            std::erase_if(clients_, [](const Client& c) { return !c.fd; });
        }

        notify::stopping("Завершуємо обслуговування");
    }

private:
    static UniqueFd make_epoll() {
        UniqueFd fd{::epoll_create1(EPOLL_CLOEXEC)};
        if (!fd) {
            throw_errno("epoll_create1");
        }
        return fd;
    }

    // Сигнали завершення забираємо дескриптором: у циклі подій вони стають
    // звичайною подією й не рвуть системний виклик посеред роботи.
    static UniqueFd make_signalfd() {
        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGTERM);
        sigaddset(&mask, SIGINT);

        // Блокування обов'язкове: без нього типова дія вб'є процес раніше,
        // ніж ми прочитаємо подію.
        if (::sigprocmask(SIG_BLOCK, &mask, nullptr) < 0) {
            throw_errno("sigprocmask");
        }

        UniqueFd fd{::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC)};
        if (!fd) {
            throw_errno("signalfd");
        }
        return fd;
    }

    static UniqueFd make_timerfd(chrono::microseconds period) {
        UniqueFd fd{::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC)};
        if (!fd) {
            throw_errno("timerfd_create");
        }

        const auto secs = chrono::duration_cast<chrono::seconds>(period);
        itimerspec spec{};
        spec.it_interval.tv_sec = secs.count();
        spec.it_interval.tv_nsec =
            chrono::duration_cast<chrono::nanoseconds>(period - secs).count();
        spec.it_value = spec.it_interval;

        if (::timerfd_settime(fd.get(), 0, &spec, nullptr) < 0) {
            throw_errno("timerfd_settime");
        }
        return fd;
    }

    void watch(int fd) const {
        epoll_event event{};
        event.events = EPOLLIN;
        event.data.fd = fd;
        if (::epoll_ctl(epoll_.get(), EPOLL_CTL_ADD, fd, &event) < 0) {
            throw_errno("epoll_ctl(ADD)");
        }
    }

    void dispatch(int fd) {
        if (fd == listen_.fd()) {
            accept_clients();
        } else if (fd == signals_.get()) {
            handle_signal();
        } else if (watchdog_ && fd == watchdog_.get()) {
            tick_watchdog();
        } else {
            serve_client(fd);
        }
    }

    void accept_clients() {
        for (;;) {
            UniqueFd fd{::accept4(listen_.fd(), nullptr, nullptr,
                                  SOCK_NONBLOCK | SOCK_CLOEXEC)};
            if (!fd) {
                if (errno == EINTR || errno == ECONNABORTED) {
                    continue;  // клієнт передумав між connect() і accept()
                }
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    return;
                }
                if (errno == EMFILE || errno == ENFILE) {
                    // З'єднання чекає в черзі backlog — заберемо його, коли
                    // звільниться дескриптор. Це не привід падати.
                    std::cerr << SD_ERR
                              << std::format("вичерпано ліміт дескрипторів: {}\n",
                                             std::strerror(errno));
                    return;
                }
                throw_errno("accept4");
            }

            if (clients_.size() >= kMaxClients) {
                static constexpr std::string_view kBusy = "ERR busy\n";
                [[maybe_unused]] const auto ignored =
                    ::write(fd.get(), kBusy.data(), kBusy.size());
                ++rejected_;
                std::cerr << SD_WARNING
                          << std::format("усі {} слотів зайнято — відмовляємо клієнтові\n",
                                         kMaxClients);
                continue;  // деструктор UniqueFd закриє з'єднання
            }

            watch(fd.get());
            clients_.push_back(Client{std::move(fd), {}, chrono::steady_clock::now()});
            ++accepted_;
        }
    }

    void serve_client(int fd) {
        const auto it = std::ranges::find_if(
            clients_, [fd](const Client& c) { return c.fd.get() == fd; });
        if (it == clients_.end()) {
            return;  // слот закрили раніше в цьому ж пакеті подій
        }
        read_requests(*it);
    }

    void read_requests(Client& client) {
        std::array<char, 256> chunk{};

        for (;;) {
            const ssize_t got = ::read(client.fd.get(), chunk.data(), chunk.size());
            if (got < 0) {
                if (errno == EINTR) {
                    continue;
                }
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    return;  // усе прочитано, чекаємо наступної події
                }
                std::cerr << SD_WARNING
                          << std::format("read(fd={}): {}\n", client.fd.get(),
                                         std::strerror(errno));
                client.fd.reset();
                return;
            }
            if (got == 0) {
                client.fd.reset();  // клієнт закрив свій бік
                return;
            }

            if (client.pending.empty()) {
                client.since = chrono::steady_clock::now();
            }
            client.pending.append(chunk.data(), static_cast<std::size_t>(got));

            if (client.pending.size() > kRequestMax) {
                // Рядок без переводу довший за межу: або чужий протокол, або
                // спроба забити нам пам'ять.
                std::cerr << SD_WARNING
                          << std::format("запит клієнта fd={} довший за {} байтів\n",
                                         client.fd.get(), kRequestMax);
                client.fd.reset();
                return;
            }

            if (!drain_lines(client)) {
                return;  // з'єднання закрите командою або збоєм запису
            }
        }
    }

    bool drain_lines(Client& client) {
        for (;;) {
            const auto nl = client.pending.find('\n');
            if (nl == std::string::npos) {
                return true;
            }

            std::string_view line{client.pending.data(), nl};
            if (!line.empty() && line.back() == '\r') {
                line.remove_suffix(1);
            }

            const bool alive = handle_request(client, line);
            if (!alive) {
                return false;
            }

            client.pending.erase(0, nl + 1);
            client.since = chrono::steady_clock::now();
        }
    }

    bool handle_request(Client& client, std::string_view line) {
        if (line == "PING") {
            return reply(client, "PONG\n");
        }
        if (line == "STATUS") {
            const auto uptime =
                chrono::duration_cast<chrono::seconds>(chrono::steady_clock::now() - started_);
            return reply(client, std::format("OK uptime={}s accepted={} rejected={} watchdog={}\n",
                                             uptime.count(), accepted_, rejected_,
                                             watchdog_ ? "on" : "off"));
        }
        if (line == "QUIT") {
            if (reply(client, "BYE\n")) {
                client.fd.reset();
            }
            return false;
        }
        return reply(client, "ERR unknown command\n");
    }

    // Повертає true, якщо з'єднання лишилося живим.
    bool reply(Client& client, std::string_view text) {
        const ssize_t written = ::write(client.fd.get(), text.data(), text.size());
        if (written < 0 || static_cast<std::size_t>(written) != text.size()) {
            // Відповіді короткі, часткового запису на них не буває: якщо він
            // стався — клієнт зник.
            std::cerr << SD_WARNING
                      << std::format("клієнт fd={} не прийняв відповідь: {}\n",
                                     client.fd.get(), std::strerror(errno));
            client.fd.reset();
            return false;
        }
        return true;
    }

    void handle_signal() {
        signalfd_siginfo info{};
        if (::read(signals_.get(), &info, sizeof info) != sizeof info) {
            return;
        }
        std::cerr << SD_INFO << std::format("сигнал {} — зупиняємось\n", info.ssi_signo);
        running_ = false;
    }

    // Сенс сторожа саме тут: пінг має означати «я обслуговую роботу»,
    // а не «мій таймер ще цокає».
    [[nodiscard]] bool healthy() const {
        if (::fcntl(listen_.fd(), F_GETFD) < 0) {
            std::cerr << SD_ERR << std::format("слухаючий дескриптор утрачено: {}\n",
                                               std::strerror(errno));
            return false;
        }

        const auto now = chrono::steady_clock::now();
        const bool stuck = std::ranges::any_of(clients_, [&](const Client& c) {
            return !c.pending.empty() && now - c.since > kStuckLimit;
        });
        if (stuck) {
            std::cerr << SD_ERR << "запит клієнта висить понад 30 с\n";
        }
        return !stuck;
    }

    void tick_watchdog() {
        std::uint64_t ticks = 0;
        if (::read(watchdog_.get(), &ticks, sizeof ticks) != sizeof ticks) {
            return;
        }
        if (!healthy()) {
            // Свідомо мовчимо: менеджер вичерпає WatchdogSec=, надішле SIGABRT
            // (звідки візьметься core dump зі станом стеків) і перезапустить нас.
            std::cerr << SD_ERR << "самодіагностика не пройшла — пульс не надсилаємо\n";
            return;
        }
        notify::watchdog();
    }

    ListenSocket listen_;
    UniqueFd epoll_;
    UniqueFd signals_;
    UniqueFd watchdog_;  // порожній, якщо WatchdogSec= не задано
    chrono::microseconds ping_{0};
    std::vector<Client> clients_;
    unsigned accepted_{0};
    unsigned rejected_{0};
    chrono::steady_clock::time_point started_{chrono::steady_clock::now()};
    bool running_{true};
};

}  // namespace

int main(int argc, char* argv[]) {
    // Клієнт може зникнути посеред нашої відповіді; без цього ядро вб'є процес
    // сигналом SIGPIPE, і менеджер порахує це аварією служби.
    std::signal(SIGPIPE, SIG_IGN);

    const std::filesystem::path socket_path =
        argc > 1 ? std::filesystem::path{argv[1]} : std::filesystem::path{kDefaultSocketPath};

    auto listen = ListenSocket::acquire(socket_path);
    if (!listen) {
        std::cerr << SD_ERR
                  << std::format("слухаючий сокет: {}\n", listen.error().message());
        return 1;
    }

    try {
        Server server{std::move(*listen)};
        server.run();
    } catch (const std::exception& e) {
        std::cerr << SD_ERR << std::format("аварія служби: {}\n", e.what());
        return 1;
    }
    return 0;
}
