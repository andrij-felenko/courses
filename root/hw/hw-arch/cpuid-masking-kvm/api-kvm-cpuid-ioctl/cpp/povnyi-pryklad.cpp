#include <iostream>
#include <vector>
#include <memory>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

class KvmCpuidService {
public:
    static std::vector<kvm_cpuid_entry2> fetch_supported_cpuid(int kvm_fd) {
        uint32_t nent = 64;
        while (true) {
            size_t size = sizeof(kvm_cpuid2) + nent * sizeof(kvm_cpuid_entry2);
            auto buffer = std::make_unique<uint8_t[]>(size);
            auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buffer.get());
            std::memset(cpuid, 0, size);
            cpuid->nent = nent;

            if (::ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) == 0) {
                return std::vector<kvm_cpuid_entry2>(
                    cpuid->entries, cpuid->entries + cpuid->nent
                );
            }

            if (errno == E2BIG) {
                nent = cpuid->nent; // Отримуємо точний розмір від ядра
                continue;
            }

            throw std::system_error(errno, std::generic_category(), "KVM_GET_SUPPORTED_CPUID failed");
        }
    }

    static void configure_vcpu(int vcpu_fd, std::vector<kvm_cpuid_entry2>& entries) {
        for (auto& entry : entries) {
            if (entry.function == 7 && entry.index == 0) {
                entry.ebx &= ~(1U << 16); // Вимикаємо AVX512F
                entry.ebx &= ~(1U << 17); // Вимикаємо AVX512DQ
                entry.ebx &= ~(1U << 30); // Вимикаємо AVX512BW
            }
        }

        size_t size = sizeof(kvm_cpuid2) + entries.size() * sizeof(kvm_cpuid_entry2);
        auto buffer = std::make_unique<uint8_t[]>(size);
        auto* cpuid = reinterpret_cast<kvm_cpuid2*>(buffer.get());
        std::memset(cpuid, 0, size);

        cpuid->nent = static_cast<uint32_t>(entries.size());
        std::memcpy(cpuid->entries, entries.data(), entries.size() * sizeof(kvm_cpuid_entry2));

        if (::ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
            throw std::system_error(errno, std::generic_category(), "KVM_SET_CPUID2 failed");
        }
    }
};
