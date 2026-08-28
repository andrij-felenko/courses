std::expected<void, std::error_code> cow_read_sector(
    const CowNode& chain,
    uint64_t sector,
    std::span<uint8_t, SECTOR_SIZE> buffer
) {
    if (sector >= chain.header.total_sectors) {
        return std::unexpected(std::error_code(EINVAL, std::generic_category()));
    }

    if (chain.is_overlay) {
        if (chain.is_sector_allocated(sector)) {
            off_t offset = chain.header.data_offset + (sector * SECTOR_SIZE);
            if (::pread(chain.fd, buffer.data(), SECTOR_SIZE, offset) != static_cast<ssize_t>(SECTOR_SIZE)) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            return {};
        }

        if (chain.backing_node) {
            return cow_read_sector(*chain.backing_node, sector, buffer);
        }

        std::fill(buffer.begin(), buffer.end(), 0);
        return {};
    } else {
        off_t offset = sector * SECTOR_SIZE;
        if (::pread(chain.fd, buffer.data(), SECTOR_SIZE, offset) != static_cast<ssize_t>(SECTOR_SIZE)) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
}

std::expected<void, std::error_code> cow_write_sector(
    CowNode& chain,
    uint64_t sector,
    std::span<const uint8_t, SECTOR_SIZE> buffer
) {
    if (!chain.is_overlay || sector >= chain.header.total_sectors) {
        return std::unexpected(std::error_code(EINVAL, std::generic_category()));
    }

    off_t data_off = chain.header.data_offset + (sector * SECTOR_SIZE);
    if (::pwrite(chain.fd, buffer.data(), SECTOR_SIZE, data_off) != static_cast<ssize_t>(SECTOR_SIZE)) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (!chain.is_sector_allocated(sector)) {
        chain.mark_sector_allocated(sector);

        uint64_t byte_idx = sector / 8;
        off_t bm_file_off = chain.header.bitmap_offset + byte_idx;

        if (::pwrite(chain.fd, &chain.bitmap[byte_idx], 1, bm_file_off) != 1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    return {};
}
