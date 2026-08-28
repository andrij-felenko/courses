// main.cpp — Ідіоматична реалізація мовою C++ (RAII, std::unique_ptr, exceptions)
#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <csignal>
#include <stdexcept>
#include <bpf/libbpf.h>
#include "bench.skel.h"

namespace {
    std::volatile std::sig_atomic_t g_exiting = 0;

    void signal_handler(int) {
        g_exiting = 1;
    }

    // RAII-обгортка для керування життєвим циклом BPF-скелета
    struct BpfSkelDeleter {
        void operator()(bench_bpf* skel) const noexcept {
            if (skel) {
                bench_bpf__destroy(skel);
            }
        }
    };
    using BpfSkelPtr = std::unique_ptr<bench_bpf, BpfSkelDeleter>;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        // 1. Створення BPF-скелета з автоматичним вивільненням через RAII
        BpfSkelPtr skel(bench_bpf__open_and_load());
        if (!skel) {
            throw std::runtime_error("Не вдалося відкрити та завантажити BPF-скелет");
        }

        // 2. Приєднання зондів
        int err = bench_bpf__attach(skel.get());
        if (err != 0) {
            throw std::runtime_error("Не вдалося приєднати BPF-програми, код: " + std::to_string(err));
        }

        std::cout << "[C++] Бенчмарк успішно запущено. Очікування подій...\n";

        // 3. Основний моніторинговий цикл
        while (!g_exiting) {
            std::this_thread::sleep_for(std::chrono::seconds(1));

            uint32_t kprobe_key = 0, fentry_key = 1;
            uint64_t kprobe_ns = 0, fentry_ns = 0;

            if (bpf_map__lookup_elem(skel->maps.bench_stats, &kprobe_key, sizeof(kprobe_key),
                                     &kprobe_ns, sizeof(kprobe_ns), 0) == 0 &&
                bpf_map__lookup_elem(skel->maps.bench_stats, &fentry_key, sizeof(fentry_key),
                                     &fentry_ns, sizeof(fentry_ns), 0) == 0) 
            {
                std::cout << "[C++] Kprobe total: " << kprobe_ns << " ns | Fentry total: " 
                          << fentry_ns << " ns\n";
            }
        }
    } 
    catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
