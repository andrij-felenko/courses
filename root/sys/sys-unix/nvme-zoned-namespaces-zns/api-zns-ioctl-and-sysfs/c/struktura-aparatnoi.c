#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

uint64_t submit_nvme_append_c(int fd, uint32_t nsid, uint64_t zslba, void *buf, size_t len) {
    uint32_t nlb = len / 512;
    struct nvme_passthru_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.opcode      = 0x7d; /* Zone Append */
    cmd.nsid        = nsid;
    cmd.addr        = (uint64_t)(uintptr_t)buf;
    cmd.data_len    = len;
    cmd.cdw10       = (uint32_t)(zslba & 0xFFFFFFFF);
    cmd.cdw11       = (uint32_t)(zslba >> 32);
    cmd.cdw12       = nlb - 1; /* 0-based NLB */
    cmd.timeout_ms  = 1000;

    if (ioctl(fd, NVME_IOCTL_IO_CMD, &cmd) < 0) {
        perror("NVME_IOCTL_IO_CMD append failed");
        return (uint64_t)-1;
    }
    return cmd.result;
}
