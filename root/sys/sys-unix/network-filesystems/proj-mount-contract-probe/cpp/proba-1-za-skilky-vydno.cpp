static double dir_ttl = -1;

static bool in_listing(const fs::path& dir, std::string_view name) {
    std::error_code ec;
    for (const auto& entry : fs::directory_iterator(dir, ec)) {
        if (entry.path().filename() == name) return true;
    }
    return false;
}

static void probe_visibility() {
    std::string name = std::format("vis-{}", ::getpid());
    auto path = at(name);

    std::error_code ec;
    if (fs::exists(path, ec)) { std::cout << "1. ім'я вже зайняте\n"; return; }
    in_listing(share_dir, name);

    if (rpc(std::format("OPEN 0 wx {}", name)) < 0) { std::cout << "1. створити не вдалося\n"; return; }
    rpc("WRITE 0 64");
    rpc("FSYNC 0");
    rpc("CLOSE 0");

    double t0 = mono(), ts = -1, td = -1;
    while (mono() - t0 < 180.0 && (ts < 0 || td < 0)) {
        if (ts < 0 && fs::exists(path, ec)) ts = mono() - t0;
        if (td < 0 && in_listing(share_dir, name)) td = mono() - t0;
        nap_ms(50);
    }

    std::cout << std::format("1a. stat() бачить новий файл через   {} с\n", secs(ts));
    std::cout << std::format("1b. readdir() бачить його через      {} с\n", secs(td));

    dir_ttl = std::max(ts, td);
    rpc(std::format("UNLINK {}", name));
}
