// C++20 Idiomatic Implementation (RAII, std::span, std::expected)
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <bpf/libbpf.h>

class RingBufferConsumer {
public:
    static std::expected<RingBufferConsumer, std::string> create(int map_fd) {
        auto raw_cb = [](void *ctx, void *data, size_t size) -> int {
            auto *self = static_cast<RingBufferConsumer*>(ctx);
            auto bytes = std::span<const std::byte>(
                reinterpret_cast<const std::byte*>(data), size
            );
            self->process_event(bytes);
            return 0;
        };

        ring_buffer *rb = ring_buffer__new(map_fd, raw_cb, nullptr, nullptr);
        if (!rb) {
            return std::unexpected("Failed to allocate libbpf ring_buffer");
        }
        return RingBufferConsumer(rb);
    }

    ~RingBufferConsumer() {
        if (rb_) ring_buffer__free(rb_);
    }

    RingBufferConsumer(RingBufferConsumer&& other) noexcept 
        : rb_(std::exchange(other.rb_, nullptr)) {}

    void poll(int timeout_ms) {
        ring_buffer__poll(rb_, timeout_ms);
    }

private:
    explicit RingBufferConsumer(ring_buffer *rb) : rb_(rb) {}
    
    void process_event(std::span<const std::byte> data) const {
        std::string_view msg(reinterpret_cast<const char*>(data.data()), data.size());
        std::cout << "[C++ RAII Consumer] Event received: " << msg << '\n';
    }

    ring_buffer *rb_{nullptr};
};
