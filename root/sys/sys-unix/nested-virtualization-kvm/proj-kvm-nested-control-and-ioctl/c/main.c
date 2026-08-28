#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

#define VMX_BIT (1 << 5)  /* CPUID.01H:ECX bit 5 */
#define SVM_BIT (1 << 2)  /* CPUID.80000001H:ECX bit 2 */

static int check_sysfs_nested(const char *module_name) {
    char path[128];
    snprintf(path, sizeof(path), "/sys/module/%s/parameters/nested", module_name);
    
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }
    
    char buf[8] = {0};
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    
    if (n > 0) {
        if (buf[0] == 'Y' || buf[0] == 'y' || buf[0] == '1') {
            return 1;
        }
        return 0;
    }
    return -1;
}

int main(void) {
    int kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return EXIT_FAILURE;
    }

    int api_ver = ioctl(kvm_fd, KVM_GET_API_VERSION, 0);
    if (api_ver != KVM_API_VERSION) {
        fprintf(stderr, "Невідповідність KVM API: очікується %d, отримано %d\n", KVM_API_VERSION, api_ver);
        close(kvm_fd);
        return EXIT_FAILURE;
    }

    /* Виділяємо пам'ять під 64 записи CPUID */
    int nent = 64;
    size_t sz = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
    struct kvm_cpuid2 *cpuid = (struct kvm_cpuid2 *)malloc(sz);
    if (!cpuid) {
        perror("Помилка виділення пам'яті");
        close(kvm_fd);
        return EXIT_FAILURE;
    }

    memset(cpuid, 0, sz);
    cpuid->nent = nent;

    if (ioctl(kvm_fd, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
        perror("Помилка KVM_GET_SUPPORTED_CPUID");
        free(cpuid);
        close(kvm_fd);
        return EXIT_FAILURE;
    }

    int has_vmx = 0;
    int has_svm = 0;

    for (__u32 i = 0; i < cpuid->nent; i++) {
        if (cpuid->entries[i].function == 0x01) {
            if (cpuid->entries[i].ecx & VMX_BIT) {
                has_vmx = 1;
            }
        } else if (cpuid->entries[i].function == 0x80000001) {
            if (cpuid->entries[i].ecx & SVM_BIT) {
                has_svm = 1;
            }
        }
    }

    printf("=== Перевірка апаратних розширень у KVM ===\n");
    printf("Intel VT-x (VMX) у CPUID: %s\n", has_vmx ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ");
    printf("AMD-V (SVM) у CPUID:     %s\n", has_svm ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ");

    int sysfs_intel = check_sysfs_nested("kvm_intel");
    int sysfs_amd = check_sysfs_nested("kvm_amd");

    printf("\n=== Стан sysfs nested у хостовому ядрі ===\n");
    if (sysfs_intel >= 0) {
        printf("kvm_intel.nested: %s\n", sysfs_intel ? "УВІМКНЕНО (1/Y)" : "ВИМКНЕНО (0/N)");
    }
    if (sysfs_amd >= 0) {
        printf("kvm_amd.nested:   %s\n", sysfs_amd ? "УВІМКНЕНО (1/Y)" : "ВИМКНЕНО (0/N)");
    }

    free(cpuid);
    close(kvm_fd);
    return EXIT_SUCCESS;
}
