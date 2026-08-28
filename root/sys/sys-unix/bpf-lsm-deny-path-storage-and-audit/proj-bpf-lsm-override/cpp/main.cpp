// C++ (Modern C++20 Idiomatic Implementation with RAII)
#include <iostream>
#include <memory>
#include <string_view>
#include <csignal>
#include <atomic>
#include <cstdint>
#include <cerrno>

#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct audit_event {
    std::uint32_t pid;
    std::uint32_t ppid;
    std::uint32_t uid;
    std::uint32_t action;
    char comm[16];
    char filename[256];
};

namespace {
    std::atomic<bool> keep_running{true};

    void signal_handler(int) noexcept {
        keep_running.store(false, std::memory_order_relaxed);
    }

    // RAII-кастомні деструктори для ресурсів libbpf
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
}

static int on_ringbuf_event(void* /*ctx*/, void* data, size_t data_sz) noexcept {
    if (data_sz < sizeof(audit_event)) {
        return 0;
    }

    const auto* e = static_cast<const audit_event*>(data);
    std::string_view comm{e->comm};
    std::string_view path{e->filename};

    if (e->action == 1) {
        std::cout << "[BLOCKED] PID: " << e->pid 
                  << " | UID: " << e->uid 
                  << " | COMM: " << comm 
                  << " | PATH: " << path << '\n';
    } else {
        std::cout << "[ALLOW]   PID: " << e->pid 
                  << " | UID: " << e->uid 
                  << " | COMM: " << comm 
                  << " | PATH: " << path << '\n';
    }
    return 0;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    UniqueBpfObject obj{bpf_object__open_file("bpf_lsm_exec.bpf.o", nullptr)};
    if (!obj) {
        std::cerr << "Помилка відкриття BPF-об'єкта\n";
        return 1;
    }

    if (int err = bpf_object__load(obj.get()); err != 0) {
        std::cerr << "Помилка завантаження BPF програми: " << err << '\n';
        return 1;
    }

    bpf_program* prog = bpf_object__find_program_by_name(obj.get(), "restrict_exec");
    if (!prog) {
        std::cerr << "Не знайдено BPF програму restrict_exec\n";
        return 1;
    }

    UniqueBpfLink link{bpf_program__attach(prog)};
    if (!link) {
        std::cerr << "Помилка прив'язки LSM-хука\n";
        return 1;
    }

    int map_fd = bpf_object__find_map_fd_by_name(obj.get(), "audit_ringbuf");
    if (map_fd < 0) {
        std::cerr << "Не знайдено карту audit_ringbuf\n";
        return 1;
    }

    UniqueRingBuffer rb{ring_buffer__new(map_fd, on_ringbuf_event, nullptr, nullptr)};
    if (!rb) {
        std::cerr << "Помилка створення ring buffer\n";
        return 1;
    }

    std::cout << "BPF LSM монітор запущено в режимі C++20 RAII. Натисніть Ctrl+C для зупинки.\n";

    while (keep_running.load(std::memory_order_relaxed)) {
        int err = ring_buffer__poll(rb.get(), 100);
        if (err < 0 && err != -EINTR) {
            std::cerr << "Помилка моніторингу кільцевого буфера: " << err << '\n';
            break;
        }
    }

    std::cout << "Ресурси автоматично звільнено деструкторами RAII.\n";
    return 0;
}
