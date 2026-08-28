#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <unistd.h>
#include <grp.h>
#include <iostream>
#include <string_view>
#include <cstdlib>

constexpr uid_t TARGET_UID = 65534; // nobody
constexpr gid_t TARGET_GID = 65534; // nogroup
constexpr uint16_t LISTEN_PORT = 8080;

// Оголошення функцій із розділів 2 та 3
[[nodiscard]] std::expected<void, std::error_code> send_fd(int socket_fd, int fd_to_send) noexcept;
[[nodiscard]] std::expected<UniqueFd, std::error_code> recv_fd(int socket_fd) noexcept;
[[nodiscard]] std::expected<void, std::error_code> install_worker_seccomp() noexcept;

void run_worker(UniqueFd channel) {
    // 1. Очищення додаткових груп
    if (::setgroups(0, nullptr) != 0) {
        std::cerr << "worker: setgroups failed\n";
        std::exit(EXIT_FAILURE);
    }

    // 2. Скидання GID та UID
    if (::setresgid(TARGET_GID, TARGET_GID, TARGET_GID) != 0 ||
        ::setresuid(TARGET_UID, TARGET_UID, TARGET_UID) != 0) {
        std::cerr << "worker: privilege drop failed\n";
        std::exit(EXIT_FAILURE);
    }

    // 3. Увімкнення Seccomp
    if (auto res = install_worker_seccomp(); !res) {
        std::cerr << "worker: seccomp installation failed: " << res.error().message() << "\n";
        std::exit(EXIT_FAILURE);
    }

    std::cout << "[Worker PID " << ::getpid() << "] Права скинуто до UID " << ::getuid() << ", seccomp активний\n";

    // 4. Обробка клієнтських запитів
    while (true) {
        auto client_fd = recv_fd(channel.get());
        if (!client_fd) {
            break; // Майстер закрив керуючий сокет
        }

        constexpr std::string_view response = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!";
        ::write(client_fd->get(), response.data(), response.size());
    }
    std::exit(EXIT_SUCCESS);
}

int main() {
    int fds[2];
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) {
        std::cerr << "socketpair error\n";
        return EXIT_FAILURE;
    }

    UniqueFd master_chan(fds[0]);
    UniqueFd worker_chan(fds[1]);

    pid_t worker_pid = ::fork();
    if (worker_pid < 0) {
        std::cerr << "fork error\n";
        return EXIT_FAILURE;
    }

    if (worker_pid == 0) {
        master_chan.reset(); // Закриваємо сторону майстра
        run_worker(std::move(worker_chan));
    }

    worker_chan.reset(); // Закриваємо сторону воркера

    UniqueFd listen_fd(::socket(AF_INET, SOCK_STREAM, 0));
    if (!listen_fd.valid()) {
        std::cerr << "master: socket error\n";
        return EXIT_FAILURE;
    }

    int opt = 1;
    ::setsockopt(listen_fd.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(LISTEN_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (::bind(listen_fd.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0 ||
        ::listen(listen_fd.get(), 128) != 0) {
        std::cerr << "master: bind/listen error\n";
        return EXIT_FAILURE;
    }

    std::cout << "[Master PID " << ::getpid() << "] Слухає порт " << LISTEN_PORT << "\n";

    for (int i = 0; i < 5; ++i) {
        UniqueFd client_fd(::accept(listen_fd.get(), nullptr, nullptr));
        if (client_fd.valid()) {
            static_cast<void>(send_fd(master_chan.get(), client_fd.get()));
        }
    }

    master_chan.reset();
    listen_fd.reset();
    ::waitpid(worker_pid, nullptr, 0);
    std::cout << "[Master] Завершення роботи.\n";
    return EXIT_SUCCESS;
}
