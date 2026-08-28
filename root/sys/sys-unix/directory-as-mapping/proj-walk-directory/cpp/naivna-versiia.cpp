/* НАЇВНО — так робити не варто. */
static unsigned long long du_naive(const std::filesystem::path &dir)
{
    unsigned long long total = 0;
    std::error_code ec;
    for (const auto &entry : std::filesystem::directory_iterator(dir, ec)) {
        struct stat st;
        if (stat(entry.path().c_str(), &st) == 0) {
            total += static_cast<unsigned long long>(st.st_blocks) * 512;
            if (S_ISDIR(st.st_mode)) {
                total += du_naive(entry.path());
            }
        }
    }
    return total;
}
