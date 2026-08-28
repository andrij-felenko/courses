/* sync-cost.cpp — ціна кожного різновиду синхронізації і перевірка,
   чи скидав при цьому пристрій власний кеш.
   збірка: g++ -O2 -Wall -Wextra -std=c++20 -o sync-cost sync-cost.cpp
   запуск: ./sync-cost /каталог/на/справжньому/диску            */
#define _GNU_SOURCE
#include <cerrno>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <algorithm>
#include <chrono>
#include <array>
#include <string>
#include <vector>
#include <iostream>
#include <fstream>

constexpr size_t BLK = 4096;
constexpr int REPS = 200;
constexpr int PREFILL = 64;
constexpr size_t BIG = 64 << 20;

static std::array<char, BLK> blk;
static std::string DSTAT;

[[noreturn]] static void die(const char* what) {
    std::perror(what);
    std::exit(1);
}

static double now_ms() {
    using namespace std::chrono;
    auto now = steady_clock::now();
    return duration<double, std::milli>(now.time_since_epoch()).count();
}

static double median(std::vector<double>& v) {
    std::sort(v.begin(), v.end());
    size_t n = v.size();
    return (n % 2 != 0) ? v[n / 2] : (v[n / 2 - 1] + v[n / 2]) / 2.0;
}

static int disk_stat_path(const char* path, char* out, size_t outsz) {
    struct stat st{};
    if (::stat(path, &st) != 0) return errno;

    char node[128], probe[160];
    std::snprintf(node, sizeof(node), "/sys/dev/block/%u:%u",
                  major(st.st_dev), minor(st.st_dev));
    std::snprintf(probe, sizeof(probe), "%s/partition", node);

    std::snprintf(out, outsz, "%s%s/stat", node,
                  (::access(probe, F_OK) == 0) ? "/.." : "");
    return 0;
}

struct dstat {
    unsigned long long writes = 0;
    unsigned long long flushes = 0;
    unsigned long long flush_ms = 0;
    int fields = 0;
};

static int read_dstat(const std::string& p, dstat& d) {
    std::ifstream f(p);
    if (!f) return errno;
    std::vector<unsigned long long> v;
    unsigned long long val;
    while (v.size() < 17 && (f >> val)) {
        v.push_back(val);
    }
    d.fields = static_cast<int>(v.size());
    d.writes = (v.size() >= 5) ? v[4] : 0;
    d.flushes = (v.size() >= 16) ? v[15] : 0;
    d.flush_ms = (v.size() >= 17) ? v[16] : 0;
    return (v.size() >= 5) ? 0 : EINVAL;
}

static void report(const char* tag, std::vector<double>& t,
                   const dstat& a, const dstat& b) {
    std::printf("%-32s медіана %8.3f мс   записів: %-5llu скидань: %-5llu (на %zu)\n",
                tag, median(t),
                b.writes - a.writes, b.flushes - a.flushes, t.size());
    std::fflush(stdout);
}

static void series(const char* tag, int fd, bool append, bool datasync) {
    std::vector<double> t(REPS);
    dstat a{}, b{};

    read_dstat(DSTAT, a);
    for (int i = 0; i < REPS; i++) {
        blk[0] = static_cast<char>(i);
        if (append) {
            if (::write(fd, blk.data(), BLK) != static_cast<ssize_t>(BLK)) die("write");
        } else {
            off_t off = static_cast<off_t>(i % PREFILL) * BLK;
            if (::pwrite(fd, blk.data(), BLK, off) != static_cast<ssize_t>(BLK)) die("pwrite");
        }
        double t0 = now_ms();
        int rc = datasync ? ::fdatasync(fd) : ::fsync(fd);
        double t1 = now_ms();
        if (rc != 0) die("sync");
        t[i] = t1 - t0;
    }
    read_dstat(DSTAT, b);
    report(tag, t, a, b);
}

int main(int argc, char** argv) {
    const char* dir = (argc > 1) ? argv[1] : ".";
    char dstat_buf[512], path[4096];
    dstat probe{}, a{}, b{};
    std::vector<double> t(REPS);

    if (disk_stat_path(dir, dstat_buf, sizeof(dstat_buf)) != 0) die("stat каталогу");
    DSTAT = dstat_buf;
    if (read_dstat(DSTAT, probe) != 0) {
        std::fprintf(stderr, "лічильники недоступні (%s): tmpfs, складений том "
                             "або каталог не на блоковому пристрої\n", DSTAT.c_str());
        return 1;
    }
    std::printf("лічильники: %s (%d полів%s)\n\n", DSTAT.c_str(), probe.fields,
                probe.fields >= 17 ? "" : "; скидання НЕ рахуються — ядро до 5.5");

    std::snprintf(path, sizeof(path), "%s/sync-cost.dat", dir);
    int fd = ::open(path, O_RDWR | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) die(path);

    unsigned long long s = 88172645463325252ULL;
    for (size_t i = 0; i < blk.size(); i++) {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        blk[i] = static_cast<char>(s);
    }

    if (::fsync(fd) != 0) die("fsync");
    read_dstat(DSTAT, a);
    for (int i = 0; i < REPS; i++) {
        double t0 = now_ms();
        if (::fsync(fd) != 0) die("fsync");
        t[i] = now_ms() - t0;
    }
    read_dstat(DSTAT, b);
    report("fsync без жодної зміни", t, a, b);

    std::vector<double> t_big(5);
    for (int r = 0; r < 5; r++) {
        if (::ftruncate(fd, 0) != 0) die("ftruncate");
        if (::lseek(fd, 0, SEEK_SET) < 0) die("lseek");
        for (size_t i = 0; i < BIG / BLK; i++)
            if (::write(fd, blk.data(), BLK) != static_cast<ssize_t>(BLK)) die("write");
        double t0 = now_ms();
        if (::fsync(fd) != 0) die("fsync");
        t_big[r] = now_ms() - t0;
    }
    std::printf("%-32s медіана %8.3f мс\n", "fsync після 64 МіБ у кеші",
                median(t_big));

    if (::ftruncate(fd, 0) != 0) die("ftruncate");
    if (::lseek(fd, 0, SEEK_SET) < 0) die("lseek");
    for (int i = 0; i < PREFILL; i++)
        if (::write(fd, blk.data(), BLK) != static_cast<ssize_t>(BLK)) die("write");
    if (::fsync(fd) != 0) die("fsync");

    series("перезапис 4 КіБ + fdatasync",   fd, false, true);
    series("перезапис 4 КіБ + fsync",       fd, false, false);

    if (::lseek(fd, 0, SEEK_END) < 0) die("lseek");
    series("дописування 4 КіБ + fdatasync", fd, true, true);
    series("дописування 4 КіБ + fsync",     fd, true, false);

    ::close(fd);
    ::unlink(path);
    return 0;
}
