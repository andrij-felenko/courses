#define _GNU_SOURCE
#include <iostream>
#include <array>
#include <atomic>
#include <string_view>
#include <dlfcn.h>
#include <unistd.h>
#include <cstdint>

namespace memory_hook {

class MemoryTracker {
public:
    using MallocFn = void* (*)(size_t);
    using FreeFn = void (*)(void*);

    static MemoryTracker& instance() noexcept {
        static MemoryTracker tracker;
        return tracker;
    }

    void* allocate(size_t size) noexcept {
        if (initializing_.load(std::memory_order_relaxed)) {
            return allocate_bootstrap(size);
        }

        if (!real_malloc_) {
            init();
        }

        void* ptr = real_malloc_(size);
        log_operation("malloc", size, ptr);
        return ptr;
    }

    void deallocate(void* ptr) noexcept {
        if (!ptr) return;

        if (is_bootstrap_ptr(ptr)) {
            return;
        }

        if (!real_free_) {
            init();
        }

        log_operation("free", 0, ptr);
        real_free_(ptr);
    }

private:
    MemoryTracker() = default;

    static constexpr size_t kBootstrapSize = 64 * 1024;
    alignas(16) std::array<char, kBootstrapSize> bootstrap_buf_{};
    size_t bootstrap_used_{0};

    std::atomic<bool> initializing_{false};
    MallocFn real_malloc_{nullptr};
    FreeFn real_free_{nullptr};

    bool is_bootstrap_ptr(const void* ptr) const noexcept {
        const auto* byte_ptr = reinterpret_cast<const char*>(ptr);
        return byte_ptr >= bootstrap_buf_.data() &&
               byte_ptr < (bootstrap_buf_.data() + bootstrap_buf_.size());
    }

    void* allocate_bootstrap(size_t size) noexcept {
        const size_t aligned_size = (size + 15) & ~size_t(15);
        if (bootstrap_used_ + aligned_size > kBootstrapSize) {
            safe_write("myhook: bootstrap buffer overflow\n");
            return nullptr;
        }
        void* ptr = &bootstrap_buf_[bootstrap_used_];
        bootstrap_used_ += aligned_size;
        return ptr;
    }

    void init() noexcept {
        initializing_.store(true, std::memory_order_relaxed);
        real_malloc_ = reinterpret_cast<MallocFn>(dlsym(RTLD_NEXT, "malloc"));
        real_free_ = reinterpret_cast<FreeFn>(dlsym(RTLD_NEXT, "free"));
        initializing_.store(false, std::memory_order_relaxed);

        if (!real_malloc_ || !real_free_) {
            safe_write("myhook: FATAL failed dlsym\n");
            _exit(1);
        }
    }

    static void safe_write(std::string_view sv) noexcept {
        ::write(STDERR_FILENO, sv.data(), sv.size());
    }

    void log_operation(std::string_view op, size_t size, void* ptr) noexcept {
        char buf[128];
        int len = 0;
        if (op == "malloc") {
            len = ::snprintf(buf, sizeof(buf), "[hook] malloc(%zu) = %p\n", size, ptr);
        } else {
            len = ::snprintf(buf, sizeof(buf), "[hook] free(%p)\n", ptr);
        }
        if (len > 0) {
            ::write(STDERR_FILENO, buf, static_cast<size_t>(len));
        }
    }
};

} // namespace memory_hook

extern "C" {

void* malloc(size_t size) {
    return memory_hook::MemoryTracker::instance().allocate(size);
}

void free(void* ptr) {
    memory_hook::MemoryTracker::instance().deallocate(ptr);
}

}
