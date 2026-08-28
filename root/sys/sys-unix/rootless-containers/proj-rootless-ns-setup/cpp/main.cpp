#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <system_error>
#include <memory>
#include <utility>
#include <unistd.h>
#include <sched.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/mount.h>

namespace rootless {

// RAII безпечна обгортка для файлових дескрипторів Linux
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

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

    int release() noexcept {
        return std::exchange(fd_, -1);
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

// RAII обгортка для каналу міжпроцесної синхронізації
class Channel {
public:
    static std::pair<Channel, Channel> create_connected_pair() {
        std::array<int, 2> fds{-1, -1};
        if (::pipe(fds.data()) == -1) {
            throw std::system_error(errno, std::generic_category(), "Failed to create IPC pipe");
        }
        return {Channel(UniqueFd(fds[0])), Channel(UniqueFd(fds[1]))};
    }

    explicit Channel(UniqueFd fd) : fd_(std::move(fd)) {}

    void send_token(char token) {
        if (::write(fd_.get(), &token, 1) != 1) {
            throw std::system_error(errno, std::generic_category(), "Failed to write token to pipe");
        }
    }

    char receive_token() {
        char token = 0;
        if (::read(fd_.get(), &token, 1) != 1) {
            throw std::system_error(errno, std::generic_category(), "Failed to read token from pipe");
        }
        return token;
    }

private:
    UniqueFd fd_;
};

// Безпечний запуск зовнішньої setuid-утиліти відображення ідентифікаторів
void invoke_id_map_tool(std::string_view tool_name, pid_t target_pid, 
                        std::string_view inside_id, std::string_view outside_id, 
                        std::string_view range_size) {
    const pid_t map_pid = ::fork();
    if (map_pid == -1) {
        throw std::system_error(errno, std::generic_category(), "Forking map tool failed");
    }

    if (map_pid == 0) {
        const std::string pid_str = std::to_string(target_pid);
        ::execlp(tool_name.data(), tool_name.data(), pid_str.c_str(), 
                 inside_id.data(), outside_id.data(), range_size.data(), nullptr);
        ::exit(EXIT_FAILURE);
    }

    int wait_status = 0;
    if (::waitpid(map_pid, &wait_status, 0) == -1) {
        throw std::system_error(errno, std::generic_category(), "Waiting for map tool failed");
    }

    if (!WIFEXITED(wait_status) || WEXITSTATUS(wait_status) != 0) {
        throw std::runtime_error("Map tool " + std::string(tool_name) + " failed execution");
    }
}

} // namespace rootless

int main() {
    try {
        std::cout << "[CPP Init] Orchestrating Rootless Container via Modern C++...\n";

        auto [reader, writer] = rootless::Channel::create_connected_pair();

        const uid_t host_uid = ::getuid();
        const gid_t host_gid = ::getgid();

        const pid_t child_pid = ::fork();
        if (child_pid == -1) {
            throw std::system_error(errno, std::generic_category(), "Forking container child failed");
        }

        if (child_pid == 0) {
            // --- Дочірній процес контейнера ---
            if (::unshare(CLONE_NEWUSER | CLONE_NEWNS) == -1) {
                throw std::system_error(errno, std::generic_category(), "unshare(CLONE_NEWUSER|CLONE_NEWNS) failed");
            }

            // Відправляємо сигнал батьківському процесу
            writer.send_token('R');

            // Очікуємо підтвердження конфігурації мапінгу від батька
            [[maybe_unused]] const char ack = writer.receive_token();

            std::cout << "[CPP Child] Container Credentials: UID=" << ::getuid() << ", GID=" << ::getgid() << "\n";
            if (::getuid() == 0) {
                std::cout << "[CPP Child] Gained Root Privileges inside isolated Namespace!\n";
            }

            // Монтуємо приватну tmpfs
            if (::mount("tmpfs", "/tmp", "tmpfs", 0, "size=32M") == 0) {
                std::cout << "[CPP Child] Private tmpfs successfully mounted on /tmp!\n";
            }

            const std::array<const char*, 2> bash_args{"/bin/bash", nullptr};
            ::execvp(bash_args[0], const_cast<char* const*>(bash_args.data()));
            ::exit(EXIT_FAILURE);
        }

        // --- Батьківський процес оркестрації ---
        [[maybe_unused]] const char ready_signal = reader.receive_token();

        std::cout << "[CPP Parent] Child process " << child_pid << " is ready. Running setuid helpers...\n";

        const std::string host_uid_str = std::to_string(host_uid);
        const std::string host_gid_str = std::to_string(host_gid);

        // Налаштування таблиці мапінгу через утиліти newuidmap / newgidmap
        rootless::invoke_id_map_tool("newuidmap", child_pid, "0", host_uid_str, "1");
        rootless::invoke_id_map_tool("newgidmap", child_pid, "0", host_gid_str, "1");

        std::cout << "[CPP Parent] Mappings registered successfully. Releasing child...\n";
        reader.send_token('G');

        int child_status = 0;
        ::waitpid(child_pid, &child_status, 0);
        std::cout << "[CPP Parent] Container session finished.\n";

    } catch (const std::exception& err) {
        std::cerr << "[CPP Error] " << err.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
