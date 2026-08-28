int container_fd, group_fd, device_fd;
struct vfio_group_status group_status = { .argsz = sizeof(group_status) };

/* 1. Відкриваємо контейнер */
container_fd = open("/dev/vfio/vfio", O_RDWR);

/* 2. Відкриваємо групу 15 та приєднуємо до контейнера */
group_fd = open("/dev/vfio/15", O_RDWR);
ioctl(group_fd, VFIO_GROUP_GET_STATUS, &group_status);

if (group_status.flags & VFIO_GROUP_FLAGS_VIABLE) {
    ioctl(group_fd, VFIO_GROUP_SET_CONTAINER, &container_fd);
    ioctl(container_fd, VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU);

    /* 3. Отримуємо дескриптор конкретного пристрою PCI */
    device_fd = ioctl(group_fd, VFIO_GROUP_GET_DEVICE_FD, "0000:01:00.0");
}
