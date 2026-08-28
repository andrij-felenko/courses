#include <iostream>
#include <unistd.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <system_error>
#include <string_view>

int main() {
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT) == -1) {
        std::cerr << "Не вдалося увімкнути SECCOMP_MODE_STRICT: "
                  << std::generic_category().message(errno) << '\n';
        return 1;
    }

    constexpr std::string_view msg = "Strict Mode активний\n";
    write(STDOUT_FILENO, msg.data(), msg.size());

    // getpid() призводить до завершення SIGKILL
    ::getpid();

    return 0;
}
