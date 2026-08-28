int cow_read_sector(CowNode *chain, uint64_t sector, uint8_t *buf) {
    if (!chain || sector >= chain->header.total_sectors) {
        return -EINVAL;
    }

    if (chain->is_overlay) {
        if (bitmap_test(chain->bitmap, sector)) {
            // Сектор модифіковано в цьому оверлеї
            off_t offset = chain->header.data_offset + (sector * SECTOR_SIZE);
            if (pread(chain->fd, buf, SECTOR_SIZE, offset) != SECTOR_SIZE) {
                return -EIO;
            }
            return 0;
        }

        // Сектор не виділено: спускаємося по ланцюжку
        if (chain->backing_node) {
            return cow_read_sector(chain->backing_node, sector, buf);
        }

        // Якщо батьківського файлу немає — повертаємо нульовий сектор
        memset(buf, 0, SECTOR_SIZE);
        return 0;
    } else {
        // Читання із сирого образу
        off_t offset = sector * SECTOR_SIZE;
        if (pread(chain->fd, buf, SECTOR_SIZE, offset) != SECTOR_SIZE) {
            return -EIO;
        }
        return 0;
    }
}

int cow_write_sector(CowNode *chain, uint64_t sector, const uint8_t *buf) {
    if (!chain || !chain->is_overlay || sector >= chain->header.total_sectors) {
        return -EINVAL;
    }

    off_t data_off = chain->header.data_offset + (sector * SECTOR_SIZE);
    if (pwrite(chain->fd, buf, SECTOR_SIZE, data_off) != SECTOR_SIZE) {
        return -EIO;
    }

    // Якщо сектор ще не був позначений як виділений — оновлюємо бітову карту
    if (!bitmap_test(chain->bitmap, sector)) {
        bitmap_set(chain->bitmap, sector);

        uint64_t byte_idx = sector / 8;
        off_t bm_file_off = chain->header.bitmap_offset + byte_idx;

        if (pwrite(chain->fd, &chain->bitmap[byte_idx], 1, bm_file_off) != 1) {
            return -EIO;
        }
    }

    return 0;
}
