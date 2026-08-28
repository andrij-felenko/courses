int cow_create_overlay(const char *overlay_path, const char *backing_path, uint64_t total_sectors) {
    int fd = open(overlay_path, O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (fd < 0) {
        return -1;
    }

    uint64_t bm_bytes = (total_sectors + 7) / 8;
    // Вирівнюємо розмір бітової карти по межі 512 байтів
    uint64_t bm_sectors = (bm_bytes + SECTOR_SIZE - 1) / SECTOR_SIZE;
    uint64_t aligned_bm_bytes = bm_sectors * SECTOR_SIZE;

    CowHeader hdr;
    memset(&hdr, 0, sizeof(hdr));
    hdr.magic = COW_MAGIC;
    hdr.version = COW_VERSION;
    hdr.total_sectors = total_sectors;
    hdr.bitmap_offset = sizeof(CowHeader);
    hdr.bitmap_bytes = aligned_bm_bytes;
    hdr.data_offset = hdr.bitmap_offset + aligned_bm_bytes;
    strncpy(hdr.backing_path, backing_path, MAX_PATH_LEN - 1);

    if (pwrite(fd, &hdr, sizeof(hdr), 0) != sizeof(hdr)) {
        close(fd);
        return -1;
    }

    // Записуємо нульову бітову карту
    uint8_t *zero_bm = (uint8_t *)calloc(1, aligned_bm_bytes);
    if (!zero_bm) {
        close(fd);
        return -1;
    }

    if ((uint64_t)pwrite(fd, zero_bm, aligned_bm_bytes, hdr.bitmap_offset) != aligned_bm_bytes) {
        free(zero_bm);
        close(fd);
        return -1;
    }

    free(zero_bm);
    fdatasync(fd);
    close(fd);
    return 0;
}
