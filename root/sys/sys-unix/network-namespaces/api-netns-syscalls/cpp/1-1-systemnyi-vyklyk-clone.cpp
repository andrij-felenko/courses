#include <sched.h>
#include <system_error>

pid_t safe_clone(int (*fn)(void*), void* stack, int flags, void* arg) {
    pid_t pid = ::clone(fn, stack, flags, arg);
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка системного виклику clone()");
    }
    return pid;
}
