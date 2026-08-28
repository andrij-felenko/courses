static void probe_locks() {
    std::string name = std::format("lock-{}", ::getpid());
    auto path = at(name);

    if (rpc(std::format("OPEN 0 rw {}", name)) < 0) { std::cout << "4. створити не вдалося\n"; return; }
    if (rpc("FLOCK 0") < 0) { std::cout << "4. чужий flock не взявся\n"; return; }

    int fd = ::open(path.c_str(), O_RDWR);
    if (fd < 0) { std::perror("4. open"); return; }

    int rc = ::flock(fd, LOCK_EX | LOCK_NB);
    std::cout << "4a. flock проти чужого flock: "
              << (rc == 0 ? "НЕ виключає — замок не долає межі машини"
                          : "виключає, як і має бути") << "\n";
    if (rc == 0) ::flock(fd, LOCK_UN);

    struct flock fl{};
    fl.l_type = F_WRLCK;
    fl.l_whence = SEEK_SET;
    rc = ::fcntl(fd, F_SETLK, &fl);
    std::cout << "4b. fcntl проти чужого flock: "
              << (rc == 0 ? "не виключає — як локально"
                          : "ВИКЛЮЧАЄ — flock зведено до POSIX-замка на весь файл") << "\n";
    if (rc == 0) { fl.l_type = F_UNLCK; ::fcntl(fd, F_SETLK, &fl); }

    rpc("CLOSE 0");
    if (rpc(std::format("OPEN 0 rw {}", name)) >= 0) {
        if (rpc("FCNTL 0") < 0) std::cout << "4c. чужий fcntl-замок не взявся взагалі\n";
        else {
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            rc = ::fcntl(fd, F_SETLK, &fl);
            std::cout << "4c. fcntl проти чужого fcntl: "
                      << (rc == 0 ? "НЕ виключає — замки лишилися локальними"
                                  : "виключає, як і має бути") << "\n";
            if (rc == 0) { fl.l_type = F_UNLCK; ::fcntl(fd, F_SETLK, &fl); }
        }
        rpc("CLOSE 0");
    }

    ::close(fd);
    rpc(std::format("UNLINK {}", name));
}
