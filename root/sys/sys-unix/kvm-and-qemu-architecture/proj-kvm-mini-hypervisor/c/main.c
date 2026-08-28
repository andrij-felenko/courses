#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/kvm.h>

#define RAM_SIZE (2 * 1024 * 1024)

int main(void) {
    // 1. Відкриття /dev/kvm
    int kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return 1;
    }

    // Перевірка версії API KVM
    int api_ver = ioctl(kvm_fd, KVM_GET_API_VERSION, 0);
    if (api_ver != 12) {
        fprintf(stderr, "Непідтримувана версія KVM API: %d\n", api_ver);
        close(kvm_fd);
        return 1;
    }

    // 2. Створення віртуальної машини
    int vm_fd = ioctl(kvm_fd, KVM_CREATE_VM, 0);
    if (vm_fd < 0) {
        perror("Помилка KVM_CREATE_VM");
        close(kvm_fd);
        return 1;
    }

    // 3. Виділення RAM для гостя
    void *mem = mmap(NULL, RAM_SIZE, PROT_READ | PROT_WRITE,
                     MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (mem == MAP_FAILED) {
        perror("Помилка mmap RAM");
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // Реєстрація слота пам'яті в KVM (GPA 0x00000000 -> HVA mem)
    struct kvm_userspace_memory_region region = {
        .slot = 0,
        .flags = 0,
        .guest_phys_addr = 0x0,
        .memory_size = RAM_SIZE,
        .userspace_addr = (unsigned long)mem,
    };
    if (ioctl(vm_fd, KVM_SET_USER_MEMORY_REGION, &region) < 0) {
        perror("Помилка KVM_SET_USER_MEMORY_REGION");
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 4. Створення віртуального процесора (vCPU 0)
    int vcpu_fd = ioctl(vm_fd, KVM_CREATE_VCPU, 0);
    if (vcpu_fd < 0) {
        perror("Помилка KVM_CREATE_VCPU");
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // Відображення структури kvm_run у простір користувача
    int mmap_size = ioctl(kvm_fd, KVM_GET_VCPU_MMAP_SIZE, 0);
    if (mmap_size < 0) {
        perror("Помилка KVM_GET_VCPU_MMAP_SIZE");
        close(vcpu_fd);
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    struct kvm_run *run = mmap(NULL, mmap_size, PROT_READ | PROT_WRITE,
                               MAP_SHARED, vcpu_fd, 0);
    if (run == MAP_FAILED) {
        perror("Помилка mmap struct kvm_run");
        close(vcpu_fd);
        munmap(mem, RAM_SIZE);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 5. Завантаження гостьового коду за адресою 0x0000
    const unsigned char code[] = {
        0xb0, 0x48,             // mov $0x48, %al  ('H')
        0xe6, 0x10,             // out %al, $0x10
        0xb0, 0x49,             // mov $0x49, %al  ('I')
        0xe6, 0x10,             // out %al, $0x10
        0xf4                    // hlt
    };
    memcpy(mem, code, sizeof(code));

    // 6. Налаштування початкових регістрів vCPU
    struct kvm_sregs sregs;
    if (ioctl(vcpu_fd, KVM_GET_SREGS, &sregs) < 0) {
        perror("Помилка KVM_GET_SREGS");
        goto cleanup;
    }
    sregs.cs.base = 0;
    sregs.cs.selector = 0;
    if (ioctl(vcpu_fd, KVM_SET_SREGS, &sregs) < 0) {
        perror("Помилка KVM_SET_SREGS");
        goto cleanup;
    }

    struct kvm_regs regs = {
        .rip = 0x0,
        .rflags = 0x2, // Обов'язковий біт 1 у прапорах x86
    };
    if (ioctl(vcpu_fd, KVM_SET_REGS, &regs) < 0) {
        perror("Помилка KVM_SET_REGS");
        goto cleanup;
    }

    // 7. Головний цикл виконання vCPU (Execution Loop)
    printf("Запуск міні-гіпервізора KVM...\nГостьовий вивід: ");
    fflush(stdout);

    int running = 1;
    while (running) {
        if (ioctl(vcpu_fd, KVM_RUN, 0) < 0) {
            perror("Помилка KVM_RUN");
            break;
        }

        switch (run->exit_reason) {
            case KVM_EXIT_IO:
                if (run->io.direction == KVM_EXIT_IO_OUT && run->io.port == 0x10) {
                    char *data = (char *)run + run->io.data_offset;
                    putchar(*data);
                    fflush(stdout);
                }
                break;

            case KVM_EXIT_HLT:
                printf("\n[KVM] Гість виконав інструкцію HLT. Завершення.\n");
                running = 0;
                break;

            case KVM_EXIT_FAIL_ENTRY:
                fprintf(stderr, "\n[KVM] Апаратна помилка входу: 0x%llx\n",
                        (unsigned long long)run->fail_entry.hardware_entry_failure_reason);
                running = 0;
                break;

            default:
                fprintf(stderr, "\n[KVM] Необроблена причина виходу: %d\n", run->exit_reason);
                running = 0;
                break;
        }
    }

cleanup:
    munmap(run, mmap_size);
    close(vcpu_fd);
    munmap(mem, RAM_SIZE);
    close(vm_fd);
    close(kvm_fd);
    return 0;
}
