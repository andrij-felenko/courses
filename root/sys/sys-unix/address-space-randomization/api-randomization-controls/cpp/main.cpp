#include <iostream>
#include <system_error>
#include <cerrno>
#include <sys/personality.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " program [args...]\n";
        return 2;
    }

    // 1. Прочитати чинну особистість, нічого не змінюючи.
    const int cur = personality(0xffffffff);
    if (cur == -1) {
        std::cerr << "personality (read): " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return 1;
    }

    // 2. Додати один біт, зберігши все інше — і домен у молодшому байті.
    if (personality(static_cast<unsigned long>(cur) | ADDR_NO_RANDOMIZE) == -1) {
        std::cerr << "personality (set): " 
                  << std::system_error(errno, std::generic_category()).what() << '\n';
        return 1;
    }

    // 3. Карту будує саме execve — і тепер він будуватиме її без жереба.
    execvp(argv[1], &argv[1]);
    std::cerr << "execvp: " 
              << std::system_error(errno, std::generic_category()).what() << '\n';
    return 1;
}
