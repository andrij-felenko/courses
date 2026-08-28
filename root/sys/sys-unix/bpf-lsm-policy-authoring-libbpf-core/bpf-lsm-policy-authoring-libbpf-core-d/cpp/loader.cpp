// loader.cpp — C++20 RAII імплементація завантажувача
#include <iostream>
#include <memory>
#include <stdexcept>
#include <thread>
#include <chrono>
#include <csignal>
#include <atomic>
#include <bpf/libbpf.h>
#include "block_chmod.skel.h"

namespace {
    std::atomic<bool> g_running{true};

    void sig_handler(int) {
        g_running.store(false);
    }
}

class BpfLsmGuard {
public:
    BpfLsmGuard() {
        skel_ = block_chmod_bpf__open_and_load();
        if (!skel_) {
            throw std::runtime_error("Failed to open and load eBPF skeleton");
        }

        int err = block_chmod_bpf__attach(skel_);
        if (err) {
            block_chmod_bpf__destroy(skel_);
            throw std::runtime_error("Failed to attach BPF-LSM hooks");
        }
    }

    ~BpfLsmGuard() {
        if (skel_) {
            block_chmod_bpf__destroy(skel_);
            std::cout << "[RAII] BPF-LSM Policy safely detached from kernel." << std::endl;
        }
    }

    BpfLsmGuard(const BpfLsmGuard&) = delete;
    BpfLsmGuard& operator=(const BpfLsmGuard&) = delete;

private:
    struct block_chmod_bpf *skel_{nullptr};
};

int main() {
    std::signal(SIGINT, sig_handler);
    std::signal(SIGTERM, sig_handler);

    try {
        BpfLsmGuard guard;
        std::cout << "BPF-LSM Protection Daemon running. Ctrl+C to terminate." << std::endl;

        while (g_running.load()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }
    } catch (const std::exception &e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
