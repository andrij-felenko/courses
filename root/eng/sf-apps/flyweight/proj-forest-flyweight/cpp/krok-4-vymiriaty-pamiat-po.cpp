#include <cstdio>
#include <unistd.h>

// Резидентний набір процесу в кілобайтах.
long resident_kib() {
    long total_pages = 0, rss_pages = 0;
    if (FILE* f = std::fopen("/proc/self/statm", "r")) {
        if (std::fscanf(f, "%ld %ld", &total_pages, &rss_pages) != 2)
            rss_pages = 0;
        std::fclose(f);
    }
    return rss_pages * (sysconf(_SC_PAGESIZE) / 1024);   // сторінки → КБ
}
