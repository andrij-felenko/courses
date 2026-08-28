#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cstring>
#include <iostream>
#include <set>
#include <string>
#include <string_view>
#include <utility>

struct Context {
    std::set<std::pair<dev_t, ino_t>> seen;
    dev_t root_dev{0};
    int max_depth{256};
    unsigned long long bytes{0};
    unsigned long long errors{0};
};

static void walk(Context &c, int dfd, std::string_view label, int depth)
{
    DIR *dp = fdopendir(dfd);
    if (!dp) {
        std::cerr << "fdopendir " << label << ": " << std::strerror(errno) << "\n";
        close(dfd);
        c.errors++;
        return;
    }
    int d = dirfd(dp);

    struct dirent *e;    while (errno = 0, (e = readdir(dp)) != nullptr) {
        std::string name(e->d_name);   // копія: буфер потоку живе до наступного readdir()
        if (name == "." || name == "..") {
            continue;
        }

        struct stat st;
        if (fstatat(d, name.data(), &st, AT_SYMLINK_NOFOLLOW) < 0) {
            std::cerr << "stat " << label << "/" << name << ": " << std::strerror(errno) << "\n";
            c.errors++;
            continue;
        }

        if (!S_ISDIR(st.st_mode) && st.st_nlink > 1) {
            auto [iter, inserted] = c.seen.insert({st.st_dev, st.st_ino});
            if (!inserted) {
                continue; // вже бачили цей файл
            }
        }

        c.bytes += static_cast<unsigned long long>(st.st_blocks) * 512;

        if (!S_ISDIR(st.st_mode) || st.st_dev != c.root_dev) {
            continue;
        }
        if (depth + 1 >= c.max_depth) {
            std::cerr << "надто глибоко: " << label << "/" << name << "\n";
            c.errors++;
            continue;
        }

        int sub = openat(d, name.data(), O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        if (sub < 0) {
            std::cerr << "openat " << label << "/" << name << ": " << std::strerror(errno) << "\n";
            c.errors++;
            continue;
        }
        walk(c, sub, name, depth + 1);
    }

    if (errno != 0) {
        std::cerr << "readdir " << label << ": " << std::strerror(errno) << "\n";
        c.errors++;
    }

    closedir(dp);
}

int main(int argc, char **argv)
{
    const char *root = (argc > 1) ? argv[1] : ".";

    struct rlimit rl;
    int max_depth = 256;
    if (getrlimit(RLIMIT_NOFILE, &rl) == 0 && rl.rlim_cur != RLIM_INFINITY) {
        int half = static_cast<int>(rl.rlim_cur / 2);
        if (half < max_depth) {
            max_depth = half;
        }
    }
    if (max_depth < 8) {
        std::cerr << "замало дескрипторів для обходу\n";
        return 1;
    }

    int rfd = open(root, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (rfd < 0) {
        std::perror(root);
        return 1;
    }

    struct stat st;
    if (fstat(rfd, &st) < 0) {
        std::perror("fstat");
        close(rfd);
        return 1;
    }

    Context c;
    c.root_dev = st.st_dev;
    c.max_depth = max_depth;
    c.bytes = static_cast<unsigned long long>(st.st_blocks) * 512;

    walk(c, rfd, root, 0);

    std::cout << c.bytes << " байтів (" << (c.bytes / 1024) << " КіБ)\n";
    if (c.errors) {
        std::cerr << "пропущено через помилки: " << c.errors << "\n";
    }
    return c.errors ? 2 : 0;
}
