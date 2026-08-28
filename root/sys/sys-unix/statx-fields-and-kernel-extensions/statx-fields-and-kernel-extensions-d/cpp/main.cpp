struct statx stx{};
if (::statx(AT_FDCWD, path.data(), AT_SYMLINK_NOFOLLOW, STATX_BASIC_STATS | STATX_BTIME, &stx) == 0) {
    if (stx.stx_mask & STATX_BTIME) {
        // Поле stx_btime гарантовано містить чесний час створення
        process_btime(stx.stx_btime);
    } else {
        // Файлова система не підтримує btime — використовуємо фолбек на mtime
        fallback_time(stx.stx_mtime);
    }
}
