// producer.cpp — Ідіоматичний C++20 варіант створення та фіксації eBPF-мапи
#include <iostream>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

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
    constexpr uint64_t initial_value = 1000;

    int raw_fd = ::bpf_map_create(BPF_MAP_TYPE_HASH, "shared_stats", sizeof(key), sizeof(initial_value), 1024, nullptr);
    if (raw_fd < 0) {
        std::cerr << "Помилка створення eBPF мапи: " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    ebpf::AutoFd map_fd(raw_fd);

    ::unlink(kPinPath.data());

    if (::bpf_obj_pin(map_fd.get(), kPinPath.data()) < 0) {
        std::cerr << "Помилка фіксації мапи: " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Producer C++] Мапу зафіксовано за шляхом " << kPinPath << '\n';

    if (::bpf_map_update_elem(map_fd.get(), &key, &initial_value, BPF_ANY) < 0) {
        std::cerr << "Помилка оновлення елемента: " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[Producer C++] Успішно записано ключ " << key 
              << " зі значенням " << initial_value << ". Вихід (RAII закриє FD).\n";

    return EXIT_SUCCESS;
}
