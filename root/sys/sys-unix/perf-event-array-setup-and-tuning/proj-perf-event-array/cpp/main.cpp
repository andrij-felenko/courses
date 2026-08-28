#include <iostream>
#include <memory>
#include <csignal>
#include <atomic>
#include <string_view>
#include <stdexcept>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "execve_event.h"

namespace {
std::atomic<bool> keep_running{true};

void sig_handler(int) {
    keep_running.store(false);
}

// RAII обгортка для BPF об'єкта
struct BpfObjectDeleter {
    void operator()(bpf_object* obj) const noexcept {
        if (obj) bpf_object__close(obj);
    }
};
using UniqueBpfObject = std::unique_ptr<bpf_object, BpfObjectDeleter>;

// RAII обгортка для Perf Buffer
struct PerfBufferDeleter {
    void operator()(perf_buffer* pb) const noexcept {
        if (pb) perf_buffer__free(pb);
    }
};
using UniquePerfBuffer = std::unique_ptr<perf_buffer, PerfBufferDeleter>;
} // namespace

class ExecveTracer {
public:
    explicit ExecveTracer(std::string_view bpf_obj_path) {
        bpf_object* raw_obj = bpf_object__open_file(bpf_obj_path.data(), nullptr);
        if (libbpf_get_error(raw_obj)) {
            throw std::runtime_error("Не вдалося відкрити BPF об'єкт з файла " + std::string(bpf_obj_path));
        }
        bpf_obj_.reset(raw_obj);

        if (bpf_object__load(bpf_obj_.get()) != 0) {
            throw std::runtime_error("Не вдалося завантажити BPF програму у ядро Linux");
        }

        int map_fd = bpf_object__find_map_fd_by_name(bpf_obj_.get(), "events");
        if (map_fd < 0) {
            throw std::runtime_error("Карту 'events' не знайдено в завантаженому BPF об'єкті");
        }

        perf_buffer* raw_pb = perf_buffer__new(
            map_fd, 8,
            &ExecveTracer::on_sample,
            &ExecveTracer::on_lost,
            this, nullptr
        );

        if (libbpf_get_error(raw_pb)) {
            throw std::runtime_error("Помилка ініціалізації perf_buffer у C++");
        }
        pb_.reset(raw_pb);
    }

    void run() {
        std::cout << "Трасування викликів execve запущено (C++ RAII). Натисніть Ctrl+C для виходу.\n";
        while (keep_running.load()) {
            int err = perf_buffer__poll(pb_.get(), 100);
            if (err < 0 && err != -EINTR) {
                std::cerr << "Помилка опитування perf_buffer__poll: " << err << '\n';
                break;
            }
        }
    }

private:
    static void on_sample(void* ctx, int cpu, void* data, __u32 size) noexcept {
        (void)ctx;
        (void)size;
        const auto* event = static_cast<const execve_event*>(data);
        std::cout << "[CPU " << cpu << "] TIME: " << event->boot_time_ns
                  << " ns | PID: " << event->pid
                  << " | COMM: " << event->comm << '\n';
    }

    static void on_lost(void* ctx, int cpu, __u64 lost_cnt) noexcept {
        (void)ctx;
        std::cerr << "УВАГА: Втрачено " << lost_cnt << " подій на CPU " << cpu << '\n';
    }

    UniqueBpfObject bpf_obj_;
    UniquePerfBuffer pb_;
};

int main() {
    std::signal(SIGINT, sig_handler);
    std::signal(SIGTERM, sig_handler);

    try {
        ExecveTracer tracer("execve_monitor.bpf.o");
        tracer.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    std::cout << "Програму успішно завершено.\n";
    return 0;
}
