// hook_write.cpp — Потокобезпечне перехоплення викликів C++ з атомарним лічильником
#define _GNU_SOURCE
#include <unistd.h>
#include <dlfcn.h>
#include <atomic>
#include <span>
#include <string_view>
#include <array>
#include <cstdio>

namespace {
    using RealWriteFn = ssize_t (*)(int, const void*, size_t);
    std::atomic<size_t> g_total_bytes_written{0};

    RealWriteFn get_real_write() noexcept {
        static RealWriteFn real_fn = reinterpret_cast<RealWriteFn>(dlsym(RTLD_NEXT, "write"));
        return real_fn;
    }
}

extern "C" ssize_t write(int fd, const void* buf, size_t count) noexcept {
    RealWriteFn real_fn = get_real_write();
    if (!real_fn) {
        return -1;
    }

    // Потокобезпечно підраховуємо загальну кількість байтів через атомарний лічильник
    g_total_bytes_written.fetch_add(count, std::memory_order_relaxed);

    if (fd == STDOUT_FILENO || fd == STDERR_FILENO) {
        std::array<char, 256> log_buffer;
        int len = std::snprintf(log_buffer.data(), log_buffer.size(),
                                "[CPP HOOK] write(fd=%d, size=%zu) | Загалом записано: %zu B\n",
                                fd, count, g_total_bytes_written.load());
        if (len > 0) {
            real_fn(STDERR_FILENO, log_buffer.data(), static_cast<size_t>(len));
        }
    }

    return real_fn(fd, buf, count);
}
