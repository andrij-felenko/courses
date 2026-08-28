#include <linux/nvme_ioctl.h>

/* той самий буфер Discovery, але повз sed-opal */
static int nvme_discovery(int fd, void *buf, size_t len)
{
        struct nvme_admin_cmd c = {
                .opcode   = 0x82,                           /* Security Receive */
                .nsid     = 0,
                .addr     = (uint64_t)(uintptr_t)buf,
                .data_len = (uint32_t)len,
                .cdw10    = (0x01u << 24) | (0x0001u << 8), /* SECP=0x01 (TCG), ComID=0x0001 */
                .cdw11    = (uint32_t)len,                  /* скільки байтів ми готові взяти */
        };
        memset(buf, 0, len);
        return ioctl(fd, NVME_IOCTL_ADMIN_CMD, &c);
}
