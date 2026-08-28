#include <cerrno>
#include <cstring>
#include <string>

[[nodiscard]] std::string get_error_string(int errnum) {
    char buf[256];
#if defined(_GNU_SOURCE) && !defined(__APPLE__) && !defined(__FreeBSD__)
    char *res = strerror_r(errnum, buf, sizeof(buf));
    return std::string(res);
#else
    if (strerror_r(errnum, buf, sizeof(buf)) == 0) {
        return std::string(buf);
    }
    return "Unknown error " + std::to_string(errnum);
#endif
}
