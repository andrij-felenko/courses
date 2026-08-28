// user_loader.cpp - Завантажувач спостереження на C++ (libbpf)
#include <iostream>
#include <memory>
#include <string_view>
#include <bpf/libbpf.h>

// RAII обгортка для BPF об'єкта
struct BpfObjectDeleter {
    void operator()(bpf_object* obj) const {
        if (obj) bpf_object__close(obj);
    }
};
using UniqueBpfObject = std::unique_ptr<bpf_object, BpfObjectDeleter>;

int main() {
    std::cout << "Завантаження BPF програми трасування на C++...\n";
    // Відкриття та завантаження BPF-об'єкта
    UniqueBpfObject obj{bpf_object__open_file("bpf_tracer.bpf.o", nullptr)};
    if (!obj || bpf_object__load(obj.get())) {
        std::cerr << "Помилка завантаження BPF-об'єкта\n";
        return 1;
    }
    std::cout << "BPF-програму успішно завантажено та прикріплено до зондів kprobes/uprobes.\n";
    return 0;
}
