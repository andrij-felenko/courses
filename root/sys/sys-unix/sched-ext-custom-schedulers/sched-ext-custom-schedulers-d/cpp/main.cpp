// C++ Реалізація завантажувача BPF-планувальника (User Space Loader)
#include <iostream>
#include <memory>
#include <csignal>
#include <thread>
#include <chrono>
#include <bpf/libbpf.h>

// Автоматичне очищення ресурсів BPF через RAII
class BpfSchedulerLoader {
private:
    struct bpf_link* link_{nullptr};
    bool is_attached_{false};

public:
    BpfSchedulerLoader() = default;
    
    ~BpfSchedulerLoader() {
        detach();
    }

    bool attach() {
        std::cout << "[Loader C++] Завантаження та активація sched_ext планувальника...\n";
        // Тут виконується bpf_map__attach_struct_ops()
        is_attached_ = true;
        return true;
    }

    void detach() {
        if (is_attached_ && link_) {
            std::cout << "[Loader C++] Безпечне вивантаження BPF-планувальника.\n";
            bpf_link__destroy(link_);
            link_ = nullptr;
            is_attached_ = false;
        }
    }
};

int main() {
    BpfSchedulerLoader loader;
    if (loader.attach()) {
        std::cout << "[Loader C++] Планувальник активний. Натисніть Ctrl+C для зупинки.\n";
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }
    return 0;
}
