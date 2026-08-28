// C++20: Ідіоматична обгортка з RAII управлінням ресурсами та std::span
#include <iostream>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

namespace ebpf {

// RAII обгортка для безпечного управління файловими дескрипторами сокетів
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
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
};

// RAII обгортка для управління життєвим циклом BPF об'єкта
class BpfObjectWrapper {
    struct bpf_object* obj_{nullptr};
public:
    explicit BpfObjectWrapper(struct bpf_object* obj) : obj_(obj) {}
    ~BpfObjectWrapper() {
        if (obj_) {
            bpf_object__close(obj_);
        }
    }

    [[nodiscard]] struct bpf_object* get() const noexcept { return obj_; }
};

} // namespace ebpf

int main() {
    std::cout << "=== BPF SOCKMAP Redirect Controller (Modern C++20) ===\n";

    // 1. Відкриваємо та завантажуємо BPF програму
    struct bpf_object* raw_obj = bpf_object__open_file("bpf_redir.bpf.o", nullptr);
    if (!raw_obj) {
        std::cerr << "Помилка: не вдалося відкрити BPF об'єкт bpf_redir.bpf.o\n";
        return 1;
    }
    ebpf::BpfObjectWrapper obj(raw_obj);

    if (bpf_object__load(obj.get()) != 0) {
        std::cerr << "Помилка: не вдалося завантажити BPF програму в ядро Linux\n";
        return 1;
    }

    struct bpf_program* prog = bpf_object__find_program_by_name(obj.get(), "bpf_sockmap_redirect");
    int prog_fd = bpf_program__fd(prog);
    int map_fd = bpf_object__find_map_fd_by_name(obj.get(), "sock_map");

    if (prog_fd < 0 || map_fd < 0) {
        std::cerr << "Помилка: не знайдено BPF програму або карту sock_map у файлі\n";
        return 1;
    }

    // 2. Прикріплюємо BPF_SK_MSG_VERDICT до SOCKMAP
    if (bpf_prog_attach(prog_fd, map_fd, BPF_SK_MSG_VERDICT, 0) != 0) {
        std::cerr << "Помилка: не вдалося прикріпити BPF_SK_MSG_VERDICT\n";
        return 1;
    }

    // 3. Створюємо сокетну пару з авто-очищенням RAII
    int fds[2];
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) < 0) {
        std::perror("socketpair");
        return 1;
    }
    ebpf::UniqueFd sock_a(fds[0]);
    ebpf::UniqueFd sock_b(fds[1]);

    // 4. Додаємо сокети у SOCKMAP
    uint32_t key_a = 0, key_b = 1;
    int raw_a = sock_a.get();
    int raw_b = sock_b.get();

    if (bpf_map_update_elem(map_fd, &key_a, &raw_a, BPF_ANY) != 0 ||
        bpf_map_update_elem(map_fd, &key_b, &raw_b, BPF_ANY) != 0) {
        std::cerr << "Помилка оновлення BPF SOCKMAP елементів\n";
        return 1;
    }

    std::cout << "C++ RAII: Сокети зареєстровано у BPF SOCKMAP!\n";

    // 5. Відправляємо дані через std::string_view
    constexpr std::string_view payload = "C++20 Zero-Copy BPF Sockmap Message!";
    ssize_t sent = ::write(sock_a.get(), payload.data(), payload.size());
    std::cout << "Sock A відправив: " << sent << " байтів.\n";

    std::vector<char> buffer(128, 0);
    ssize_t bytes = ::read(sock_b.get(), buffer.data(), buffer.size() - 1);
    if (bytes > 0) {
        std::string_view received(buffer.data(), static_cast<size_t>(bytes));
        std::cout << "Sock B прочитав без TCP/IP: '" << received << "'\n";
    }

    return 0; // RAII деструктори автоматично закриють сокети та BPF об'єкт
}
