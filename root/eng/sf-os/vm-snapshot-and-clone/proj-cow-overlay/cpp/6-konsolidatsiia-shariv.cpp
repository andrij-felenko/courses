std::expected<void, std::error_code> cow_commit_to_backing(CowNode& overlay) {
    if (!overlay.is_overlay || !overlay.backing_node) {
        return std::unexpected(std::error_code(EINVAL, std::generic_category()));
    }

    std::array<uint8_t, SECTOR_SIZE> buffer{};
    uint64_t total = overlay.header.total_sectors;

    for (uint64_t s = 0; s < total; ++s) {
        if (overlay.is_sector_allocated(s)) {
            off_t src_off = overlay.header.data_offset + (s * SECTOR_SIZE);
            if (::pread(overlay.fd, buffer.data(), SECTOR_SIZE, src_off) != static_cast<ssize_t>(SECTOR_SIZE)) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            if (overlay.backing_node->is_overlay) {
                auto res = cow_write_sector(*overlay.backing_node, s, buffer);
                if (!res) return res;
            } else {
                off_t dst_off = s * SECTOR_SIZE;
                if (::pwrite(overlay.backing_node->fd, buffer.data(), SECTOR_SIZE, dst_off) != static_cast<ssize_t>(SECTOR_SIZE)) {
                    return std::unexpected(std::error_code(errno, std::generic_category()));
                }
            }
        }
    }

    ::fdatasync(overlay.backing_node->fd);

    std::fill(overlay.bitmap.begin(), overlay.bitmap.end(), 0);
    if (static_cast<uint64_t>(::pwrite(overlay.fd, overlay.bitmap.data(), 
                                      overlay.bitmap.size(), 
                                      overlay.header.bitmap_offset)) != overlay.bitmap.size()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::fdatasync(overlay.fd);
    return {};
}
