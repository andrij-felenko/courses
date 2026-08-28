static void probe_write_path() {
    constexpr size_t CHUNKS = 64;
    constexpr size_t CHUNK = 1u << 20; // 1 МіБ
    std::string name = std::format("flush-{}", ::getpid());
    auto path = at(name);

    std::vector<char> buf(CHUNK, 'z');
    int fd = ::open(path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { std::perror("3. open"); return; }

    double t0 = mono();
    int rc = 0;
    for (size_t i = 0; i < CHUNKS; ++i) {
        if (::write(fd, buf.data(), CHUNK) != static_cast<ssize_t>(CHUNK)) { rc = -1; break; }
    }
    double t_write = mono() - t0;

    t0 = mono();
    if (::fsync(fd) < 0) rc = -1;
    double t_fsync = mono() - t0;

    t0 = mono();
    if (::close(fd) < 0) rc = -1;
    double t_close = mono() - t0;

    std::cout << std::format("3.  {} МіБ:  write() {:.2f} с   fsync() {:.2f} с   close() {:.2f} с{}\n",
                CHUNKS, t_write, t_fsync, t_close, rc < 0 ? "   ← ПОМИЛКА" : "");
    std::cout << std::format("    сукупний темп ≈ {:.0f} МіБ/с\n",
                CHUNKS / (t_write + t_fsync + t_close + 1e-9));

    std::error_code ec;
    fs::remove(path, ec);
}
