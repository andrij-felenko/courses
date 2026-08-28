// C++20 Ідіоматичний API (libbpf з RAII та std::span)
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

namespace ebpf {

// RAII обгортка для ring_buffer
class RingBuffer {
public:
    using EventCallback = std::function<void(std::span<const std::byte>)>;

    static std::expected<RingBuffer, std::string> create(int map_fd, EventCallback cb) {
        auto cb_holder = std::make_unique<EventCallback>(std::move(cb));
        
        auto raw_cb = [](void *ctx, void *data, size_t size) -> int {
            auto *fn = static_cast<EventCallback*>(ctx);
            auto payload = std::span<const std::byte>(
                reinterpret_cast<const std::byte*>(data), size
            );
            (*fn)(payload);
            return 0;
        };

        ring_buffer *rb = ring_buffer__new(map_fd, raw_cb, cb_holder.get(), nullptr);
        if (!rb) {
            return std::unexpected("Failed to allocate ring_buffer in libbpf");
        }

        return RingBuffer(rb, std::move(cb_holder));
    }

    ~RingBuffer() {
        if (rb_) {
            ring_buffer__free(rb_);
        }
    }

    RingBuffer(const RingBuffer&) = delete;
    RingBuffer& operator=(const RingBuffer&) = delete;

    RingBuffer(RingBuffer&& other) noexcept 
        : rb_(std::exchange(other.rb_, nullptr)), 
          cb_holder_(std::move(other.cb_holder_)) {}

    int poll(int timeout_ms) {
        return ring_buffer__poll(rb_, timeout_ms);
    }

    int consume() {
        return ring_buffer__consume(rb_);
    }

    int epoll_fd() const noexcept {
        return ring_buffer__epoll_fd(rb_);
    }

private:
    RingBuffer(ring_buffer *rb, std::unique_ptr<EventCallback> cb)
        : rb_(rb), cb_holder_(std::move(cb)) {}

    ring_buffer *rb_{nullptr};
    std::unique_ptr<EventCallback> cb_holder_;
};

} // namespace ebpf
