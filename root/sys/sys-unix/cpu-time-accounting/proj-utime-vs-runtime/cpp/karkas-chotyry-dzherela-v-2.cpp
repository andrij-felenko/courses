// Джерело 1: точна сума планувальника, наносекунди, без жодної вибірки.
static double cpu_clock(clockid_t id)
{
    timespec ts{};
    if (clock_gettime(id, &ts) < 0) return -1.0;
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

// Джерело 2: поділ на режими в мікросекундах.
static std::pair<double, double> rusage_pair(int who)
{
    rusage r{};
    if (getrusage(who, &r) < 0) return {-1.0, -1.0};
    double u = r.ru_utime.tv_sec + r.ru_utime.tv_usec / 1e6;
    double s = r.ru_stime.tv_sec + r.ru_stime.tv_usec / 1e6;
    return {u, s};
}

// Джерело 3: поля 14 і 15 у stat — той самий поділ, але в тиках USER_HZ.
static std::pair<bool, std::pair<double, double>> proc_stat_cpu(std::string_view path)
{
    std::string content = slurp(path);
    if (content.empty()) return {false, {-1.0, -1.0}};

    auto pos = content.rfind(')');
    if (pos == std::string::npos || pos + 2 >= content.size())
        return {false, {-1.0, -1.0}};

    std::istringstream iss(content.substr(pos + 2));
    char state;
    int ppid, pgrp, session, tty, tpgid;
    unsigned flags;
    unsigned long minflt, cminflt, majflt, cmajflt, ut = 0, st = 0;

    if (iss >> state >> ppid >> pgrp >> session >> tty >> tpgid
            >> flags >> minflt >> cminflt >> majflt >> cmajflt >> ut >> st) {
        return {true, {ut / clk_tck(), st / clk_tck()}};
    }
    return {false, {-1.0, -1.0}};
}

// Джерело 4: перше число schedstat — se.sum_exec_runtime у наносекундах.
static std::pair<bool, double> proc_runtime(std::string_view path)
{
    std::string content = slurp(path);
    if (content.empty()) return {false, -1.0};

    std::istringstream iss(content);
    unsigned long long ns = 0;
    if (iss >> ns) return {true, ns / 1e9};
    return {false, -1.0};
}
