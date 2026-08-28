#include <sys/ioctl.h>
#include <linux/nsfs.h>
#include <system_error>

int safe_nsfs_ioctl(int netns_fd, unsigned long request) {
    int res = ::ioctl(netns_fd, request);
    if (res < 0) {
        throw std::system_error(errno, std::generic_category(), "nsfs ioctl failed");
    }
    return res;
}
