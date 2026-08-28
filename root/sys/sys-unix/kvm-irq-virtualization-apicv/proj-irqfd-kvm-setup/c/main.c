#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <sys/ioctl.h>
#include <sys/eventfd.h>
#include <linux/kvm.h>

struct worker_args {
    int efd;
    volatile int running;
};

static void* interrupt_worker(void* arg) {
    struct worker_args* args = (struct worker_args*)arg;
    uint64_t signal_val = 1;

    for (int i = 0; i < 5; ++i) {
        usleep(100000); // Інтервал 100 мс між подіями
        ssize_t s = write(args->efd, &signal_val, sizeof(signal_val));
        if (s != sizeof(signal_val)) {
            perror("Помилка запису в eventfd");
            break;
        }
        printf("[Worker] Сигнал переривання #%d надіслано через eventfd\n", i + 1);
    }
    args->running = 0;
    return NULL;
}

int main(void) {
    int kvm_fd = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm_fd < 0) {
        perror("Не вдалося відкрити /dev/kvm");
        return 1;
    }

    int vm_fd = ioctl(kvm_fd, KVM_CREATE_VM, 0);
    if (vm_fd < 0) {
        perror("Помилка створення віртуальної машини KVM_CREATE_VM");
        close(kvm_fd);
        return 1;
    }

    // 1. Створюємо in-kernel irqchip (PIC + IOAPIC + Local APIC)
    if (ioctl(vm_fd, KVM_CREATE_IRQCHIP, 0) < 0) {
        perror("Помилка ініціалізації KVM_CREATE_IRQCHIP");
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 2. Створюємо неблокуючий дескриптор eventfd
    int irq_efd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
    if (irq_efd < 0) {
        perror("Помилка створення eventfd");
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    // 3. Налаштовуємо таблицю маршрутизації переривань GSI
    struct kvm_irq_routing* routing = calloc(1, sizeof(struct kvm_irq_routing) +
                                                sizeof(struct kvm_irq_routing_entry));
    if (!routing) {
        perror("Не вдалося виділити пам'ять під таблицю маршрутизації");
        close(irq_efd);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    routing->nr = 1;
    routing->flags = 0;
    routing->entries[0].gsi = 4; // Прив'язка до лінії GSI 4
    routing->entries[0].type = KVM_IRQ_ROUTING_IRQCHIP;
    routing->entries[0].u.irqchip.irqchip = KVM_IRQCHIP_IOAPIC;
    routing->entries[0].u.irqchip.pin = 4; // Пін 4 на контролері IO-APIC

    if (ioctl(vm_fd, KVM_SET_GSI_ROUTING, routing) < 0) {
        perror("Помилка налаштування KVM_SET_GSI_ROUTING");
        free(routing);
        close(irq_efd);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }
    free(routing);

    // 4. Реєструємо зв'язку IRQFD
    struct kvm_irqfd irqfd_cfg;
    memset(&irqfd_cfg, 0, sizeof(irqfd_cfg));
    irqfd_cfg.fd = irq_efd;
    irqfd_cfg.gsi = 4;
    irqfd_cfg.flags = 0;

    if (ioctl(vm_fd, KVM_IRQFD, &irqfd_cfg) < 0) {
        perror("Помилка прив'язки KVM_IRQFD");
        close(irq_efd);
        close(vm_fd);
        close(kvm_fd);
        return 1;
    }

    printf("[Host] IRQFD успішно прив'язано до GSI 4. Запуск генератора подій...\n");

    // 5. Запускаємо фоновий робочий потік
    struct worker_args args = { .efd = irq_efd, .running = 1 };
    pthread_t thread;
    if (pthread_create(&thread, NULL, interrupt_worker, &args) == 0) {
        pthread_join(thread, NULL);
    }

    // 6. Відв'язуємо дескриптор перед завершенням роботи
    irqfd_cfg.flags = KVM_IRQFD_FLAG_DEASSIGN;
    ioctl(vm_fd, KVM_IRQFD, &irqfd_cfg);

    close(irq_efd);
    close(vm_fd);
    close(kvm_fd);
    printf("[Host] Ресурси успішно звільнено, пайплайн переривань зупинено.\n");
    return 0;
}
