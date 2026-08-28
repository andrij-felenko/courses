#include <sys/capsicum.h>
#include <fcntl.h>
#include <unistd.h>
#include <system_error>
#include <cerrno>

namespace capsicum_demo {

void run_sandboxed() {
    /* 1. Відкриваємо файл у звичайному режимі */
    int fd = ::open("/tmp/output.dat", O_RDWR | O_CREAT, 0600);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }

    /* 2. Обмежуємо дескриптор лише правом читання та fstat */
    cap_rights_t rights;
    ::cap_rights_init(&rights, CAP_READ, CAP_FSTAT);
    if (::cap_rights_limit(fd, &rights) < 0) {
        ::close(fd);
        throw std::system_error(errno, std::generic_category(), "cap_rights_limit failed");
    }

    /* 3. Входимо в режим повної ізоляції */
    if (::cap_enter() < 0) {
        ::close(fd);
        throw std::system_error(errno, std::generic_category(), "cap_enter failed");
    }

    /* Прямий open тепер неможливий: повертає -1, errno = ECAPMODE */
    int bad = ::open("/etc/passwd", O_RDONLY);
    (void)bad;

    /* Запис у fd заборонено: повертає -1, errno = ENOTCAPABLE */
    ssize_t w = ::write(fd, "test", 4);
    (void)w;

    ::close(fd);
}

} // namespace capsicum_demo
