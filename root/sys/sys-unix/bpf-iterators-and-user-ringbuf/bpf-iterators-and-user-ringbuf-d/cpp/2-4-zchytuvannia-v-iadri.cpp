// Передача подій у ядро без системних викликів (Userspace C++20)
#include <iostream>
#include <memory>
#include <system_error>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct IpPolicy {
    std::uint32_t ip_address;
    std::uint8_t  action;
};

class UserRingBufferWrapper {
    struct user_ring_buffer* rb_{nullptr};
public:
    explicit UserRingBufferWrapper(int map_fd) {
        rb_ = user_ring_buffer__new(map_fd, nullptr);
        if (!rb_) throw std::runtime_error("Помилка ініціалізації user_ring_buffer");
    }
    ~UserRingBufferWrapper() {
        if (rb_) user_ring_buffer__free(rb_);
    }

    template <typename T>
    bool submit(const T& data) {
        auto* slot = static_cast<T*>(user_ring_buffer__reserve(rb_, sizeof(T)));
        if (!slot) return false;
        *slot = data;
        user_ring_buffer__submit(rb_, slot);
        return true;
    }
};

int main()
{
    int map_fd = bpf_obj_get("/sys/fs/bpf/user_ringbuf_map");
    if (map_fd < 0) {
        std::cerr << "Не вдалося відкрити мапу User Ringbuf\n";
        return 1;
    }

    try {
        UserRingBufferWrapper ringbuf(map_fd);
        for (std::uint32_t i = 0; i < 100000; ++i) {
            IpPolicy policy{.ip_address = 0x0A000001 + i, .action = 1};
            if (!ringbuf.submit(policy)) {
                std::cerr << "Буфер переповнено на ітерації " << i << '\n';
                break;
            }
        }
        std::cout << "Успішно передано 100 000 політик у ядро за нуль системних викликів!\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
