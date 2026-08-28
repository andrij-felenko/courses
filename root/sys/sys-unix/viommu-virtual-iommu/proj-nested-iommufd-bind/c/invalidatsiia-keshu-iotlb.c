#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/iommufd.h>

/* Інвалідація IOTLB у C */
int invalidate_stage1_iotlb_c(int iommufd_fd, uint32_t nested_hwpt_id,
                              uint64_t *inv_entries_array, uint32_t num_entries)
{
    struct iommu_hwpt_invalidate inv_cmd;
    memset(&inv_cmd, 0, sizeof(inv_cmd));
    inv_cmd.size = sizeof(inv_cmd);
    inv_cmd.hwpt_id = nested_hwpt_id;
    inv_cmd.data_type = IOMMU_HWPT_INVALIDATE_DATA_VTD_S1;
    inv_cmd.entry_len = sizeof(struct iommu_hwpt_vtd_s1_invalidate);
    inv_cmd.entry_num = num_entries;
    inv_cmd.inv_data_uptr = (uint64_t)(uintptr_t)inv_entries_array;

    if (ioctl(iommufd_fd, IOMMU_HWPT_INVALIDATE, &inv_cmd) < 0) {
        perror("[C] Помилка інвалідації IOTLB для вкладеного HWPT");
        return -1;
    }
    return 0;
}
