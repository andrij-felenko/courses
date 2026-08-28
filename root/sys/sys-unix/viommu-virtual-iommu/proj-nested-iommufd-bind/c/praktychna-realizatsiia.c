#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* Структура конфігурації Intel VT-d Stage 1 для передачі в ядро */
struct iommu_hwpt_vtd_s1_config {
    __u64 flags;
    __u64 pgtbl_pptr; /* Фізичний покажчик на корінь таблиці сторінок L1 */
    __u32 addr_width; /* Ширина адреси (48 або 57 біт для 4/5-рівневого пейджингу) */
    __u32 pad;
};

/* Створення вкладеної HWPT Стадії 1 у C */
int create_nested_stage1_hwpt_c(int iommufd_fd, uint32_t dev_id, 
                                uint32_t stage2_hwpt_id, 
                                uint64_t l1_pgtbl_root,
                                uint32_t *out_nested_hwpt_id) 
{
    if (iommufd_fd < 0 || !out_nested_hwpt_id) {
        errno = EINVAL;
        return -1;
    }

    struct iommu_hwpt_vtd_s1_config vtd_s1_cfg;
    memset(&vtd_s1_cfg, 0, sizeof(vtd_s1_cfg));
    vtd_s1_cfg.flags = 0;
    vtd_s1_cfg.pgtbl_pptr = l1_pgtbl_root;
    vtd_s1_cfg.addr_width = 48; /* Стандартний 4-рівневий пейджинг x86_64 */

    struct iommu_hwpt_alloc alloc_cmd;
    memset(&alloc_cmd, 0, sizeof(alloc_cmd));
    alloc_cmd.size = sizeof(alloc_cmd);
    alloc_cmd.flags = 0; /* вкладеність задає не прапорець, а батьківський pt_id */
    alloc_cmd.dev_id = dev_id;
    alloc_cmd.pt_id = stage2_hwpt_id; /* Базовий батьківський HWPT Стадії 2 */
    alloc_cmd.data_type = IOMMU_HWPT_DATA_VTD_S1; /* Режим Intel VT-d Stage 1 */
    alloc_cmd.data_len = sizeof(vtd_s1_cfg);
    alloc_cmd.data_uptr = (uint64_t)(uintptr_t)&vtd_s1_cfg;

    if (ioctl(iommufd_fd, IOMMU_HWPT_ALLOC, &alloc_cmd) < 0) {
        perror("[C-API] Помилка виконання ioctl(IOMMU_HWPT_ALLOC)");
        return -1;
    }

    *out_nested_hwpt_id = alloc_cmd.out_hwpt_id;
    printf("[C-API] Успішно створено вкладений HWPT Stage 1 ID: %u\n", alloc_cmd.out_hwpt_id);
    return 0;
}
