// Userspace Controller на ідіоматичному C++20
#include <iostream>
#include <fstream>
#include <string>
#include <memory>
#include <string_view>
#include <charconv>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct PolicyCommand {
    std::uint32_t target_pid;
    std::uint8_t  block_action;
};

// RAII обгортка для файлового дескриптора
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для libbpf user_ring_buffer
class UserRingBuffer {
    struct user_ring_buffer* rb_{nullptr};
public:
    explicit UserRingBuffer(int map_fd) {
        rb_ = user_ring_buffer__new(map_fd, nullptr);
        if (!rb_) {
            throw std::runtime_error("Не вдалося ініціалізувати user_ring_buffer");
        }
    }
    ~UserRingBuffer() {
        if (rb_) user_ring_buffer__free(rb_);
    }
    UserRingBuffer(const UserRingBuffer&) = delete;
    UserRingBuffer& operator=(const UserRingBuffer&) = delete;

    template <typename T>
    class Reservation {
        UserRingBuffer& parent_;
        T* ptr_{nullptr};
    public:
        Reservation(UserRingBuffer& parent, T* ptr) : parent_(parent), ptr_(ptr) {}
        ~Reservation() {
            if (ptr_) {
                user_ring_buffer__discard(parent_.rb_, ptr_);
            }
        }
        T* get() noexcept { return ptr_; }
        T* operator->() noexcept { return ptr_; }

        void submit() {
            if (ptr_) {
                user_ring_buffer__submit(parent_.rb_, ptr_);
                ptr_ = nullptr; // Скасовуємо discard у деструкторі
            }
        }
    };

    template <typename T>
    [[nodiscard]] Reservation<T> reserve() {
        auto* mem = static_cast<T*>(user_ring_buffer__reserve(rb_, sizeof(T)));
        return Reservation<T>(*this, mem);
    }
};

int main()
{
    try {
        UniqueFd map_fd(::bpf_obj_get("/sys/fs/bpf/cmd_ringbuf_map"));
        if (!map_fd.valid()) {
            std::cerr << "Помилка відкриття BPF мапи\n";
            return 1;
        }

        UserRingBuffer ringbuf(map_fd.get());

        // Читання ітератора через стандартний потік C++
        std::ifstream iter_file("/sys/fs/bpf/task_inspector");
        if (!iter_file.is_open()) {
            std::cerr << "Не вдалося відкрити BPF ітератор\n";
            return 1;
        }

        std::string line;
        while (std::getline(iter_file, line)) {
            std::cout << "[BPF Iter] " << line << '\n';

            // Парсинг PID з рядка "PID:12345 COMM:..."
            auto pid_pos = line.find("PID:");
            if (pid_pos != std::string::npos) {
                std::uint32_t pid = 0;
                auto sub = line.substr(pid_pos + 4);
                auto res = std::from_chars(sub.data(), sub.data() + sub.size(), pid);

                if (res.ec == std::errc{} && pid > 0) {
                    std::cout << "Надсилання команди блокування PID " << pid << " в ядро...\n";

                    auto reserve = ringbuf.reserve<PolicyCommand>();
                    if (reserve.get()) {
                        reserve->target_pid = pid;
                        reserve->block_action = 1;
                        reserve.submit(); // Zero-syscall commit
                        std::cout << "Команду успішно надіслано в ядро.\n";
                    }
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняткова ситуація: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
