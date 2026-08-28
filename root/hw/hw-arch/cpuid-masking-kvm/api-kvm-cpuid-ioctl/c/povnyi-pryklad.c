#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

struct kvm_cpuid2* kvm_alloc_cpuid(uint32_t nent) {
    size_t size = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
    struct kvm_cpuid2* cpuid = (struct kvm_cpuid2*)malloc(size);
    if (cpuid) {
        memset(cpuid, 0, size);
        cpuid->nent = nent;
    }
    return cpuid;
}

struct kvm_cpuid2* get_host_supported_cpuid(int kvm_fd) {
    uint32_t nent = 64;
    struct kvm_cpuid2* cpuid = kvm_alloc_cpuid(nent);
    if (!cpuid) return NULL;

    while (ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
        if (errno == E2BIG) {
            nent = cpuid->nent; // Ядро записало точну необхідну кількість
            free(cpuid);
            cpuid = kvm_alloc_cpuid(nent);
            if (!cpuid) return NULL;
            continue;
        }
        perror("Помилка KVM_GET_SUPPORTED_CPUID");
        free(cpuid);
        return NULL;
    }
    return cpuid;
}

int apply_vcpu_cpuid_configuration(int vcpu_fd, struct kvm_cpuid2* cpuid) {
    // Модифікація прапорців перед завантаженням
    for (uint32_t i = 0; i < cpuid->nent; ++i) {
        struct kvm_cpuid_entry2* entry = &cpuid->entries[i];

        // Маскуємо векторні інструкції AVX-512 для сумісності міграції
        if (entry->function == 7 && entry->index == 0) {
            entry->ebx &= ~(1U << 16); // AVX512F
            entry->ebx &= ~(1U << 17); // AVX512DQ
            entry->ebx &= ~(1U << 30); // AVX512BW
        }
    }

    if (ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
        perror("Помилка KVM_SET_CPUID2");
        return -1;
    }
    return 0;
}
