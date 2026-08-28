#include <sched.h>
#include <system_error>
#include <unistd.h>

// Системний виклик unshare з обробкою помилок C++
void create_user_namespace() {
    if (::unshare(CLONE_NEWUSER) == -1) {
        throw std::system_error(errno, std::generic_category(), "unshare(CLONE_NEWUSER) failed");
    }
}
