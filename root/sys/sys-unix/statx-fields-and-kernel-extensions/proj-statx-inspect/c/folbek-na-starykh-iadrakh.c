static int safe_statx_with_fallback(int dirfd, const char *path, int flags,
                                    unsigned int mask, struct statx *stx) {
    int res = statx(dirfd, path, flags, mask, stx);
    if (res == 0) {
        return 0; /* Виклик statx успішно виконано */
    }

    /* Якщо ядро або seccomp блокують statx, робимо фолбек на fstatat */
    if (errno == ENOSYS || errno == EPERM || errno == EACCES) {
        struct stat st;
        int stat_flags = 0;
        if (flags & AT_SYMLINK_NOFOLLOW) stat_flags |= AT_SYMLINK_NOFOLLOW;
        if (flags & AT_EMPTY_PATH) stat_flags |= AT_EMPTY_PATH;

        if (fstatat(dirfd, path, &st, stat_flags) == 0) {
            memset(stx, 0, sizeof(*stx));
            stx->stx_mask = STATX_BASIC_STATS;
            stx->stx_size = st.st_size;
            stx->stx_mode = st.st_mode;
            stx->stx_ino = st.st_ino;
            stx->stx_nlink = st.st_nlink;
            stx->stx_uid = st.st_uid;
            stx->stx_gid = st.st_gid;
            stx->stx_blocks = st.st_blocks;
            stx->stx_blksize = st.st_blksize;
            stx->stx_atime.tv_sec = st.st_atime;
            stx->stx_mtime.tv_sec = st.st_mtime;
            stx->stx_ctime.tv_sec = st.st_ctime;
            return 0;
        }
    }
    return -1;
}
