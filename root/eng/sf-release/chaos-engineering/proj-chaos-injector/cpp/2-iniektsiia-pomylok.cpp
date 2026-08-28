// Простір користувача: C++20 RAII-завантажувач eBPF (ChaosBpfLoader.hpp)
#include <memory>
#include <stdexcept>
#include <string_view>
#include <format>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

class ChaosBpfManager {
public:
    explicit ChaosBpfManager(uint32_t target_pid) : target_pid_(target_pid) {
        skel_ = bpf_object__open_file("kprobe_connect.bpf.o", nullptr);
        if (!skel_) {
            throw std::runtime_error("Не вдалося відкрити eBPF об'єкт");
        }

        if (bpf_object__load(skel_) < 0) {
            bpf_object__close(skel_);
            throw std::runtime_error("Помилка завантаження eBPF програми в ядро");
        }

        // Прив'язка kprobe до системного виклику connect
        prog_ = bpf_object__find_program_by_name(skel_, "trace_connect");
        link_ = bpf_program__attach(prog_);
        if (!link_) {
            bpf_object__close(skel_);
            throw std::runtime_error("Не вдалося підключити eBPF kprobe hook");
        }
    }

    ~ChaosBpfManager() noexcept {
        if (link_) bpf_link__destroy(link_);
        if (skel_) bpf_object__close(skel_);
    }

    ChaosBpfManager(const ChaosBpfManager&) = delete;
    ChaosBpfManager& operator=(const ChaosBpfManager&) = delete;
    ChaosBpfManager(ChaosBpfManager&& other) noexcept 
        : skel_(other.skel_), prog_(other.prog_), link_(other.link_), target_pid_(other.target_pid_) {
        other.skel_ = nullptr;
        other.link_ = nullptr;
    }

private:
    struct bpf_object* skel_{nullptr};
    struct bpf_program* prog_{nullptr};
    struct bpf_link* link_{nullptr};
    uint32_t target_pid_{0};
};
