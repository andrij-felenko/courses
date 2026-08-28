/* Використовуємо std::ifstream замість FILE*, std::string_view
   для пошуку прапорців у /proc/cpuinfo та RAII для очищення ресурсів. */
static void show_file(const std::string& path, const std::string& label)
{
    std::ifstream f(path);
    if (!f.is_open()) {
        std::cout << "  " << label << ": файлу немає\n";
        return;
    }
    std::string line;
    if (std::getline(f, line)) {
        std::cout << "  " << label << ": " << line << "\n";
    }
}

static bool has_flag(std::string_view flag)
{
    std::ifstream f("/proc/cpuinfo");
    if (!f.is_open()) return false;
    std::string line;
    std::string needle = " ";
    needle += flag;
    needle += " ";
    while (std::getline(f, line)) {
        if (line.rfind("flags", 0) != 0) continue;
        line += " ";
        return line.find(needle) != std::string::npos;
    }
    return false;
}

int main(int argc, char** argv)
{
    static constexpr std::array<unsigned, 8> KIB = { 0, 64, 256, 1024, 4096, 16384, 65536, 262144 };
    struct Probe {
        std::string_view name;
        void (*fn)();
    };
    static const std::array<Probe, 3> PROBES = {{
        { "clock_gettime через vDSO", probe_vdso     },
        { "clock_gettime крізь межу", probe_crossing },
        { "getppid",                  probe_getppid  },
    }};

    std::size_t bytes = static_cast<std::size_t>(MAX_KIB) * 1024;
    int cpu = (argc > 1) ? std::atoi(argv[1]) : 0;
    bool thp = (argc > 2 && std::string_view(argv[2]) == "--thp");

    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof(set), &set) != 0) {
        std::perror("sched_setaffinity");
        return 1;
    }

    auto* buf = static_cast<uint8_t*>(mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    if (buf == MAP_FAILED) { std::perror("mmap"); return 1; }

    madvise(buf, bytes, thp ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);
    std::memset(buf, 0, bytes);

    double hz = tsc_hz();

    std::cout << "режим вимірювання\n";
    std::cout << "  ядро процесора: " << cpu << ", частота TSC: " << static_cast<long>(hz / 1e6) << " МГц\n";
    show_file("/sys/devices/system/cpu/vulnerabilities/meltdown", "meltdown");
    std::cout << "  прапорці: pti=" << has_flag("pti")
              << " pcid=" << has_flag("pcid")
              << " invpcid=" << has_flag("invpcid")
              << " constant_tsc=" << has_flag("constant_tsc") << "\n";
    std::cout << "  великі сторінки: " << (thp ? "MADV_HUGEPAGE" : "MADV_NOHUGEPAGE") << "\n";

    std::cout << "\nбез робочої множини (тактів / нс на виклик)\n";
    for (const auto& probe : PROBES) {
        double t = cost(probe.fn, 200000, buf, 0, 5);
        std::cout << "  " << probe.name << ": " << t << " / " << (t * 1e9 / hz) << "\n";
    }

    std::cout << "\ngetppid під тиском на TLB (тактів / нс на виклик)\n";
    for (unsigned kib : KIB) {
        std::size_t pages = static_cast<std::size_t>(kib) * 1024 / PAGE;
        if (pages) chain(buf, pages);
        double t = cost(probe_getppid, 20000, buf, pages, 3);
        std::cout << "  " << kib << " КіБ: " << t << " / " << (t * 1e9 / hz) << "\n";
    }

    munmap(buf, bytes);
    return 0;
}
