#include <iostream>
#include <string_view>
#include <string>
#include <thread>
#include <atomic>
#include <chrono>
#include <memory>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace {

constexpr std::string_view kWorkDir = "/tmp/toctou_test_cpp";
constexpr std::string_view kTargetPath = "/tmp/toctou_test_cpp/vulnerable_file.txt";
constexpr std::string_view kSecretPath = "/tmp/toctou_test_cpp/canary_secret.txt";
constexpr int kIterations = 50000;

struct ScopedFd {
    int fd = -1;
    explicit ScopedFd(int f) : fd(f) {}
    ~ScopedFd() { if (fd >= 0) ::close(fd); }
    [[nodiscard]] bool valid() const noexcept { return fd >= 0; }
    [[nodiscard]] int get() const noexcept { return fd; }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : fd(other.fd) { other.fd = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd >= 0) ::close(fd);
            fd = other.fd;
            other.fd = -1;
        }
        return *this;
    }
};

std::atomic<bool> g_running{true};
std::atomic<long> g_victim_attempts{0};

void run_attacker() {
    const std::string temp_real = std::string(kWorkDir) + "/tmp_real";
    const std::string temp_sym = std::string(kWorkDir) + "/tmp_sym";

    while (g_running.load(std::memory_order_relaxed)) {
        {
            ScopedFd fd(::open(temp_real.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0600));
        }
        ::unlink(temp_sym.c_str());
        ::symlink(kSecretPath.data(), temp_sym.c_str());

        ::rename(temp_real.c_str(), kTargetPath.data());
        ::rename(temp_sym.c_str(), kTargetPath.data());
    }
}

void run_vulnerable_victim() {
    for (int i = 0; i < kIterations; ++i) {
        g_victim_attempts.fetch_add(1, std::memory_order_relaxed);

        // 1. ЕТАП ПЕРЕВІРКИ: access() за рядковим шляхом
        if (::access(kTargetPath.data(), F_OK | W_OK) == 0) {
            std::this_thread::sleep_for(std::chrono::microseconds(1));

            // 2. ЕТАП ВИКОРИСТАННЯ: open() за рядковим шляхом
            ScopedFd fd(::open(kTargetPath.data(), O_WRONLY));
            if (fd.valid()) {
                constexpr std::string_view msg = "CORRUPTED_BY_VICTIM\n";
                ::write(fd.get(), msg.data(), msg.size());
            }
        }
    }
    g_running.store(false, std::memory_order_relaxed);
}

} // namespace

int main() {
    ::mkdir(kWorkDir.data(), 0700);

    {
        ScopedFd sfd(::open(kSecretPath.data(), O_WRONLY | O_CREAT | O_TRUNC, 0600));
        if (sfd.valid()) {
            constexpr std::string_view initial = "ORIGINAL_SECRET_STATE\n";
            ::write(sfd.get(), initial.data(), initial.size());
        }
    }

    std::thread attacker(run_attacker);
    std::thread victim(run_vulnerable_victim);

    victim.join();
    attacker.join();

    std::array<char, 128> buf{};
    {
        ScopedFd rfd(::open(kSecretPath.data(), O_RDONLY));
        if (rfd.valid()) {
            ::read(rfd.get(), buf.data(), buf.size() - 1);
        }
    }

    std::cout << "=== Результати вразливої C++ схеми ===\n";
    std::cout << "Спроб жертви: " << g_victim_attempts.load() << "\n";
    std::cout << "Вміст canary-файлу: " << buf.data();

    if (std::string_view(buf.data()).find("CORRUPTED_BY_VICTIM") != std::string_view::npos) {
        std::cout << "СТАТУС: ВРАЗЛИВІСТЬ ПІДТВЕРДЖЕНО (секрет скомпрометовано!)\n";
    } else {
        std::cout << "СТАТУС: Підміна не потрапила у вікно в цій сесії.\n";
    }

    ::unlink(kTargetPath.data());
    ::unlink(kSecretPath.data());
    ::rmdir(kWorkDir.data());
    return 0;
}
