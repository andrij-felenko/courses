#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/vfio.h>
#include <linux/iommufd.h>
#include <errno.h>

#define PAGE_SIZE_4K 4096
#define BUFFER_SIZE  (2 * 1024 * 1024) // 2 MB Hugepage-сумісний буфер

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/vfio/devices/0000:01:00.0";
    int iommufd = -1;
    int dev_fd = -1;
    void *dma_buffer = NULL;
    int ret = 0;

    printf("[1] Відкриття /dev/iommufd...\n");
    iommufd = open("/dev/iommufd", O_RDWR | O_CLOEXEC);
    if (iommufd < 0) {
        perror("Помилка відкриття /dev/iommufd");
        return 1;
    }

    printf("[2] Відкриття VFIO пристрою %s...\n", dev_path);
    dev_fd = open(dev_path, O_RDWR | O_CLOEXEC);
    if (dev_fd < 0) {
        perror("Помилка відкриття пристрою VFIO");
        ret = 1;
        goto cleanup;
    }

    printf("[3] Прив'язка пристрою через VFIO_DEVICE_BIND_IOMMUFD...\n");
    struct vfio_device_bind_iommufd bind_cmd = {
        .argsz = sizeof(bind_cmd),
        .flags = 0,
        .iommufd = iommufd,
        .dev_id = 0, // Заповнюється ядром
    };
    if (ioctl(dev_fd, VFIO_DEVICE_BIND_IOMMUFD, &bind_cmd) < 0) {
        perror("VFIO_DEVICE_BIND_IOMMUFD failed");
        ret = 1;
        goto cleanup;
    }
    uint32_t dev_id = bind_cmd.dev_id;
    printf("    -> Отримано dev_id: %u\n", dev_id);

    printf("[4] Виділення IOAS через IOMMU_IOAS_ALLOC...\n");
    struct iommu_ioas_alloc alloc_cmd = {
        .size = sizeof(alloc_cmd),
        .flags = 0,
        .out_ioas_id = 0,
    };
    if (ioctl(iommufd, IOMMU_IOAS_ALLOC, &alloc_cmd) < 0) {
        perror("IOMMU_IOAS_ALLOC failed");
        ret = 1;
        goto cleanup;
    }
    uint32_t ioas_id = alloc_cmd.out_ioas_id;
    printf("    -> Створено IOAS з id: %u\n", ioas_id);

    printf("[5] Виділення 2 MB буфера в пам'яті процесу (HVA)...\n");
    ret = posix_memalign(&dma_buffer, PAGE_SIZE_4K, BUFFER_SIZE);
    if (ret != 0 || !dma_buffer) {
        fprintf(stderr, "Помилка posix_memalign: %s\n", strerror(ret));
        ret = 1;
        goto cleanup;
    }
    memset(dma_buffer, 0xAA, BUFFER_SIZE);

    printf("[6] Відображення пам'яті через IOMMU_IOAS_MAP...\n");
    uint64_t target_iova = 0x10000000; // Цільова IOVA адреса для DMA
    struct iommu_ioas_map map_cmd = {
        .size = sizeof(map_cmd),
        .flags = IOMMU_IOAS_MAP_FIXED_IOVA | IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE,
        .ioas_id = ioas_id,
        .__reserved = 0,
        .user_va = (uint64_t)dma_buffer,
        .length = BUFFER_SIZE,
        .iova = target_iova,
    };
    if (ioctl(iommufd, IOMMU_IOAS_MAP, &map_cmd) < 0) {
        perror("IOMMU_IOAS_MAP failed");
        ret = 1;
        goto cleanup;
    }
    printf("    -> Буфер HVA %p mapped до IOVA 0x%lx (довжина: %u байтів)\n",
           dma_buffer, (unsigned long)map_cmd.iova, BUFFER_SIZE);

    printf("[7] Підключення пристрою до IOAS через VFIO_DEVICE_ATTACH_IOMMUFD_PT...\n");
    struct vfio_device_attach_iommufd_pt attach_cmd = {
        .argsz = sizeof(attach_cmd),
        .flags = 0,
        .pt_id = ioas_id, // Передаємо ioas_id; ядро створить HWPT автоматично
    };
    if (ioctl(dev_fd, VFIO_DEVICE_ATTACH_IOMMUFD_PT, &attach_cmd) < 0) {
        perror("VFIO_DEVICE_ATTACH_IOMMUFD_PT failed");
        ret = 1;
        goto cleanup;
    }
    printf("    -> Пристрій dev_id %u успішно підключено до апаратної таблиці IOMMU!\n", dev_id);

    printf("[8] Тестовий цикл завершено. Очищення ресурсів...\n");

    // Відключення пристрою
    struct vfio_device_detach_iommufd_pt detach_cmd = {
        .argsz = sizeof(detach_cmd),
        .flags = 0,
    };
    ioctl(dev_fd, VFIO_DEVICE_DETACH_IOMMUFD_PT, &detach_cmd);

    // Розвідображення DMA пам'яті
    struct iommu_ioas_unmap unmap_cmd = {
        .size = sizeof(unmap_cmd),
        .ioas_id = ioas_id,
        .iova = target_iova,
        .length = BUFFER_SIZE,
    };
    ioctl(iommufd, IOMMU_IOAS_UNMAP, &unmap_cmd);

    ret = 0;

cleanup:
    if (dma_buffer) free(dma_buffer);
    if (dev_fd >= 0) close(dev_fd);
    if (iommufd >= 0) close(iommufd);
    return ret;
}
