std::expected<std::unique_ptr<CowNode>, std::error_code> open_cow_chain(std::string_view image_path) {
    int fd = ::open(image_path.data(), O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        fd = ::open(image_path.data(), O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    auto node = std::make_unique<CowNode>();
    node->fd = fd;

    CowHeader hdr{};
    if (::pread(fd, &hdr, sizeof(hdr), 0) == sizeof(hdr) && hdr.magic == COW_MAGIC) {
        node->is_overlay = true;
        node->header = hdr;
        node->bitmap.resize(hdr.bitmap_bytes);

        if (static_cast<uint64_t>(::pread(fd, node->bitmap.data(), hdr.bitmap_bytes, hdr.bitmap_offset)) != hdr.bitmap_bytes) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (std::strlen(hdr.backing_path) > 0) {
            auto backing_res = open_cow_chain(hdr.backing_path);
            if (!backing_res) {
                return std::unexpected(backing_res.error());
            }
            node->backing_node = std::move(*backing_res);
        }
    } else {
        node->is_overlay = false;
        off_t size = ::lseek(fd, 0, SEEK_END);
        node->header.total_sectors = (size > 0) ? (size / SECTOR_SIZE) : 0;
    }

    return node;
}
