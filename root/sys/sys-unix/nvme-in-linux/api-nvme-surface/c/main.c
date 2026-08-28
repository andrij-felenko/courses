#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

int main(void) {
    uint8_t log[512];
    struct nvme_passthru_cmd cmd = {
        .opcode     = 0x02,                 /* Get Log Page          */
        .nsid       = 0xffffffff,           /* журнал усього контролера */
        .addr       = (uint64_t)(uintptr_t)log,
        .data_len   = sizeof log,
        .cdw10      = (127u << 16) | 0x02,  /* NUMDL = 127, LID = 0x02 */
        .timeout_ms = 5000,
    };

    int fd = open("/dev/nvme0", O_RDONLY);
    if (fd < 0) return 1;

    int rc = ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd);
    if (rc < 0)  return 2;              /* виклик не дійшов: дивись errno    */
    if (rc > 0)  return 3;              /* дійшов, але контролер відмовив:   */
                                        /* rc — це статус із черги завершень */

    printf("температура %u K, зношення %u %%\n",
           (unsigned)(log[1] | (log[2] << 8)), log[5]);
    return 0;
}
