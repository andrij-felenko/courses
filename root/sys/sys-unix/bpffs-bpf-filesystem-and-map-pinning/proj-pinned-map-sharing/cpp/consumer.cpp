// consumer.cpp — Ідіоматичний C++20 варіант отримання та читання зафіксованої мапи
#include <iostream>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <bpf/bpf.h>

namespace ebpf {

class AutoFd {
public:
    explicit AutoFd(int fd = -1) noexcept : fd_(fd) {}
    ~AutoFd() { reset(); }

    AutoFd(const AutoFd&) = delete;
    AutoFd& operator=(const AutoFd&) = delete;

    AutoFd(AutoFd&& other) noexcept : fd_(other.release()) {}
    AutoFd& operator=(AutoFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

} // namespace ebpf

constexpr std::string_view kPinPath = "/sys/fs/bpf/shared_stats_map";

int main() {
    constexpr uint32_t key = 42;
    uint64_t value = 0;

    int raw_fd = ::bpf_obj_get(kPinPath.data());
    if (raw_fd < 0) {
        std::cerr << "Помилка відкриття " << kPinPath << ": " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    ebpf::AutoFd map_fd(raw_fd);

    std::cout << "[Consumer C++] Успішно отримано дескриптор мапи (FD " << map_fd.get() << ")\n";

    if (::bpf_map_lookup_elem(map_fd.get(), &key, &value) < 0) {
        std::cerr << "Помилка пошуку ключа " << key << ": "
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Consumer C++] Прочитане значення для ключа " << key << ": " << value << '\n';

    value += 500;
    if (::bpf_map_update_elem(map_fd.get(), &key, &value, BPF_EXIST) < 0) {
        std::cerr << "Помилка запису нового значення: "
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Consumer C++] Нове оновлене значення: " << value << '\n';

    return EXIT_SUCCESS;
}
