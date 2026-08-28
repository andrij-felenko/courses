// loader.cpp — Ідіоматичний завантажувач C++20 із використанням RAII
#include <iostream>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <unistd.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

namespace cgroup_fw {

// RAII обгортка для файлових дескрипторів POSIX
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& rhs) noexcept : fd_(rhs.fd_) { rhs.fd_ = -1; }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для BPF-об'єкта libbpf
struct BpfObjectDeleter {
    void operator()(struct bpf_object* obj) const noexcept {
        if (obj) {
            ::bpf_object__close(obj);
        }
    }
};
using BpfObjectPtr = std::unique_ptr<struct bpf_object, BpfObjectDeleter>;

class FirewallManager {
    FileDescriptor cgroup_fd_;
    BpfObjectPtr bpf_obj_;
    int prog_fd_{-1};
    int map_fd_{-1};

public:
    FirewallManager(std::string_view cgroup_path, std::string_view bpf_obj_path)
        : cgroup_fd_(::open(cgroup_path.data(), O_RDONLY))
    {
        if (!cgroup_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити каталог cgroup");
        }

        bpf_obj_.reset(::bpf_object__open_file(bpf_obj_path.data(), nullptr));
        if (!bpf_obj_) {
            throw std::runtime_error("Не вдалося відкрити eBPF об'єктний файл");
        }

        if (::bpf_object__load(bpf_obj_.get()) != 0) {
            throw std::runtime_error("Не вдалося завантажити eBPF програму в ядро");
        }

        auto* prog = ::bpf_object__find_program_by_name(bpf_obj_.get(), "cgroup_egress_firewall");
        if (!prog) {
            throw std::runtime_error("Не вдалося знайти програму cgroup_egress_firewall");
        }

        auto* map = ::bpf_object__find_map_by_name(bpf_obj_.get(), "blocklist");
        if (!map) {
            throw std::runtime_error("Не вдалося знайти мапу blocklist");
        }

        prog_fd_ = ::bpf_program__fd(prog);
        map_fd_ = ::bpf_map__fd(map);
    }

    void block_ip(std::string_view ip_str) {
        struct in_addr addr{};
        if (::inet_pton(AF_INET, ip_str.data(), &addr) != 1) {
            throw std::invalid_argument("Некоректний формат IP-адреси");
        }

        std::uint32_t key = addr.s_addr;
        std::uint64_t initial_count = 0;

        if (::bpf_map_update_elem(map_fd_, &key, &initial_count, BPF_ANY) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося оновити BPF мапу");
        }
    }

    void attach() {
        if (::bpf_prog_attach(prog_fd_, cgroup_fd_.get(), BPF_CGROUP_INET_EGRESS, BPF_F_ALLOW_MULTI) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося прикріпити BPF програму до cgroup");
        }
    }
};

} // namespace cgroup_fw

int main(int argc, char** argv)
{
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <cgroup_path> <ip_to_block>\n";
        return 1;
    }

    try {
        cgroup_fw::FirewallManager manager(argv[1], "cgroup_fw.bpf.o");
        manager.block_ip(argv[2]);
        manager.attach();

        std::cout << "Файрвол успішно активовано на cgroup '" << argv[1] 
                  << "'. Заблоковано IP: " << argv[2] << "\n";
        std::cout << "Натисніть Ctrl+C для завершення...\n";

        while (true) {
            ::sleep(5);
        }
    }
    catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
