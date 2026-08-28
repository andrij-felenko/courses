// Безпечний варіант функції робітника мовою C++20
void safe_worker_iteration_cpp(int dirfd, std::string_view filename) {
    // 1. Атомарне відкриття через openat із прапорцем O_NOFOLLOW
    ScopedFd fd(::openat(dirfd, filename.data(), O_WRONLY | O_NOFOLLOW | O_CLOEXEC));
    if (!fd.valid()) {
        if (errno == ELOOP) {
            // Спробу атаки заблоковано: VFS відмовився переходити за симлінком
            return;
        }
        return;
    }

    // 2. Перевірка зафіксованого дескриптора через fstat
    struct stat st{};
    if (::fstat(fd.get(), &st) == 0 && S_ISREG(st.st_mode)) {
        constexpr std::string_view msg = "SAFE_DATA_WRITE\n";
        ::write(fd.get(), msg.data(), msg.size());
    }
}
