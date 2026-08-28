#include <iostream>
#include <system_error>
#include <unistd.h>
#include <sys/prctl.h>

void enable_debugging_access() {
    // Дозволяємо будь-якому процесу з тим самим UID підключатися через ptrace
    if (prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0) == -1) {
        throw std::system_error(errno, std::generic_category(), "Помилка налаштування PR_SET_PTRACER");
    }
    std::cout << "Процес (PID: " << getpid() << ") відкритий для підключення GDB\n";
}
