// loader.cpp — Сучасна C++20 RAII імплементація демона моніторингу
#include <iostream>
#include <memory>
#include <stdexcept>
#include <csignal>
#include <atomic>
#include <thread>
#include <chrono>
#include <bpf/libbpf.h>
#include "lsm_policy.skel.h"

namespace {
    std::atomic<bool> g_stop_requested{false};

    void signal_handler(int) {
        g_stop_requested.store(true);
    }
}

// Клас-менеджер політики BPF-LSM із використанням принципу RAII (Resource Acquisition Is Initialization)
class BpfPolicyManager {
public:
    BpfPolicyManager() {
        // 1. Відкриваємо та завантажуємо BPF об'єкт
        skel_ = lsm_policy_bpf__open_and_load();
        if (!skel_) {
            throw std::runtime_error("Failed to open and load eBPF skeleton");
        }

        // 2. Прикріплюємо BPF Link до LSM хука
        int err = lsm_policy_bpf__attach(skel_);
        if (err) {
            lsm_policy_bpf__destroy(skel_);
            throw std::runtime_error("Failed to attach eBPF LSM hooks to kernel");
        }

        // 3. Створюємо споживача Ring Buffer
        rb_ = ring_buffer__new(bpf_map__fd(skel_->maps.audit_ringbuf),
                               &BpfPolicyManager::on_event, this, nullptr);
        if (!rb_) {
            lsm_policy_bpf__destroy(skel_);
            throw std::runtime_error("Failed to initialize eBPF Ring Buffer consumer");
        }
    }

    // Деструктор гарантує 100% від'єднання політики з ядра при виході з області видимості
    ~BpfPolicyManager() {
        if (rb_) {
            ring_buffer__free(rb_);
        }
        if (skel_) {
            lsm_policy_bpf__destroy(skel_);
        }
        std::cout << "[RAII Destructor] BPF-LSM Policy detached and resources freed." << std::endl;
    }

    // Забороняємо копіювання об'єкта (Move-only)
    BpfPolicyManager(const BpfPolicyManager&) = delete;
    BpfPolicyManager& operator=(const BpfPolicyManager&) = delete;

    // Метод опитування кільцевого буфера
    void poll(int timeout_ms = 100) {
        if (rb_) {
            int err = ring_buffer__poll(rb_, timeout_ms);
            if (err < 0 && err != -EINTR) {
                throw std::runtime_error("Error during ring buffer polling: " + std::to_string(err));
            }
        }
    }

private:
    // Статичний callback метод обробки подій
    static int on_event(void *ctx, void *data, size_t data_sz) {
        auto *evt = static_cast<const audit_event*>(data);
        
        std::cout << "[C++ AUDIT] PID: " << evt->pid 
                  << " | PPID: " << evt->ppid 
                  << " | UID: " << evt->uid 
                  << " | Comm: " << evt->comm 
                  << " | Status: " << (evt->blocked ? "DENIED" : "ALLOWED")
                  << " | File: " << evt->filename 
                  << std::endl;
        return 0;
    }

    struct lsm_policy_bpf *skel_{nullptr};
    struct ring_buffer *rb_{nullptr};
};

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        BpfPolicyManager manager;
        std::cout << "BPF-LSM C++ Protection Manager running. Press Ctrl+C to exit." << std::endl;

        while (!g_stop_requested.load()) {
            manager.poll(100);
        }
    } catch (const std::exception &ex) {
        std::cerr << "Fatal Exception: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
