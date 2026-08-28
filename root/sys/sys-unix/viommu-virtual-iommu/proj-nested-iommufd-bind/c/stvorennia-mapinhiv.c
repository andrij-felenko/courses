/* Створення мапінгу IOAS у C */
int map_ioas_region_c(int iommufd_fd, uint32_t ioas_id, uint64_t hva_address,
                     uint64_t l1_gpa_address, uint64_t memory_region_size)
{
    struct iommu_ioas_map map_cmd;
    memset(&map_cmd, 0, sizeof(map_cmd));
    map_cmd.size = sizeof(map_cmd);
    map_cmd.ioas_id = ioas_id;
    map_cmd.flags = IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE |
                    IOMMU_IOAS_MAP_FIXED_IOVA; /* IOVA задає викликач, а не ядро */
    map_cmd.user_va = hva_address;
    map_cmd.iova = l1_gpa_address;
    map_cmd.length = memory_region_size;

    if (ioctl(iommufd_fd, IOMMU_IOAS_MAP, &map_cmd) < 0) {
        perror("Помилка створення мапінгу IOAS");
        return -1;
    }
    return 0;
}
