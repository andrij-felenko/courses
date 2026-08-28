/* Демонстрація небезпеки ручного close після vfork у C++ */
#include <unistd.h>
#include <array>

void broken_vfork_cleanup(int secret_fd) {
    pid_t pid = ::vfork();
    if (pid == 0) {
        ::close(secret_fd); // Пошкоджує стан дескриптора у батьківському процесі!
        std::array<char*, 2> argv = { const_cast<char*>("app"), nullptr };
        ::execve("/bin/app", argv.data(), nullptr);
        ::_exit(1);
    }
}
