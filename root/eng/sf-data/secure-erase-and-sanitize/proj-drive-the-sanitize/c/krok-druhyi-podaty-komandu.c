static int sanitize_start(int fd, unsigned sanact, int no_dealloc)
{
    uint32_t cdw10 = (sanact & 0x7)                        /* SANACT */
                   | (0u << 3)                             /* AUSE = 0 */
                   | (0u << 4)                             /* OWPASS */
                   | (0u << 8)                             /* OIPBP */
                   | ((uint32_t)(no_dealloc != 0) << 9);   /* NODAS */

    struct nvme_passthru_cmd c = {
        .opcode     = NVME_ADMIN_SANITIZE,
        .cdw10      = cdw10,
        .cdw11      = 0,             /* OVRPAT — візерунок для перезапису */
        .timeout_ms = 60000,
    };
    return admin(fd, &c);
}
