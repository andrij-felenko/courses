#include <sched.h>
#include <fcntl.h>
#include <unistd.h>
#include <system_error>

void join_user_namespace(int fd) {
    if (::setns(fd, CLONE_NEWUSER) == -1) {
        throw std::system_error(errno, std::generic_category(), "setns(CLONE_NEWUSER) failed");
    }
}
