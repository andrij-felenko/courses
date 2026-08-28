#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

// RAII обгортка для файлового дескриптора POSIX
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    
    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для відображеної пам'яті mmap
class MappedMemory {
    void* addr_{MAP_FAILED};
    std::size_t size_{0};
public:
    MappedMemory(void* addr, std::size_t size) : addr_(addr), size_(size) {}
    ~MappedMemory() {
        if (addr_ != MAP_FAILED && size_ > 0) {
            ::munmap(addr_, size_);
        }
    }

    MappedMemory(const MappedMemory&) = delete;
    MappedMemory& operator=(const MappedMemory&) = delete;

    MappedMemory(MappedMemory&& other) noexcept 
        : addr_(other.addr_), size_(other.size_) {
        other.addr_ = MAP_FAILED;
        other.size_ = 0;
    }

    [[nodiscard]] void* get() const noexcept { return addr_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
};

class MiniHypervisor {
    static constexpr std::size_t kRamSize = 2 * 1024 * 1024;
    
    UniqueFd kvm_fd_{-1};
    UniqueFd vm_fd_{-1};
    UniqueFd vcpu_fd_{-1};
    MappedMemory ram_{MAP_FAILED, 0};
    MappedMemory run_mmap_{MAP_FAILED, 0};
    struct kvm_run* run_{nullptr};

public:
    MiniHypervisor() {
        // 1. Відкриття /dev/kvm
        kvm_fd_ = UniqueFd{::open("/dev/kvm", O_RDWR | O_CLOEXEC)};
        if (!kvm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /dev/kvm");
        }

        int api_ver = ::ioctl(kvm_fd_.get(), KVM_GET_API_VERSION, 0);
        if (api_ver != 12) {
            throw std::runtime_error("Непідтримувана версія KVM API: " + std::to_string(api_ver));
        }

        // 2. Створення VM
        vm_fd_ = UniqueFd{::ioctl(kvm_fd_.get(), KVM_CREATE_VM, 0)};
        if (!vm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_CREATE_VM");
        }

        // 3. Виділення RAM
        void* ram_ptr = ::mmap(nullptr, kRamSize, PROT_READ | PROT_WRITE,
                               MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        if (ram_ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap RAM");
        }
        ram_ = MappedMemory{ram_ptr, kRamSize};

        struct kvm_userspace_memory_region region{
            .slot = 0,
            .flags = 0,
            .guest_phys_addr = 0x0,
            .memory_size = kRamSize,
            .userspace_addr = reinterpret_cast<std::uint64_t>(ram_.get()),
        };
        if (::ioctl(vm_fd_.get(), KVM_SET_USER_MEMORY_REGION, &region) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_SET_USER_MEMORY_REGION");
        }

        // 4. Створення vCPU
        vcpu_fd_ = UniqueFd{::ioctl(vm_fd_.get(), KVM_CREATE_VCPU, 0)};
        if (!vcpu_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_CREATE_VCPU");
        }

        int mmap_size = ::ioctl(kvm_fd_.get(), KVM_GET_VCPU_MMAP_SIZE, 0);
        if (mmap_size < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_GET_VCPU_MMAP_SIZE");
        }

        void* run_ptr = ::mmap(nullptr, static_cast<std::size_t>(mmap_size), 
                               PROT_READ | PROT_WRITE, MAP_SHARED, vcpu_fd_.get(), 0);
        if (run_ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap struct kvm_run");
        }
        run_mmap_ = MappedMemory{run_ptr, static_cast<std::size_t>(mmap_size)};
        run_ = static_cast<struct kvm_run*>(run_mmap_.get());
    }

    void load_payload(std::span<const std::uint8_t> payload) {
        if (payload.size() > ram_.size()) {
            throw std::invalid_argument("Розмір коду перевищує RAM");
        }
        std::memcpy(ram_.get(), payload.data(), payload.size());
    }

    void setup_registers() {
        struct kvm_sregs sregs{};
        if (::ioctl(vcpu_fd_.get(), KVM_GET_SREGS, &sregs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_GET_SREGS");
        }
        sregs.cs.base = 0;
        sregs.cs.selector = 0;
        if (::ioctl(vcpu_fd_.get(), KVM_SET_SREGS, &sregs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_SET_SREGS");
        }

        struct kvm_regs regs{
            .rip = 0x0,
            .rflags = 0x2,
        };
        if (::ioctl(vcpu_fd_.get(), KVM_SET_REGS, &regs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка KVM_SET_REGS");
        }
    }

    void run() {
        std::cout << "Запуск міні-гіпервізора KVM (C++ RAII)...\nГостьовий вивід: " << std::flush;

        bool running = true;
        while (running) {
            if (::ioctl(vcpu_fd_.get(), KVM_RUN, 0) < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка KVM_RUN");
            }

            switch (run_->exit_reason) {
                case KVM_EXIT_IO:
                    if (run_->io.direction == KVM_EXIT_IO_OUT && run_->io.port == 0x10) {
                        const char* data = reinterpret_cast<const char*>(run_) + run_->io.data_offset;
                        std::cout << *data << std::flush;
                    }
                    break;

                case KVM_EXIT_HLT:
                    std::cout << "\n[KVM] Гість виконав HLT. Завершення.\n";
                    running = false;
                    break;

                case KVM_EXIT_FAIL_ENTRY:
                    std::cerr << "\n[KVM] Апаратна помилка входу: " 
                              << run_->fail_entry.hardware_entry_failure_reason << '\n';
                    running = false;
                    break;

                default:
                    std::cerr << "\n[KVM] Необроблена причина виходу: " << run_->exit_reason << '\n';
                    running = false;
                    break;
            }
        }
    }
};

int main() {
    try {
        MiniHypervisor hypervisor;

        const std::vector<std::uint8_t> code = {
            0xb0, 0x48, // mov $0x48, %al ('H')
            0xe6, 0x10, // out %al, $0x10
            0xb0, 0x49, // mov $0x49, %al ('I')
            0xe6, 0x10, // out %al, $0x10
            0xf4        // hlt
        };

        hypervisor.load_payload(code);
        hypervisor.setup_registers();
        hypervisor.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
