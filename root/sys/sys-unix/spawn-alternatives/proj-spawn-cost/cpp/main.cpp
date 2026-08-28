#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <spawn.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <algorithm>
#include <chrono>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

extern char **environ;

static char HELPER[] = "./noop";
static char *ARGV[] = { HELPER, nullptr };

static double ms_between(struct timespec a, struct timespec b) {
    return static_cast<double>(b.tv_sec - a.tv_sec) * 1e3
         + static_cast<double>(b.tv_nsec - a.tv_nsec) / 1e6;
}

static struct timespec now() {
    struct timespec t{};
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t;
}

static long field_kb(const char *path, const char *key) {
    std::ifstream file(path);
    if (!file.is_open()) return -1;
    std::string line;
    while (std::getline(file, line)) {
        if (line.rfind(key, 0) == 0) {
            size_t pos = line.find_first_of("0123456789");
            if (pos != std::string::npos) {
                return std::stol(line.substr(pos));
            }
        }
    }
    return -1;
}

static void grow_parent(size_t bytes, bool huge) {
    if (bytes == 0) return;
    char *p = static_cast<char*>(mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    if (p == MAP_FAILED) {
        std::perror("mmap");
        std::exit(1);
    }
    madvise(p, bytes, huge ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);

    size_t page = static_cast<size_t>(sysconf(_SC_PAGESIZE));
    for (size_t off = 0; off < bytes; off += page) {
        p[off] = 1;
    }
}

static pid_t spawn_fork() {
    pid_t pid = ::fork();
    if (pid < 0) { std::perror("fork"); std::exit(1); }
    if (pid == 0) {
        ::execv(HELPER, ARGV);
        ::_exit(127);
    }
    return pid;
}

static pid_t spawn_vfork() {
    static const char msg[] = "execv failed\n";
    pid_t pid = ::vfork();
    if (pid < 0) { std::perror("vfork"); std::exit(1); }
    if (pid == 0) {
        ::execv(HELPER, ARGV);
        (void)!::write(STDERR_FILENO, msg, sizeof(msg) - 1);
        ::_exit(127);
    }
    return pid;
}

static pid_t spawn_posix() {
    pid_t pid = 0;
    int rc = ::posix_spawn(&pid, HELPER, nullptr, nullptr, ARGV, environ);
    if (rc != 0) {
        std::cerr << "posix_spawn: " << std::strerror(rc) << '\n';
        std::exit(1);
    }
    return pid;
}

static void reap(pid_t pid) {
    int st = 0;
    while (::waitpid(pid, &st, 0) < 0 && errno == EINTR) {}
}

template <typename Func>
static void run(std::string_view name, Func spawn_fn, int iters, std::vector<double>& v) {
    struct rusage r0{}, r1{};

    reap(spawn_fn());

    getrusage(RUSAGE_SELF, &r0);
    struct timespec t0 = now();
    for (int i = 0; i < iters; ++i) {
        struct timespec c0 = now();
        pid_t pid = spawn_fn();
        struct timespec c1 = now();
        v[i] = ms_between(c0, c1);
        reap(pid);
    }
    struct timespec t1 = now();
    getrusage(RUSAGE_SELF, &r1);

    double whole = ms_between(t0, t1) / iters;
    double sys = ((static_cast<double>(r1.ru_stime.tv_sec - r0.ru_stime.tv_sec) * 1e3)
                + (static_cast<double>(r1.ru_stime.tv_usec - r0.ru_stime.tv_usec) / 1e3))
               / iters;

    std::sort(v.begin(), v.end());
    std::cout << std::left << std::setw(12) << name << ' '
              << std::right << std::setw(9) << std::fixed << std::setprecision(3) << v[iters / 2] << ' '
              << std::setw(11) << sys << ' '
              << std::setw(10) << whole << '\n';
}

int main(int argc, char **argv) {
    size_t mib = (argc > 1) ? std::stoul(argv[1]) : 1024;
    int iters = (argc > 2) ? std::stoi(argv[2]) : 200;
    bool huge = (argc > 3 && std::string_view(argv[3]) == "--huge");

    if (iters < 3) iters = 3;
    grow_parent(mib << 20, huge);

    std::cout << "батько: " << mib << " МіБ торкнутих · VmRSS "
              << field_kb("/proc/self/status", "VmRSS:") << " КіБ · VmPTE "
              << field_kb("/proc/self/status", "VmPTE:") << " КіБ · великі сторінки "
              << field_kb("/proc/self/smaps_rollup", "AnonHugePages:") << " КіБ\n"
              << "спосіб       у виклику  sys батька     усього\n";

    std::vector<double> v(iters);
    run("fork+exec",   spawn_fork,  iters, v);
    run("vfork+exec",  spawn_vfork, iters, v);
    run("posix_spawn", spawn_posix, iters, v);
    return 0;
}
