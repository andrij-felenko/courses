#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/eventfd.h>
#include <linux/kvm.h>

// RAII обгортка для безпечного керування системними дескрипторами Linux
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

// Контролер життєвого циклу підсистеми віртуальних переривань KVM
class KvmIrqPipeline {
public:
    KvmIrqPipeline() {
        kvm_fd_.reset(::open("/dev/kvm", O_RDWR | O_CLOEXEC));
        if (!kvm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Відкриття /dev/kvm невдале");
        }

        vm_fd_.reset(::ioctl(kvm_fd_.get(), KVM_CREATE_VM, 0));
        if (!vm_fd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "KVM_CREATE_VM помилка створення VM");
        }

        // 1. Створюємо in-kernel irqchip
        if (::ioctl(vm_fd_.get(), KVM_CREATE_IRQCHIP, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_CREATE_IRQCHIP помилка");
        }

        // 2. Створюємо non-blocking eventfd
        irq_efd_.reset(::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC));
        if (!irq_efd_.valid()) {
            throw std::system_error(errno, std::generic_category(), "Створення eventfd невдале");
        }
    }

    void setupRoutingAndIrqfd(uint32_t target_gsi, uint32_t ioapic_pin) {
        // 3. Формуємо динамічний буфер під структуру KVM маршрутизації
        std::vector<uint8_t> buffer(sizeof(struct kvm_irq_routing) + sizeof(struct kvm_irq_routing_entry), 0);
        auto* routing = reinterpret_cast<struct kvm_irq_routing*>(buffer.data());

        routing->nr = 1;
        routing->flags = 0;
        routing->entries[0].gsi = target_gsi;
        routing->entries[0].type = KVM_IRQ_ROUTING_IRQCHIP;
        routing->entries[0].u.irqchip.irqchip = KVM_IRQCHIP_IOAPIC;
        routing->entries[0].u.irqchip.pin = ioapic_pin;

        if (::ioctl(vm_fd_.get(), KVM_SET_GSI_ROUTING, routing) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_SET_GSI_ROUTING помилка");
        }

        // 4. Прив'язуємо eventfd до GSI лінії
        std::memset(&irqfd_cfg_, 0, sizeof(irqfd_cfg_));
        irqfd_cfg_.fd = irq_efd_.get();
        irqfd_cfg_.gsi = target_gsi;
        irqfd_cfg_.flags = 0;

        if (::ioctl(vm_fd_.get(), KVM_IRQFD, &irqfd_cfg_) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_IRQFD помилка реєстрації");
        }
        gsi_bound_ = true;
    }

    void triggerInterrupt() const {
        uint64_t val = 1;
        ssize_t bytes = ::write(irq_efd_.get(), &val, sizeof(val));
        if (bytes != sizeof(val)) {
            throw std::system_error(errno, std::generic_category(), "Запис у дескриптор eventfd невдалий");
        }
    }

    ~KvmIrqPipeline() {
        // Гарантоване відв'язування IRQFD перед закриттям дескрипторів
        if (gsi_bound_ && vm_fd_.valid()) {
            irqfd_cfg_.flags = KVM_IRQFD_FLAG_DEASSIGN;
            ::ioctl(vm_fd_.get(), KVM_IRQFD, &irqfd_cfg_);
        }
    }

private:
    UniqueFd kvm_fd_;
    UniqueFd vm_fd_;
    UniqueFd irq_efd_;
    struct kvm_irqfd irqfd_cfg_{};
    bool gsi_bound_{false};
};

int main() {
    try {
        KvmIrqPipeline pipeline;
        constexpr uint32_t test_gsi = 4;
        pipeline.setupRoutingAndIrqfd(test_gsi, 4);

        std::cout << "[Host] C++ RAII пайплайн налаштовано для GSI " << test_gsi << ".\n";

        std::thread worker([&pipeline]() {
            for (int i = 0; i < 5; ++i) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                pipeline.triggerInterrupt();
                std::cout << "[Worker] Асинхронне переривання #" << (i + 1) << " доставлено в KVM!\n";
            }
        });

        worker.join();
        std::cout << "[Host] Усі події оброблено. Автоматичне завершення.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Виняткова ситуація: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
