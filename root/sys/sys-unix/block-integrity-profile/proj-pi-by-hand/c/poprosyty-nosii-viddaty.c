static int nvme_read(int fd, uint32_t nsid, uint64_t slba,
                     void *data, uint32_t dlen, void *meta, uint32_t mlen)
{
    struct nvme_passthru_cmd c = {
        .opcode       = 0x02,                    /* Read */
        .nsid         = nsid,
        .addr         = (uint64_t)(uintptr_t)data,
        .data_len     = dlen,
        .metadata     = (uint64_t)(uintptr_t)meta,   /* окремий буфер під теги */
        .metadata_len = mlen,
        .cdw10        = (uint32_t)slba,
        .cdw11        = (uint32_t)(slba >> 32),
        .cdw12        = 0,        /* NLB = 0 → один блок; PRINFO = 0 */
        .timeout_ms   = 5000,
    };
    int rc = ioctl(fd, NVME_IOCTL_IO_CMD, &c);

    if (rc < 0) { perror("NVME_IOCTL_IO_CMD"); return -1; }
    if (rc > 0) {                                /* дійшло, та контролер відмовив */
        fprintf(stderr, "LBA %llu: NVMe SCT=%u SC=0x%02x\n",
                (unsigned long long)slba, ((unsigned)rc >> 8) & 0x7, (unsigned)rc & 0xff);
        return -1;
    }
    return 0;
}
