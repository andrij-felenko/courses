#include <unistd.h>
#include <sys/types.h>
#include <iostream>

void print_basic_uids() {
    const uid_t ruid = ::getuid();   // Повертає Real UID
    const uid_t euid = ::geteuid();  // Повертає Effective UID
    const gid_t rgid = ::getgid();   // Повертає Real GID
    const gid_t egid = ::getegid();  // Повертає Effective GID
    std::cout << "RUID: " << ruid << ", EUID: " << euid << '\n';
}
