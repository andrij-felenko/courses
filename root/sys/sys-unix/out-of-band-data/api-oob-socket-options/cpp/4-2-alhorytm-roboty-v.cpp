#include <sys/ioctl.h>
#include <system_error>

bool is_socket_at_mark(int sockfd) {
    int mark = 0;
    if (::ioctl(sockfd, SIOCATMARK, &mark) < 0) {
        throw std::system_error(errno, std::generic_category(), "ioctl SIOCATMARK failed");
    }
    return mark != 0;
}
