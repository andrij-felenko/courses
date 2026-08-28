int main(int argc, char **argv)
{
    long pg = sysconf(_SC_PAGESIZE);
    long hp = sysfs_num("/sys/kernel/mm/transparent_hugepage/hpage_pmd_size");
    if (hp <= 0) {
        std::cerr << "прозорих великих сторінок у цьому ядрі немає\n";
        return 1;
    }
    size_t hpsz = static_cast<size_t>(hp);
    int pmd_order = 0;
    for (size_t s = static_cast<size_t>(pg); s < hpsz; s <<= 1) pmd_order++;

    size_t count = 128;
    bool collapse = false;
    for (int i = 1; i < argc; i++) {
        std::string_view arg(argv[i]);
        if (arg == "--count" && i + 1 < argc) count = std::stoul(argv[++i]);
        else if (arg == "--collapse") collapse = true;
        else { std::cerr << "не знаю опції " << arg << "\n"; return 2; }
    }

    size_t total = count * hpsz;
    std::cout << "велика сторінка " << hpsz << " Б = порядок " << pmd_order
              << "; прошу " << count << " штук (" << (total / 1048576.0) << " МіБ)\n";

    void *raw = mmap(NULL, total + hpsz, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (raw == MAP_FAILED) { std::perror("mmap"); return 1; }
    auto *base = reinterpret_cast<volatile unsigned char *>(
        (reinterpret_cast<uintptr_t>(raw) + hpsz - 1) & ~(uintptr_t)(hpsz - 1));

    long a0 = vmstat("thp_fault_alloc"), f0 = vmstat("thp_fault_fallback");
    long s0 = vmstat("compact_stall"),   c0 = vmstat("compact_success");
    long thp0 = anon_thp_kb();

    std::vector<double> us(count);
    size_t ok = 0, enomem = 0, other = 0;

    if (collapse) {
        for (size_t i = 0; i < count; i++)
            for (size_t off = 0; off < hpsz; off += static_cast<size_t>(pg))
                base[i * hpsz + off] = 0xA5;
        for (size_t i = 0; i < count; i++) {
            double t = now_us();
            int rc = madvise(const_cast<void *>(static_cast<volatile void *>(base + i * hpsz)), hpsz, MADV_COLLAPSE);
            us[i] = now_us() - t;
            if (rc == 0) ok++;
            else if (errno == ENOMEM) enomem++;
            else other++;
        }
    } else {
        madvise(const_cast<void *>(static_cast<volatile void *>(base)), total, MADV_HUGEPAGE);
        for (size_t i = 0; i < count; i++) {
            double t = now_us();
            base[i * hpsz] = 0xA5;
            us[i] = now_us() - t;
        }
        long got = anon_thp_kb() - (thp0 > 0 ? thp0 : 0);
        ok = got > 0 ? static_cast<size_t>(got) / (hpsz / 1024) : 0;
        if (ok > count) ok = count;
        enomem = count - ok;
    }

    std::sort(us.begin(), us.end());
    std::cout << "дано великих сторінок: " << ok << " з " << count
              << "   (відмов: " << enomem << ", інших помилок: " << other << ")\n";
    std::cout << "затримка на шматок, мкс: медіана " << us[count / 2]
              << ", 90% " << us[count * 9 / 10] << ", найгірша " << us[count - 1] << "\n";
    std::cout << "приріст: thp_fault_alloc " << (vmstat("thp_fault_alloc") - a0)
              << ", thp_fault_fallback " << (vmstat("thp_fault_fallback") - f0)
              << ", compact_stall " << (vmstat("compact_stall") - s0)
              << ", compact_success " << (vmstat("compact_success") - c0) << "\n";

    munmap(raw, total + hpsz);
    return 0;
}
