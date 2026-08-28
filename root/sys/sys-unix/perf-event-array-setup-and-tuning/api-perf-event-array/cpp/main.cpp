#include <iostream>
#include <memory>
#include <stdexcept>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

class PerfBufferWrapper {
public:
    explicit PerfBufferWrapper(int map_fd, size_t page_cnt = 16) {
        perf_buffer* pb = perf_buffer__new(
            map_fd,
            page_cnt,
            &PerfBufferWrapper::on_sample,
            &PerfBufferWrapper::on_lost,
            this,
            nullptr
        );

        if (libbpf_get_error(pb)) {
            throw std::runtime_error("Не вдалося ініціалізувати perf_buffer у C++");
        }
        pb_.reset(pb);
    }

    void poll(int timeout_ms = 100) {
        int err = perf_buffer__poll(pb_.get(), timeout_ms);
        if (err < 0 && err != -EINTR) {
            throw std::runtime_error("Помилка опитування perf_buffer__poll");
        }
    }

private:
    static void on_sample(void* ctx, int cpu, void* data, __u32 size) noexcept {
        (void)ctx;
        std::cout << "[C++ Agent] CPU " << cpu << ": отримано " << size << " байт\n";
    }

    static void on_lost(void* ctx, int cpu, __u64 lost_cnt) noexcept {
        (void)ctx;
        std::cerr << "[C++ Agent] УВАГА: Втрачено " << lost_cnt << " подій на CPU " << cpu << "\n";
    }

    struct BufferDeleter {
        void operator()(perf_buffer* pb) const noexcept {
            if (pb) perf_buffer__free(pb);
        }
    };

    std::unique_ptr<perf_buffer, BufferDeleter> pb_;
};
