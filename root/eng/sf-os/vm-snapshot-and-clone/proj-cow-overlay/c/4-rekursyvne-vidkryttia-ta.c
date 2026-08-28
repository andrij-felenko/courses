CowNode *cow_open_chain(const char *image_path) {
    int fd = open(image_path, O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        // Спроба відкрити в режимі Read-Only (для базових образів)
        fd = open(image_path, O_RDONLY | O_CLOEXEC);
        if (fd < 0) return NULL;
    }

    CowNode *node = (CowNode *)calloc(1, sizeof(CowNode));
    if (!node) {
        close(fd);
        return NULL;
    }
    node->fd = fd;

    CowHeader hdr;
    if (pread(fd, &hdr, sizeof(hdr), 0) == sizeof(hdr) && hdr.magic == COW_MAGIC) {
        node->is_overlay = true;
        node->header = hdr;
        node->bitmap = (uint8_t *)malloc(hdr.bitmap_bytes);
        if (!node->bitmap) {
            close(fd);
            free(node);
            return NULL;
        }

        if ((uint64_t)pread(fd, node->bitmap, hdr.bitmap_bytes, hdr.bitmap_offset) != hdr.bitmap_bytes) {
            free(node->bitmap);
            close(fd);
            free(node);
            return NULL;
        }

        if (strlen(hdr.backing_path) > 0) {
            node->backing_node = cow_open_chain(hdr.backing_path);
            if (!node->backing_node) {
                fprintf(stderr, "Помилка відкриття backing-файлу: %s\n", hdr.backing_path);
                free(node->bitmap);
                close(fd);
                free(node);
                return NULL;
            }
        }
    } else {
        // Сирий образ (RAW)
        node->is_overlay = false;
        off_t size = lseek(fd, 0, SEEK_END);
        node->header.total_sectors = (size > 0) ? (size / SECTOR_SIZE) : 0;
    }

    return node;
}

void cow_close_chain(CowNode *node) {
    if (!node) return;
    if (node->backing_node) {
        cow_close_chain(node->backing_node);
    }
    if (node->bitmap) {
        free(node->bitmap);
    }
    if (node->fd >= 0) {
        close(node->fd);
    }
    free(node);
}
