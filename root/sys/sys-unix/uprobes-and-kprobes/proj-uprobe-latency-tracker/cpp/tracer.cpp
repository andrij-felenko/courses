// tracer.cpp - Ідіоматичний завантажувач трасування мовою C++
#include <iostream>
#include <memory>
#include <string_view>
#include <csignal>
#include <atomic>
#include <bpf/libbpf.h>
#include "uprobe_tracer.skel.h"

namespace {
std::atomic<bool> exiting{false};

void sig_handler(int) {
    exiting = true;
}

int handle_event(void*, void* data, size_t) {
    struct Event {
        uint32_t pid;
        uint64_t duration_ns;
    };
    auto e = static_cast<const Event*>(data);
    std::cout << "PID " << e->pid << " | Виконання compute_hash: "
              << (e->duration_ns / 1000) << " мкс ("
              << (static_cast<double>(e->duration_ns) / 1000000.0) << " мс)\n";
    return 0;
}

// RAII обгортка для BPF-скелета
struct SkeletonDeleter {
    void operator()(uprobe_tracer_bpf* ptr) const {
        if (ptr) uprobe_tracer_bpf__destroy(ptr);
    }
};
using UniqueSkeleton = std::unique_ptr<uprobe_tracer_bpf, SkeletonDeleter>;

// RAII обгортка для Ring Buffer
struct RingBufferDeleter {
    void operator()(ring_buffer* ptr) const {
        if (ptr) ring_buffer__free(ptr);
    }
};
using UniqueRingBuffer = std::unique_ptr<ring_buffer, RingBufferDeleter>;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_target_app>\n";
        return 1;
    }
    const std::string_view binary_path = argv[1];

    std::signal(SIGINT, sig_handler);

    UniqueSkeleton skel{uprobe_tracer_bpf__open_and_load()};
    if (!skel) {
        std::cerr << "Помилка відкриття BPF скелета\n";
        return 1;
    }

    skel->links.trace_entry = bpf_program__attach_uprobe(
        skel->progs.trace_entry, false, -1, binary_path.data(), 0);
    skel->links.trace_exit = bpf_program__attach_uprobe(
        skel->progs.trace_exit, true, -1, binary_path.data(), 0);

    UniqueRingBuffer rb{ring_buffer__new(bpf_map__fd(skel->maps.ringbuf), handle_event, nullptr, nullptr)};
    if (!rb) {
        std::cerr << "Помилка створення Ring Buffer\n";
        return 1;
    }

    std::cout << "Трасування затримки активовано для " << binary_path << ". Натисніть Ctrl+C для виходу.\n";

    while (!exiting) {
        int err = ring_buffer__poll(rb.get(), 100);
        if (err < 0 && err != -EINTR) {
            break;
        }
    }

    return 0; // Автоматична очистка через RAII
}
