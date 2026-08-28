#include <iostream>
#include <memory>
#include <string_view>
#include <stdexcept>
#include <chrono>
#include <thread>
#include <net/if.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

// RAII обгортка для bpf_object
struct BpfObjectDeleter {
    void operator()(bpf_object* obj) const noexcept {
        if (obj) {
            bpf_object__close(obj);
        }
    }
};

using BpfObjectPtr = std::unique_ptr<bpf_object, BpfObjectDeleter>;

class XdpRouterManager {
public:
    XdpRouterManager(std::string_view rx_ifname, std::string_view tx_ifname)
        : rx_ifname_(rx_ifname), tx_ifname_(tx_ifname) {
        
        rx_ifindex_ = if_nametoindex(rx_ifname_.data());
        tx_ifindex_ = if_nametoindex(tx_ifname_.data());

        if (rx_ifindex_ == 0 || tx_ifindex_ == 0) {
            throw std::runtime_error("Не вдалося знайти системний індекс мережевого інтерфейсу");
        }
    }

    void load_and_attach(std::string_view bpf_obj_path) {
        bpf_obj_.reset(bpf_object__open_file(bpf_obj_path.data(), nullptr));
        if (!bpf_obj_) {
            throw std::runtime_error("Неможливо відкрити файл BPF об'єкта");
        }

        if (bpf_object__load(bpf_obj_.get()) != 0) {
            throw std::runtime_error("Помилка завантаження eBPF програмою у ядро");
        }

        configure_maps();
        attach_xdp();
    }

    ~XdpRouterManager() {
        if (attached_ && rx_ifindex_ != 0) {
            DECLARE_LIBBPF_OPTS(bpf_xdp_attach_opts, opts);
            bpf_xdp_detach(rx_ifindex_, 0, &opts);
            std::cout << "[RAII] XDP програму відкріплено від інтерфейсу.\n";
        }
    }

private:
    void configure_maps() {
        int cpu_map_fd = bpf_object__find_map_fd_by_name(bpf_obj_.get(), "cpu_map");
        int dev_map_fd = bpf_object__find_map_fd_by_name(bpf_obj_.get(), "tx_dev_map");

        if (cpu_map_fd < 0 || dev_map_fd < 0) {
            throw std::runtime_error("Не знайдено необхідних карт CPUMAP чи DEVMAP");
        }

        // Конфігурація CPUMAP (цільовий CPU 1, qsize 2048)
        struct bpf_cpumap_val cpu_val{};
        cpu_val.qsize = 2048;
        cpu_val.bpf_prog.fd = 0;
        uint32_t cpu_key = 1;

        if (bpf_map_update_elem(cpu_map_fd, &cpu_key, &cpu_val, BPF_ANY) < 0) {
            throw std::runtime_error("Помилка ініціалізації елемента CPUMAP");
        }

        // Конфігурація DEVMAP (вихідний ifindex)
        struct bpf_devmap_val dev_val{};
        dev_val.ifindex = tx_ifindex_;
        dev_val.bpf_prog.fd = 0;
        uint32_t dev_key = tx_ifindex_;

        if (bpf_map_update_elem(dev_map_fd, &dev_key, &dev_val, BPF_ANY) < 0) {
            throw std::runtime_error("Помилка ініціалізації елемента DEVMAP");
        }
    }

    void attach_xdp() {
        bpf_program* prog = bpf_object__find_program_by_name(bpf_obj_.get(), "xdp_router_entry");
        if (!prog) {
            throw std::runtime_error("Не знайдено XDP-функцію xdp_router_entry у BPF-об'єкті");
        }

        int prog_fd = bpf_program__fd(prog);
        DECLARE_LIBBPF_OPTS(bpf_xdp_attach_opts, opts);

        if (bpf_xdp_attach(rx_ifindex_, prog_fd, XDP_FLAGS_UPDATE_IF_NOEXIST, &opts) < 0) {
            throw std::runtime_error("Помилка прив'язки XDP програми до вхідного мережевого порту");
        }

        attached_ = true;
        std::cout << "Успішно запущено XDP-маршрутизатор [C++] (" << rx_ifname_ << " -> " << tx_ifname_ << ")\n";
    }

    std::string rx_ifname_;
    std::string tx_ifname_;
    unsigned int rx_ifindex_{0};
    unsigned int tx_ifindex_{0};
    BpfObjectPtr bpf_obj_{nullptr};
    bool attached_{false};
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <rx_ifname> <tx_ifname>\n";
        return EXIT_FAILURE;
    }

    try {
        XdpRouterManager router(argv[1], argv[2]);
        router.load_and_attach("xdp_router_kern.o");

        std::cout << "Маршрутизатор працює. Натисніть Ctrl+C для завершення...\n";
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
