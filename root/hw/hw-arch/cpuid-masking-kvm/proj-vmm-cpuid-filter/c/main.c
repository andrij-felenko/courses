#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

#define MAX_ENTRIES 256
#define GUEST_MEM_SIZE (2 * 1024 * 1024)

// Бітові маски розширень
#define LEAF1_ECX_HYPERVISOR (1U << 31)
#define LEAF7_EBX_AVX2       (1U << 5)
#define LEAF7_EBX_AVX512F    (1U << 16)
#define LEAF7_EBX_AVX512DQ   (1U << 17)
#define LEAF7_EBX_AVX512BW   (1U << 30)

typedef struct {
    int kvm_fd;
    int vm_fd;
    int vcpu_fd;
    uint8_t* guest_memory;
    struct kvm_run* run_state;
} MiniVmm;

// Динамічне отримання таблиці CPUID хоста
struct kvm_cpuid2* vmm_fetch_host_cpuid(int kvm_fd) {
    uint32_t nent = 64;
    struct kvm_cpuid2* cpuid = NULL;

    while (1) {
        size_t size = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
        cpuid = (struct kvm_cpuid2*)realloc(cpuid, size);
        if (!cpuid) {
            perror("realloc failed");
            return NULL;
        }
        memset(cpuid, 0, size);
        cpuid->nent = nent;

        if (ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) == 0) {
            return cpuid;
        }

        if (cpuid->nent > nent) {
            nent = cpuid->nent; // Отримуємо точну кількість від ядра
        } else {
            nent *= 2;
        }

        if (nent > MAX_ENTRIES) {
            fprintf(stderr, "Перевищено максимальну кількість записів CPUID\n");
            free(cpuid);
            return NULL;
        }
    }
}

// Застосування фільтрації та завантаження таблиці у vCPU
bool vmm_configure_vcpu_cpuid(int vcpu_fd, struct kvm_cpuid2* cpuid, uint32_t vcpu_id) {
    bool has_pv_sig = false;

    for (uint32_t i = 0; i < cpuid->nent; ++i) {
        struct kvm_cpuid_entry2* entry = &cpuid->entries[i];

        // 1. Листок 1: Встановлюємо біт присутності гіпервізора та APIC ID
        if (entry->function == 1) {
            entry->ecx |= LEAF1_ECX_HYPERVISOR;
            entry->ebx &= 0x00FFFFFF;
            entry->ebx |= ((vcpu_id & 0xFF) << 24);
        }

        // 2. Листок 7: Маскуємо AVX-512 під базову модель x86-64-v3
        if (entry->function == 7 && entry->index == 0) {
            entry->ebx &= ~LEAF7_EBX_AVX512F;
            entry->ebx &= ~LEAF7_EBX_AVX512DQ;
            entry->ebx &= ~LEAF7_EBX_AVX512BW;
            entry->ebx |= LEAF7_EBX_AVX2; // Гарантуємо наявність AVX2
        }

        // 3. Листок 0x40000000: KVM Signature
        if (entry->function == 0x40000000) {
            has_pv_sig = true;
            entry->eax = 0x40000001;
            entry->ebx = 0x4b4d564b; // "KVMK"
            entry->ecx = 0x564d4b56; // "VMKV"
            entry->edx = 0x0000004d; // "M\0\0\0"
        }

        // 4. Листок 0x40000001: KVM Features
        if (entry->function == 0x40000001) {
            entry->eax = (1U << 3) | (1U << 6); // kvm-clock | PV_EOI
            entry->ebx = 0;
            entry->ecx = 0;
            entry->edx = 0;
        }
    }

    // Якщо паравіртуального листка 0x40000000 не було у відповіді хоста — додаємо вручну
    if (!has_pv_sig && cpuid->nent < (MAX_ENTRIES - 2)) {
        struct kvm_cpuid_entry2* sig = &cpuid->entries[cpuid->nent++];
        sig->function = 0x40000000;
        sig->index = 0;
        sig->flags = 0;
        sig->eax = 0x40000001;
        sig->ebx = 0x4b4d564b;
        sig->ecx = 0x564d4b56;
        sig->edx = 0x0000004d;

        struct kvm_cpuid_entry2* feat = &cpuid->entries[cpuid->nent++];
        feat->function = 0x40000001;
        feat->index = 0;
        feat->flags = 0;
        feat->eax = (1U << 3) | (1U << 6);
        feat->ebx = 0;
        feat->ecx = 0;
        feat->edx = 0;
    }

    // Завантажуємо таблицю у vCPU через ioctl
    if (ioctl(vcpu_fd, KVM_SET_CPUID2, cpuid) < 0) {
        perror("KVM_SET_CPUID2 failed");
        return false;
    }
    return true;
}

int main(void) {
    MiniVmm vmm;
    memset(&vmm, 0, sizeof(vmm));

    vmm.kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (vmm.kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return 1;
    }

    vmm.vm_fd = ioctl(vmm.kvm_fd, KVM_CREATE_VM, 0);
    if (vmm.vm_fd < 0) {
        perror("KVM_CREATE_VM");
        close(vmm.kvm_fd);
        return 1;
    }

    vmm.vcpu_fd = ioctl(vmm.vm_fd, KVM_CREATE_VCPU, 0);
    if (vmm.vcpu_fd < 0) {
        perror("KVM_CREATE_VCPU");
        close(vmm.vm_fd);
        close(vmm.kvm_fd);
        return 1;
    }

    // Отримуємо та конфігуруємо CPUID
    struct kvm_cpuid2* cpuid = vmm_fetch_host_cpuid(vmm.kvm_fd);
    if (!cpuid) {
        fprintf(stderr, "Помилка отримання CPUID\n");
        return 1;
    }

    if (!vmm_configure_vcpu_cpuid(vmm.vcpu_fd, cpuid, 0)) {
        fprintf(stderr, "Помилка завантаження CPUID у vCPU 0\n");
        free(cpuid);
        return 1;
    }
    free(cpuid);

    printf("Успішно: CPUID відфільтровано під x86-64-v3, AVX-512 приховано, PV-листки налаштовано.\n");

    close(vmm.vcpu_fd);
    close(vmm.vm_fd);
    close(vmm.kvm_fd);
    return 0;
}
