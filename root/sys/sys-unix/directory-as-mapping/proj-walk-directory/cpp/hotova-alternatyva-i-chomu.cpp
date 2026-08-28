static unsigned long long total = 0;
std::error_code ec;

for (const auto &entry : std::filesystem::recursive_directory_iterator(
         root, std::filesystem::directory_options::skip_permission_denied, ec)) {
    struct stat st;
    if (stat(entry.path().c_str(), &st) == 0) {
        total += static_cast<unsigned long long>(st.st_blocks) * 512;
    }
}
