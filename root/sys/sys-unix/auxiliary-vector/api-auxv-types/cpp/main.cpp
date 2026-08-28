#include <sys/auxv.h>
#include <iostream>
#include <cerrno>

void safe_get_auxv_cpp() {
    errno = 0;
    const unsigned long val = ::getauxval(AT_SECURE);
    const int err = errno;

    if (val == 0 && err == ENOENT) {
        std::cout << "Ключ AT_SECURE відсутній у auxv\n";
    } else {
        std::cout << "Значення AT_SECURE: " << val << "\n";
    }
}
