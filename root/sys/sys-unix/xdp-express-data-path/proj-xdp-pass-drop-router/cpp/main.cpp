// C++20 Implementation: RAII XdpLoader Wrapper
#include <iostream>
#include <string_view>
#include <system_error>
#include <memory>
#include <thread>
#include <chrono>
#include <net/if.h>
#include <linux/if_link.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

class XdpLoader {
public:
    XdpLoader(std::string_view ifname, std::string_view bpf_path) 
        : ifname_(ifname) {
        ifindex_ = if_nametoindex(ifname_.c_str());
        if (ifindex_ == 0) {
            throw std::system_error(errno, std::generic_category(), "Невідомий мережевий інтерфейс");
        }

        bpf_obj_ = bpf_object__open_file(bpf_path.data(), nullptr);
        if (!bpf_obj_) {
            throw std::runtime_error("Не вдалося відкрити BPF об'єктний файл");
        }

        if (bpf_object__load(bpf_obj_)) {
            bpf_object__close(bpf_obj_);
            throw std::runtime_error("Помилка завантаження BPF програми у ядро (помилка верифікатора)");
        }

        struct bpf_program* prog = bpf_object__find_program_by_name(bpf_obj_, "xdp_router_filter");
        if (!prog) {
            bpf_object__close(bpf_obj_);
            throw std::runtime_error("Секцію програми xdp_router_filter не знайдено");
        }

        int prog_fd = bpf_program__fd(prog);
        attach_flags_ = XDP_FLAGS_DRV_MODE;
        
        int err = bpf_xdp_attach(ifindex_, prog_fd, attach_flags_, nullptr);
        if (err) {
            std::cout << "Native XDP не підтримується драйвером, перехід на Generic mode...\n";
            attach_flags_ = XDP_FLAGS_SKB_MODE;
            err = bpf_xdp_attach(ifindex_, prog_fd, attach_flags_, nullptr);
            if (err) {
                bpf_object__close(bpf_obj_);
                throw std::system_error(-err, std::generic_category(), "Помилка прив'язки bpf_xdp_attach");
            }
        }
        attached_ = true;
    }

    ~XdpLoader() {
        if (attached_) {
            bpf_xdp_detach(ifindex_, attach_flags_, nullptr);
            std::cout << "\nXDP програму відв'язано від мережевого інтерфейсу " << ifname_ << std::endl;
        }
        if (bpf_obj_) {
            bpf_object__close(bpf_obj_);
        }
    }

    // Забороняємо копіювання об'єкта для гарантії єдиного володіння (RAII)
    XdpLoader(const XdpLoader&) = delete;
    XdpLoader& operator=(const XdpLoader&) = delete;

    // Дозволяємо переміщення володіння (Move semantics)
    XdpLoader(XdpLoader&& other) noexcept 
        : ifname_(std::move(other.ifname_)), ifindex_(other.ifindex_), 
          bpf_obj_(other.bpf_obj_), attach_flags_(other.attach_flags_), 
          attached_(other.attached_) {
        other.attached_ = false;
        other.bpf_obj_ = nullptr;
    }

private:
    std::string ifname_;
    unsigned int ifindex_{0};
    struct bpf_object* bpf_obj_{nullptr};
    uint32_t attach_flags_{0};
    bool attached_{false};
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <interface> <bpf_obj_file>\n";
        return 1;
    }

    try {
        XdpLoader loader(argv[1], argv[2]);
        std::cout << "XDP програму завантажено! Натисніть Ctrl+C для виходу...\n";
        
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
