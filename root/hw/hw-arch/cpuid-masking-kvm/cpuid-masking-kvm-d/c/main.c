#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

void apply_cpuid_masking(struct kvm_cpuid2* cpuid, uint32_t vcpu_id) {
    for (uint32_t i = 0; i < cpuid->nent; ++i) {
        struct kvm_cpuid_entry2* entry = &cpuid->entries[i];

        // 1. Листок 1: Встановлюємо біт віртуалізації та віртуальний APIC ID
        if (entry->function == 1) {
            entry->ecx |= (1U << 31); // Біт присутності гіпервізора
            entry->ebx &= 0x00FFFFFF;
            entry->ebx |= ((vcpu_id & 0xFF) << 24); // Синтетичний APIC ID
        }

        // 2. Листок 7: Маскуємо AVX-512 під базову модель x86-64-v3
        if (entry->function == 7 && entry->index == 0) {
            entry->ebx &= ~(1U << 16); // Вимикаємо AVX512F
            entry->ebx &= ~(1U << 17); // Вимикаємо AVX512DQ
            entry->ebx &= ~(1U << 30); // Вимикаємо AVX512BW
            entry->ebx |= (1U << 5);   // Гарантуємо наявність AVX2
        }

        // 3. Листок 0x40000000: Синтезуємо сигнатуру "KVMKVMKVM\0\0\0"
        if (entry->function == 0x40000000) {
            entry->eax = 0x40000001; // Максимальний паравіртуальний листок
            entry->ebx = 0x4b4d564b; // "KVMK"
            entry->ecx = 0x564d4b56; // "VMKV"
            entry->edx = 0x0000004d; // "M\0\0\0"
        }
    }
}
