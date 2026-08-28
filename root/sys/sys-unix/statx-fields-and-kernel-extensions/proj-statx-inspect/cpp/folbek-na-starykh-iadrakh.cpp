inline std::expected<struct statx, std::error_code> 
safe_statx_with_fallback(int dirfd, const std::string& path, int flags, unsigned int mask) {
    struct statx stx{};
    int res = ::statx(dirfd, path.c_str(), flags, mask, &stx);
    if (res == 0) {
        return stx;
    }

    if (errno == ENOSYS || errno == EPERM || errno == EACCES) {
        struct stat st{};
        int stat_flags = 0;
        if (flags & AT_SYMLINK_NOFOLLOW) stat_flags |= AT_SYMLINK_NOFOLLOW;
        if (flags & AT_EMPTY_PATH) stat_flags |= AT_EMPTY_PATH;

        if (::fstatat(dirfd, path.c_str(), &st, stat_flags) == 0) {
            stx.stx_mask = STATX_BASIC_STATS;
            stx.stx_size = static_cast<uint64_t>(st.st_size);
            stx.stx_mode = static_cast<uint16_t>(st.st_mode);
            stx.stx_ino = static_cast<uint64_t>(st.st_ino);
            stx.stx_nlink = static_cast<uint32_t>(st.st_nlink);
            stx.stx_uid = static_cast<uint32_t>(st.st_uid);
            stx.stx_gid = static_cast<uint32_t>(st.st_gid);
            stx.stx_blocks = static_cast<uint64_t>(st.st_blocks);
            stx.stx_blksize = static_cast<uint32_t>(st.st_blksize);
            stx.stx_atime.tv_sec = st.st_atime;
            stx.stx_mtime.tv_sec = st.st_mtime;
            stx.stx_ctime.tv_sec = st.st_ctime;
            return stx;
        }
    }
    return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
}
