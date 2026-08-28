static void probe_open_file() {
    std::string name = std::format("app-{}", ::getpid());
    auto path = at(name);

    rpc(std::format("UNLINK {}", name));
    if (rpc(std::format("OPEN 0 w {}", name)) < 0) { std::cout << "2. створити не вдалося\n"; return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");

    int fd = ::open(path.c_str(), O_RDONLY);
    if (fd < 0) { std::perror("2. open"); return; }
    
    struct stat st{};
    if (::fstat(fd, &st) < 0) { ::close(fd); return; }
    off_t base = st.st_size;

    rpc("WRITE 0 4096");
    rpc("FSYNC 0");
    double t0 = mono(), tsize = -1, tdata = -1, treopen = -1;

    while (mono() - t0 < 180.0 && (tsize < 0 || tdata < 0 || treopen < 0)) {
        char c;
        if (tsize < 0 && ::fstat(fd, &st) == 0 && st.st_size > base)
            tsize = mono() - t0;
        if (tdata < 0 && ::pread(fd, &c, 1, base) == 1)
            tdata = mono() - t0;
        if (treopen < 0) {
            int g = ::open(path.c_str(), O_RDONLY);
            if (g >= 0) {
                if (::pread(g, &c, 1, base) == 1) treopen = mono() - t0;
                ::close(g);
            }
        }
        nap_ms(50);
    }

    std::cout << std::format("2a. новий розмір видно через         {} с\n", secs(tsize));
    std::cout << std::format("2b. дописані байти читаються через   {} с\n", secs(tdata));
    std::cout << std::format("2c. те саме з перевідкриттям файлу:  {} с\n", secs(treopen));

    ::close(fd);
    rpc("CLOSE 0");
    rpc(std::format("UNLINK {}", name));
}
