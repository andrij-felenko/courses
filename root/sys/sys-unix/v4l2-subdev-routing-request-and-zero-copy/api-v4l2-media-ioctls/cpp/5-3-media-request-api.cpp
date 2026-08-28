#include <linux/media.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <system_error>

int req_fd = -1;
if (::ioctl(media_fd, MEDIA_IOC_REQUEST_ALLOC, &req_fd) < 0) {
    throw std::system_error(errno, std::generic_category(), "REQUEST_ALLOC failed");
}

if (::ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE) < 0) {
    ::close(req_fd);
    throw std::system_error(errno, std::generic_category(), "REQUEST_QUEUE failed");
}

::ioctl(req_fd, MEDIA_REQUEST_IOC_REINIT);
::close(req_fd);
