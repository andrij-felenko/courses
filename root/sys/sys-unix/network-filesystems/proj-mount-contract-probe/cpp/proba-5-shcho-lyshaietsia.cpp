static void probe_open_unlink() {
    std::string aname = std::format("del-a-{}", ::getpid());
    std::string bname = std::format("del-b-{}", ::getpid());
    auto apath = at(aname);

    if (rpc(std::format("OPEN 0 rw {}", aname)) < 0) { std::cout << "5. створити не вдалося\n"; return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");
    std::error_code ec;
    fs::remove(apath, ec);

    long n = rpc("PREAD 0 0 16");
    std::cout << "5a. чужий дескриптор після нашого unlink: "
              << (n >= 0       ? "читається далі — сервер утримав відкритий файл" :
                  n == -ESTALE ? "ESTALE — об'єкт зник просто під дескриптором"
                               : "інша помилка читання") << "\n";
    rpc("CLOSE 0");

    if (rpc(std::format("OPEN 1 rw {}", bname)) < 0) return;
    rpc("WRITE 1 4096");
    rpc(std::format("UNLINK {}", bname));
    std::cout << "5b. з боку письменника імен «.nfs» у каталозі: " << rpc("COUNT .nfs") << "\n";

    if (dir_ttl > 0) nap_ms(static_cast<long>(dir_ttl * 1000) + 1000);
    std::cout << "    з нашого боку:                          " << count_prefix(share_dir, ".nfs") << "\n";

    rpc("CLOSE 1");
    if (dir_ttl > 0) nap_ms(static_cast<long>(dir_ttl * 1000) + 1000);
    std::cout << "5c. після close() письменника лишилося:     " << count_prefix(share_dir, ".nfs") << "\n";
}
