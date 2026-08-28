// C++20 Idiomatic Implementation (RAII, std::span, std::expected)
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <csignal>
#include <atomic>
#include <expected>
#include <bpf/libbpf.h>

struct alignas(8) Event {
    std::uint64_t timestamp_ns;
    std::uint32_t pid;
    std::uint32_t cpu_id;
    char comm[16];
    char filename[256];
};

namespace {
std::atomic<bool> g_stop{false};
}

class EventConsumer {
public:
    explicit EventConsumer(int map_fd) {
        auto callback_wrapper = [](void *ctx, void *data, size_t size) -> int {
            auto *self = static_cast<EventConsumer*>(ctx);
            if (size < sizeof(Event)) {
                return 0;
            }
            const auto *ev = static_cast<const Event*>(data);
            self->process_event(*ev);
            return 0;
        };

        rb_ = ring_buffer__new(map_fd, callback_wrapper, this, nullptr);
        if (!rb_) {
            throw std::runtime_error("Failed to initialize libbpf ring_buffer");
        }
    }

    ~EventConsumer() {
        if (rb_) {
            ring_buffer__free(rb_);
        }
    }

    EventConsumer(const EventConsumer&) = delete;
    EventConsumer& operator=(const EventConsumer&) = delete;

    void poll_loop() {
        while (!g_stop.load(std::memory_order_relaxed)) {
            int err = ring_buffer__poll(rb_, 100);
            if (err < 0 && err != -EINTR) {
                std::cerr << "Poll error encountered: " << err << '\n';
                break;
            }
        }
    }

private:
    void process_event(const Event &e) const {
        std::string_view comm(e.comm);
        std::string_view filename(e.filename);
        
        std::cout << '[' << e.timestamp_ns << " ns]"
                  << "[CPU " << e.cpu_id << "] "
                  << "PID " << e.pid << " (" << comm << ") -> "
                  << filename << '\n';
    }

    ring_buffer *rb_{nullptr};
};

int main() {
    std::signal(SIGINT, [](int) { g_stop.store(true); });
    std::signal(SIGTERM, [](int) { g_stop.store(true); });

    int map_fd = 0; // Вказівник на fd відкритими картами

    try {
        EventConsumer consumer(map_fd);
        std::cout << "C++ Trace consumer started...\n";
        consumer.poll_loop();
    } catch (const std::exception &ex) {
        std::cerr << "Fatal error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
