#define _GNU_SOURCE
#include <endian.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/nvme_ioctl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define NVME_ADMIN_GET_LOG   0x02
#define NVME_ADMIN_IDENTIFY  0x06
#define NVME_ADMIN_SANITIZE  0x84

/* Від'ємне — ядро не пустило (errno). Додатне — статус від самого контролера. */
static int admin(int fd, struct nvme_passthru_cmd *c)
{
    int rc = ioctl(fd, NVME_IOCTL_ADMIN_CMD, c);
    return rc < 0 ? -errno : rc;
}

static int read_sanicap(int fd, uint32_t *sanicap)
{
    uint8_t id[4096] = {0};
    struct nvme_passthru_cmd c = {
        .opcode     = NVME_ADMIN_IDENTIFY,
        .addr       = (uint64_t)(uintptr_t)id,
        .data_len   = sizeof id,
        .cdw10      = 1,              /* CNS = 1: Identify Controller */
        .timeout_ms = 15000,
    };
    int rc = admin(fd, &c);
    if (rc) return rc;

    uint32_t le;
    memcpy(&le, id + 328, 4);         /* SANICAP — байти 331:328 */
    *sanicap = le32toh(le);           /* дані від контролера — little-endian */
    return 0;
}
