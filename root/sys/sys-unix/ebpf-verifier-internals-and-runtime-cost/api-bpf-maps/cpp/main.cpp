#include <iostream>
#include <cstdint>
#include <cstring>
#include <system_error>
#include <unistd.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

class BpfMapHandle {
public:
    explicit BpfMapHandle(int fd) : fd_(fd) {
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "bpf_map_create failed");
        }
    }

    ~BpfMapHandle() noexcept {
        if (fd_ >= 0) {
            close(fd_);
        }
    }

    BpfMapHandle(const BpfMapHandle&) = delete;
    BpfMapHandle& operator=(const BpfMapHandle&) = delete;

    BpfMapHandle(BpfMapHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    BpfMapHandle& operator=(BpfMapHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

int main()
{
    try {
        BpfMapHandle map{bpf_map_create(BPF_MAP_TYPE_HASH, "proc_stats",
                                        sizeof(uint32_t), sizeof(uint64_t),
                                        1024, nullptr)};

        const uint32_t key = 1337;
        const uint64_t initial_val = 1;

        if (bpf_map_update_elem(map.get(), &key, &initial_val, BPF_ANY) != 0) {
            throw std::system_error(errno, std::generic_category(), "bpf_map_update_elem failed");
        }

        uint64_t lookup_val = 0;
        if (bpf_map_lookup_elem(map.get(), &key, &lookup_val) == 0) {
            std::cout << "Знайдено значення для PID " << key << ": " << lookup_val << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
