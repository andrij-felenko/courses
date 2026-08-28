#include <iostream>
#include <memory>
#include <atomic>
#include <csignal>
#include <string_view>
#include <stdexcept>
#include <cerrno>
#include <bpf/libbpf.h>
#include "exec_monitor.skel.h"
#include "exec_event.h"   // спільне оголошення struct exec_event

namespace {
// Атомарний прапор завершення для безпечної роботи між потоками та обробником сигналів
std::atomic<bool> exiting{false};

void signal_handler(int) {
    exiting.store(true);
}

// RAII-обгортка для керування життєвим циклом BPF-скелета
class bpf_monitor_skeleton {
public:
    bpf_monitor_skeleton() {
        skel_.reset(exec_monitor_bpf__open_and_load());
        if (!skel_) {
            throw std::runtime_error("Не вдалося завантажити BPF-скелет у ядро");
        }
        if (exec_monitor_bpf__attach(skel_.get()) != 0) {
            throw std::runtime_error("Не вдалося прив'язати BPF-програму до tracepoint");
        }
    }

    [[nodiscard]] int get_map_fd() const noexcept {
        return bpf_map__fd(skel_->maps.rb);
    }

private:
    struct skel_deleter {
        void operator()(exec_monitor_bpf* s) const noexcept {
            if (s) {
                exec_monitor_bpf__destroy(s);
            }
        }
    };
    std::unique_ptr<exec_monitor_bpf, skel_deleter> skel_;
};

// RAII-обгортка для керування життєвим циклом Ring Buffer
class bpf_ring_buffer {
public:
    using sample_cb = int (*)(void *ctx, void *data, size_t size);

    bpf_ring_buffer(int map_fd, sample_cb cb) {
        rb_.reset(ring_buffer__new(map_fd, cb, nullptr, nullptr));
        if (!rb_) {
            throw std::runtime_error("Не вдалося створити об'єкт Ring Buffer");
        }
    }

    void poll(int timeout_ms) {
        int err = ring_buffer__poll(rb_.get(), timeout_ms);
        if (err < 0 && err != -EINTR) {
            throw std::runtime_error("Помилка опитування Ring Buffer");
        }
    }

private:
    struct rb_deleter {
        void operator()(ring_buffer* r) const noexcept {
            if (r) {
                ring_buffer__free(r);
            }
        }
    };
    std::unique_ptr<ring_buffer, rb_deleter> rb_;
};

// C++20 колбек обробки подій з використанням std::string_view для відсутності копіювань
int handle_exec_event(void*, void* data, size_t) {
    const auto* e = static_cast<const exec_event*>(data);
    
    std::cout << "[EXEC] PID: " << e->pid 
              << " | PPID: " << e->ppid 
              << " | UID: " << e->uid 
              << " | GID: " << e->gid 
              << " | COMM: " << std::string_view(e->comm) 
              << " | PATH: " << std::string_view(e->filename) << "\n";
    return 0;
}
} // namespace

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        // Створення RAII об'єктів скелета та кільцевого буфера
        bpf_monitor_skeleton skeleton;
        bpf_ring_buffer rb(skeleton.get_map_fd(), handle_exec_event);

        std::cout << "eBPF Process Monitor (C++20 RAII) запущено. Ctrl-C для виходу...\n";

        // Головний цикл обробки подій
        while (!exiting.load(std::memory_order_relaxed)) {
            rb.poll(100);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << "\n";
        return 1;
    }

    std::cout << "Монітор коректно завершив роботу.\n";
    return 0;
}
