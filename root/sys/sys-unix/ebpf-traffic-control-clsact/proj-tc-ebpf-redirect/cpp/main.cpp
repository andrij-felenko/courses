#include <iostream>
#include <string_view>
#include <stdexcept>
#include <memory>
#include <system_error>
#include <net/if.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

// RAII клас для керування життєвим циклом eBPF TC clsact програми
class BpfTcManager {
public:
    BpfTcManager(std::string_view src_if, std::string_view target_if) {
        src_ifindex_ = if_nametoindex(src_if.data());
        target_ifindex_ = if_nametoindex(target_if.data());

        if (src_ifindex_ == 0 || target_ifindex_ == 0) {
            throw std::system_error(errno, std::generic_category(), "Невідомий мережевий інтерфейс у системі");
        }

        // 1. Відкриваємо BPF ELF об'єктний файл
        obj_ = bpf_object__open_file("tc_redirect_kern.o", nullptr);
        if (libbpf_get_error(obj_)) {
            throw std::runtime_error("Не вдалося відкрити eBPF ELF об'єктний файл");
        }

        // 2. Завантажуємо байт-код у ядро (проходження BPF Verifier)
        if (bpf_object__load(obj_)) {
            bpf_object__close(obj_);
            throw std::runtime_error("Помилка BPF Verifier при завантаженні eBPF у ядро");
        }

        setup_map();
        attach_tc();
    }

    ~BpfTcManager() noexcept {
        // Гарантоване відкріплення BPF фільтра при руйнуванні об'єкта або винятку
        if (attached_) {
            opts_.prog_fd = 0;
            opts_.prog_id = 0;
            bpf_tc_detach(&hook_, &opts_);
        }
        if (obj_) {
            bpf_object__close(obj_);
        }
    }

    // Забороняємо копіювання об'єкта (строгий RAII ресурс)
    BpfTcManager(const BpfTcManager&) = delete;
    BpfTcManager& operator=(const BpfTcManager&) = delete;

private:
    void setup_map() {
        auto* map = bpf_object__find_map_by_name(obj_, "config_map");
        int map_fd = bpf_map__fd(map);
        std::uint32_t key = 0;
        std::uint32_t val = target_ifindex_;

        if (bpf_map_update_elem(map_fd, &key, &val, BPF_ANY) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося оновити конфігураційну BPF карту");
        }
    }

    void attach_tc() {
        auto* prog = bpf_object__find_program_by_name(obj_, "tc_redirect_func");
        int prog_fd = bpf_program__fd(prog);

        hook_.sz = sizeof(struct bpf_tc_hook);
        hook_.ifindex = src_ifindex_;
        hook_.attach_point = BPF_TC_INGRESS;

        opts_.sz = sizeof(struct bpf_tc_opts);
        opts_.prog_fd = prog_fd;

        // Створюємо qdisc clsact (операція є ідемпотентною)
        int err = bpf_tc_hook_create(&hook_);
        if (err && err != -EEXIST) {
            throw std::system_error(-err, std::generic_category(), "Не вдалося створити clsact qdisc");
        }

        // Прикріплюємо фільтр direct-action
        err = bpf_tc_attach(&hook_, &opts_);
        if (err) {
            throw std::system_error(-err, std::generic_category(), "Не вдалося прикріпити TC BPF filter");
        }
        attached_ = true;
    }

    unsigned int src_ifindex_{0};
    unsigned int target_ifindex_{0};
    struct bpf_object* obj_{nullptr};
    struct bpf_tc_hook hook_{};
    struct bpf_tc_opts opts_{};
    bool attached_{false};
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <src_ifname> <target_ifname>\n";
        return 1;
    }

    try {
        BpfTcManager manager(argv[1], argv[2]);
        std::cout << "eBPF TC clsact прикріплено у режимі RAII. Натисніть Enter для виходу...\n";
        std::cin.get();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
