#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/eventfd.h>
#include <linux/vfio.h>
#include <stdint.h>

#define DMA_BUFFER_SIZE (2 * 1024 * 1024) /* 2 MB DMA буфер */

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <group_id> <pci_bdf>\n", argv[0]);
        fprintf(stderr, "Приклад: %s 15 0000:01:00.0\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *group_id = argv[1];
    const char *pci_bdf = argv[2];

    /* 1. Збільшуємо ліміт закріпленої пам'яті (RLIMIT_MEMLOCK) */
    struct rlimit rlim = { RLIM_INFINITY, RLIM_INFINITY };
    if (setrlimit(RLIMIT_MEMLOCK, &rlim) < 0) {
        perror("setrlimit(RLIMIT_MEMLOCK)");
        return EXIT_FAILURE;
    }

    /* 2. Відкриваємо контейнер VFIO */
    int container_fd = open("/dev/vfio/vfio", O_RDWR);
    if (container_fd < 0) {
        perror("open /dev/vfio/vfio");
        return EXIT_FAILURE;
    }

    if (ioctl(container_fd, VFIO_GET_API_VERSION) != VFIO_API_VERSION ||
        !ioctl(container_fd, VFIO_CHECK_EXTENSION, VFIO_TYPE1_IOMMU)) {
        fprintf(stderr, "Непідтримувана версія VFIO або відсутній TYPE1 IOMMU\n");
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* 3. Відкриваємо групу VFIO */
    char group_path[64];
    snprintf(group_path, sizeof(group_path), "/dev/vfio/%s", group_id);
    int group_fd = open(group_path, O_RDWR);
    if (group_fd < 0) {
        perror("open /dev/vfio/<group>");
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* Перевіряємо стан групи */
    struct vfio_group_status status = { .argsz = sizeof(status) };
    if (ioctl(group_fd, VFIO_GROUP_GET_STATUS, &status) < 0 || !(status.flags & VFIO_GROUP_FLAGS_VIABLE)) {
        fprintf(stderr, "Група %s не є готова (деякі пристрої не під контролем VFIO)\n", group_id);
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* Приєднуємо групу до контейнера */
    if (ioctl(group_fd, VFIO_GROUP_SET_CONTAINER, &container_fd) < 0) {
        perror("ioctl(VFIO_GROUP_SET_CONTAINER)");
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* Встановлюємо тип IOMMU для контейнера */
    if (ioctl(container_fd, VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU) < 0) {
        perror("ioctl(VFIO_SET_IOMMU)");
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* 4. Отримуємо дескриптор PCI-пристрою */
    int device_fd = ioctl(group_fd, VFIO_GROUP_GET_DEVICE_FD, pci_bdf);
    if (device_fd < 0) {
        perror("ioctl(VFIO_GROUP_GET_DEVICE_FD)");
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* 5. Виділяємо та реєструємо DMA-буфер у пам'яті */
    void *dma_buffer = NULL;
    if (posix_memalign(&dma_buffer, sysconf(_SC_PAGESIZE), DMA_BUFFER_SIZE) != 0) {
        perror("posix_memalign");
        close(device_fd);
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }
    memset(dma_buffer, 0, DMA_BUFFER_SIZE);

    struct vfio_iommu_type1_dma_map dma_map = {
        .argsz = sizeof(dma_map),
        .flags = VFIO_DMA_MAP_FLAG_READ | VFIO_DMA_MAP_FLAG_WRITE,
        .vaddr = (uint64_t)dma_buffer,
        .iova = 0x10000000, /* Призначаємо IOVA адресою 0x10000000 */
        .size = DMA_BUFFER_SIZE
    };

    if (ioctl(container_fd, VFIO_IOMMU_MAP_DMA, &dma_map) < 0) {
        perror("ioctl(VFIO_IOMMU_MAP_DMA)");
        free(dma_buffer);
        close(device_fd);
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }
    printf("DMA буфер зареєстровано: HVA=%p -> IOVA=0x%llx (розмір %d байтів)\n",
           dma_buffer, (unsigned long long)dma_map.iova, DMA_BUFFER_SIZE);

    /* 6. Отримуємо інформацію про BAR0 та робимо mmap */
    struct vfio_region_info reg_info = {
        .argsz = sizeof(reg_info),
        .index = VFIO_PCI_BAR0_REGION_INDEX
    };

    if (ioctl(device_fd, VFIO_DEVICE_GET_REGION_INFO, &reg_info) == 0 && reg_info.size > 0) {
        void *bar0_mmio = mmap(NULL, reg_info.size, PROT_READ | PROT_WRITE,
                               MAP_SHARED, device_fd, reg_info.offset);
        if (bar0_mmio != MAP_FAILED) {
            printf("BAR0 MMIO відображено за адресою %p (розмір %llu байтів)\n",
                   bar0_mmio, (unsigned long long)reg_info.size);
            
            /* Читаємо перший 32-бітний регістр MMIO */
            volatile uint32_t *reg0 = (volatile uint32_t *)bar0_mmio;
            printf("Значення регістра BAR0[0]: 0x%08x\n", *reg0);

            munmap(bar0_mmio, reg_info.size);
        }
    }

    /* 7. Налаштовуємо переривання MSI через eventfd */
    int efd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
    if (efd >= 0) {
        char irq_set_buf[sizeof(struct vfio_irq_set) + sizeof(int)];
        struct vfio_irq_set *irq_set = (struct vfio_irq_set *)irq_set_buf;
        irq_set->argsz = sizeof(irq_set_buf);
        irq_set->flags = VFIO_IRQ_SET_DATA_EVENTFD | VFIO_IRQ_SET_ACTION_TRIGGER;
        irq_set->index = VFIO_PCI_MSI_IRQ_INDEX;
        irq_set->start = 0;
        irq_set->count = 1;
        *(int *)&irq_set->data[0] = efd;

        if (ioctl(device_fd, VFIO_DEVICE_SET_IRQS, irq_set) == 0) {
            printf("Переривання MSI-0 успішно підключено до eventfd %d\n", efd);
        }
        close(efd);
    }

    /* Очищення ресурсів */
    struct vfio_iommu_type1_dma_unmap dma_unmap = {
        .argsz = sizeof(dma_unmap),
        .flags = 0,
        .iova = 0x10000000,
        .size = DMA_BUFFER_SIZE
    };
    ioctl(container_fd, VFIO_IOMMU_UNMAP_DMA, &dma_unmap);
    free(dma_buffer);
    close(device_fd);
    close(group_fd);
    close(container_fd);

    printf("Драйвер успішно завершив роботу.\n");
    return EXIT_SUCCESS;
}
