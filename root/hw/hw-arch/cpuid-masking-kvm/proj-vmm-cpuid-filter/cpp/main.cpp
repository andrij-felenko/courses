#include <iostream>
#include <vector>
#include <memory>
#include <string_view>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

class KvmHandle {
public:
    explicit KvmHandle(int fd) noexcept : fd_{fd} {}
    ~KvmHandle() { if (fd_ >= 0) ::close(fd_); }

    KvmHandle(const KvmHandle&) = delete;
    KvmHandle& operator=(const KvmHandle&) = delete;

    KvmHandle(KvmHandle&& other) noexcept : fd_{other.fd_} { other.fd_ = -1; }
    KvmHandle& operator=(KvmHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

class VmmCpuidPipeline {
public:
    static constexpr uint32_t kHypervisorBit = 1U << 31;
    static constexpr uint32_t kAvx2Bit       = 1U << 5;
    static constexpr uint32_t kAvx512FBit    = 1U << 16;
    static constexpr uint32_t kAvx512DQBit   = 1U << 17;
    static constexpr uint32_t kAvx512BWBit   = 1U << 30;

    static std::vector<kvm_cpuid_entry2> query_host_table(int kvm_fd) {
        uint32_t nent = 64;
        while (true) {
            size_t size = sizeof(kvm_cpuid2) + nent * sizeof(kvm_cpuid_entry2);
            auto buf = std::make_unique<uint8_t[]>(size);
            auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buf.get());
            std::memset(cpuid, 0, size);
            cpuid->nent = nent;

            if (::ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) == 0) {
                return std::vector<kvm_cpuid_entry2>(
                    cpuid->entries, cpuid->entries + cpuid->nent
                );
            }

            if (errno == E2BIG) {
                nent = cpuid->nent;
                continue;
            }

            throw std::system_error(errno, std::generic_category(), "KVM_GET_SUPPORTED_CPUID query error");
        }
    }

    static void apply_v3_profile(std::vector<kvm_cpuid_entry2>& table, uint32_t vcpu_id) {
        bool pv_leaf_present = false;

        for (auto& entry : table) {
            // Листок 1: Прапорець гіпервізора та APIC ID
            if (entry.function == 1) {
                entry.ecx |= kHypervisorBit;
                entry.ebx &= 0x00FFFFFF;
                entry.ebx |= ((vcpu_id & 0xFF) << 24);
            }

            // Листок 7: Маскування розширень AVX-512 під базову модель
            if (entry.function == 7 && entry.index == 0) {
                entry.ebx &= ~kAvx512FBit;
                entry.ebx &= ~kAvx512DQBit;
                entry.ebx &= ~kAvx512BWBit;
                entry.ebx |= kAvx2Bit;
            }

            // Листок 0x40000000: KVM Signature
            if (entry.function == 0x40000000) {
                pv_leaf_present = true;
                entry.eax = 0x40000001;
                entry.ebx = 0x4b4d564b; // "KVMK"
                entry.ecx = 0x564d4b56; // "VMKV"
                entry.edx = 0x0000004d; // "M\0\0\0"
            }

            // Листок 0x40000001: KVM Features
            if (entry.function == 0x40000001) {
                entry.eax = (1U << 3) | (1U << 6); // kvm-clock | PV_EOI
                entry.ebx = 0;
                entry.ecx = 0;
                entry.edx = 0;
            }
        }

        if (!pv_leaf_present) {
            kvm_cpuid_entry2 sig{};
            sig.function = 0x40000000;
            sig.eax = 0x40000001;
            sig.ebx = 0x4b4d564b;
            sig.ecx = 0x564d4b56;
            sig.edx = 0x0000004d;
            table.push_back(sig);

            kvm_cpuid_entry2 feat{};
            feat.function = 0x40000001;
            feat.eax = (1U << 3) | (1U << 6);
            table.push_back(feat);
        }
    }

    static void commit_to_vcpu(int vcpu_fd, const std::vector<kvm_cpuid_entry2>& table) {
        size_t size = sizeof(kvm_cpuid2) + table.size() * sizeof(kvm_cpuid_entry2);
        auto buf = std::make_unique<uint8_t[]>(size);
        auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buf.get());
        std::memset(cpuid, 0, size);

        cpuid->nent = static_cast<uint32_t>(table.size());
        std::memcpy(cpuid->entries, table.data(), table.size() * sizeof(kvm_cpuid_entry2));

        if (::ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_SET_CPUID2 commit failed");
        }
    }
};

int main() {
    try {
        KvmHandle kvm{::open("/dev/kvm", O_RDWR | O_CLOEXEC)};
        if (!kvm.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Cannot open /dev/kvm");
        }

        KvmHandle vm{::ioctl(kvm.get(), KVM_CREATE_VM, 0)};
        if (!vm.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Cannot create VM");
        }

        KvmHandle vcpu{::ioctl(vm.get(), KVM_CREATE_VCPU, 0)};
        if (!vcpu.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Cannot create vCPU");
        }

        // 1. Опитуємо хост
        auto table = VmmCpuidPipeline::query_host_table(kvm.get());

        // 2. Застосовуємо маскування x86-64-v3 та додаємо PV-листки
        VmmCpuidPipeline::apply_v3_profile(table, 0);

        // 3. Завантажуємо таблицю у віртуальний процесор
        VmmCpuidPipeline::commit_to_vcpu(vcpu.get(), table);

        std::cout << "KVM vCPU успішно налаштовано через ідіоматичний C++ RAII пайплайн.\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання VMM: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
