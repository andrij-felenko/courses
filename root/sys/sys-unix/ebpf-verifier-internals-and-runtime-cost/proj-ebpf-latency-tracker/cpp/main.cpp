#include <iostream>
#include <memory>
#include <atomic>
#include <csignal>
#include <system_error>
#include <iomanip>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

namespace {
    std::atomic<bool> stop_requested{false};

    void sig_handler(int) {
        stop_requested.store(true, std::memory_order_relaxed);
    }
}

struct Event {
    uint32_t pid;
    uint32_t tgid;
    uint64_t duration_ns;
    int32_t ret_code;
    char comm[16];
};

struct BpfObjectDeleter {
    void operator()(bpf_object* obj) const noexcept {
        if (obj) bpf_object__close(obj);
    }
};

struct BpfLinkDeleter {
    void operator()(bpf_link* link) const noexcept {
        if (link) bpf_link__destroy(link);
    }
};

struct RingBufferDeleter {
    void operator()(ring_buffer* rb) const noexcept {
        if (rb) ring_buffer__free(rb);
    }
};

using UniqueBpfObject = std::unique_ptr<bpf_object, BpfObjectDeleter>;
using UniqueBpfLink = std::unique_ptr<bpf_link, BpfLinkDeleter>;
using UniqueRingBuffer = std::unique_ptr<ring_buffer, RingBufferDeleter>;

static int handle_event([[maybe_unused]] void* ctx, void* data, [[maybe_unused]] size_t data_sz) {
    const auto* e = static_cast<const Event*>(data);
    std::cout << "[TGID " << std::setw(5) << e->tgid << "] "
              << std::setw(16) << std::left << e->comm << std::right
              << " | openat FD: " << std::setw(3) << e->ret_code
              << " | Затримка: " << std::fixed << std::setprecision(2)
              << (static_cast<double>(e->duration_ns) / 1000.0) << " мкс\n";
    return 0;
}

int main() {
    std::signal(SIGINT, sig_handler);
    std::signal(SIGTERM, sig_handler);

    try {
        UniqueBpfObject obj{bpf_object__open_file("openat_tracker.bpf.o", nullptr)};
        if (!obj) {
            throw std::runtime_error("Не вдалося відкрити BPF-файл");
        }

        if (bpf_object__load(obj.get()) != 0) {
            throw std::runtime_error("Верифікатор ядра відхилив програму BPF");
        }

        auto* prog_enter = bpf_object__find_program_by_name(obj.get(), "trace_openat_enter");
        auto* prog_exit = bpf_object__find_program_by_name(obj.get(), "trace_openat_exit");

        UniqueBpfLink link_enter{bpf_program__attach(prog_enter)};
        UniqueBpfLink link_exit{bpf_program__attach(prog_exit)};

        if (!link_enter || !link_exit) {
            throw std::runtime_error("Не вдалося прикріпити зонди kprobe/kretprobe");
        }

        const int map_fd = bpf_object__find_map_fd_by_name(obj.get(), "events");
        UniqueRingBuffer rb{ring_buffer__new(map_fd, handle_event, nullptr, nullptr)};
        if (!rb) {
            throw std::runtime_error("Помилка ініціалізації Ring Buffer");
        }

        std::cout << "Трасування openat запущено (C++). Натисніть Ctrl+C для виходу...\n";

        while (!stop_requested.load(std::memory_order_relaxed)) {
            const int res = ring_buffer__poll(rb.get(), 100);
            if (res < 0 && res != -EINTR) {
                break;
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
