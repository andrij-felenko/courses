std::expected<void, std::error_code> create_cow_overlay(
    std::string_view overlay_path,
    std::string_view backing_path,
    uint64_t total_sectors
) {
    int fd = ::open(overlay_path.data(), O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    uint64_t bm_bytes = (total_sectors + 7) / 8;
    uint64_t bm_sectors = (bm_bytes + SECTOR_SIZE - 1) / SECTOR_SIZE;
    uint64_t aligned_bm_bytes = bm_sectors * SECTOR_SIZE;

    CowHeader hdr{};
    hdr.magic = COW_MAGIC;
    hdr.version = COW_VERSION;
    hdr.total_sectors = total_sectors;
    hdr.bitmap_offset = sizeof(CowHeader);
    hdr.bitmap_bytes = aligned_bm_bytes;
    hdr.data_offset = hdr.bitmap_offset + aligned_bm_bytes;
    
    size_t copy_len = std::min(backing_path.size(), MAX_PATH_LEN - 1);
    std::memcpy(hdr.backing_path, backing_path.data(), copy_len);
    hdr.backing_path[copy_len] = '\0';

    if (::pwrite(fd, &hdr, sizeof(hdr), 0) != sizeof(hdr)) {
        int err = errno;
        ::close(fd);
        return std::unexpected(std::error_code(err, std::generic_category()));
    }

    std::vector<uint8_t> zero_bm(aligned_bm_bytes, 0);
    if (static_cast<uint64_t>(::pwrite(fd, zero_bm.data(), zero_bm.size(), hdr.bitmap_offset)) != aligned_bm_bytes) {
        int err = errno;
        ::close(fd);
        return std::unexpected(std::error_code(err, std::generic_category()));
    }

    ::fdatasync(fd);
    ::close(fd);
    return {};
}
