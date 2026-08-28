int cow_commit_to_backing(CowNode *overlay) {
    if (!overlay || !overlay->is_overlay || !overlay->backing_node) {
        return -EINVAL;
    }

    uint8_t buffer[SECTOR_SIZE];
    uint64_t total = overlay->header.total_sectors;

    for (uint64_t s = 0; s < total; ++s) {
        if (bitmap_test(overlay->bitmap, s)) {
            off_t src_off = overlay->header.data_offset + (s * SECTOR_SIZE);
            if (pread(overlay->fd, buffer, SECTOR_SIZE, src_off) != SECTOR_SIZE) {
                return -EIO;
            }

            if (overlay->backing_node->is_overlay) {
                if (cow_write_sector(overlay->backing_node, s, buffer) != 0) {
                    return -EIO;
                }
            } else {
                off_t dst_off = s * SECTOR_SIZE;
                if (pwrite(overlay->backing_node->fd, buffer, SECTOR_SIZE, dst_off) != SECTOR_SIZE) {
                    return -EIO;
                }
            }
        }
    }

    // Синхронізуємо дані на постійному носії
    fdatasync(overlay->backing_node->fd);

    // Очищаємо бітову карту оверлею
    memset(overlay->bitmap, 0, overlay->header.bitmap_bytes);
    if ((uint64_t)pwrite(overlay->fd, overlay->bitmap, overlay->header.bitmap_bytes, 
                         overlay->header.bitmap_offset) != overlay->header.bitmap_bytes) {
        return -EIO;
    }

    fdatasync(overlay->fd);
    return 0;
}
