#include <sys/prctl.h>
#include <system_error>
#include <cerrno>

void make_subreaper() {
    // Оголошуємо поточний процес субрепером у піддереві нащадків
    if (::prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) == -1) {
        throw std::system_error(errno, std::generic_category(), "prctl PR_SET_CHILD_SUBREAPER failed");
    }
}
