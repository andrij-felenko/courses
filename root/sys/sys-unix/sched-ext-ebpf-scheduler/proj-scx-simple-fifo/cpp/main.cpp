#include <iostream>
#include <memory>
#include <csignal>
#include <atomic>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <bpf/libbpf.h>
#include "my_fifo.skel.h"

namespace {
    std::atomic<bool> g_stop{false};

    void signal_handler(int signal) noexcept {
        (void)signal;
        g_stop.store(true, std::memory_order_relaxed);
    }
}

// RAII обгортка для керування BPF-скелетом
class ScxScheduler {
public:
    ScxScheduler() {
        m_skel.reset(my_fifo_bpf__open_and_load());
        if (!m_skel) {
            throw std::runtime_error("Не вдалося відкрити або завантажити BPF-скелет");
        }

        m_link.reset(bpf_map__attach_struct_ops(m_skel->maps.fifo_ops));
        if (!m_link) {
            throw std::runtime_error("Не вдалося приєднати struct_ops до sched_ext");
        }
    }

    ~ScxScheduler() noexcept {
        // Деструктор автоматично вивантажує BPF link та skel у зворотному порядку
        std::cout << "\nВивантаження BPF-планувальника sched_ext через RAII...\n";
    }

    ScxScheduler(const ScxScheduler&) = delete;
    ScxScheduler& operator=(const ScxScheduler&) = delete;

private:
    struct BpfDeleter {
        void operator()(my_fifo_bpf* skel) const noexcept {
            if (skel) my_fifo_bpf__destroy(skel);
        }
    };

    struct LinkDeleter {
        void operator()(bpf_link* link) const noexcept {
            if (link) bpf_link__destroy(link);
        }
    };

    std::unique_ptr<my_fifo_bpf, BpfDeleter> m_skel;
    std::unique_ptr<bpf_link, LinkDeleter> m_link;
};

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        ScxScheduler scheduler;
        std::cout << "Планувальник simple_fifo успішно завантажено в ядрі (C++ RAII).\n";
        std::cout << "Очікування сигналу вивантаження (Ctrl+C)...\n";

        while (!g_stop.load(std::memory_order_relaxed)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }

    std::cout << "Планувальник вивантажено. Автоматичне повернення до EEVDF.\n";
    return 0;
}
