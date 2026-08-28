#include <iostream>
#include <vector>
#include <cstddef>
#include <system_error>
#include <expected>
#include <string>
#include <string_view>
#include <cstring>
#include <cerrno>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>

namespace sandbox {

#define syscall_nr (offsetof(struct seccomp_data, nr))
#define arch_nr (offsetof(struct seccomp_data, arch))

class RawCbpfSandbox {
public:
    static std::expected<void, std::string> apply_strict_worker() {
        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
            return std::unexpected("Failed to set PR_SET_NO_NEW_PRIVS: " + std::string(strerror(errno)));
        }

        const std::vector<sock_filter> filter = {
            // Завантаження та перевірка архітектури
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, arch_nr),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 0, 8),

            // Завантаження номера виклику
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, syscall_nr),

            // Дозволи для необхідних системних викликів
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 5, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 4, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_brk, 3, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mmap, 2, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group, 1, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit, 0, 1),

            // Повернення дій: ALLOW або KILL
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
        };

        const sock_fprog prog = {
            .len = static_cast<unsigned short>(filter.size()),
            .filter = const_cast<sock_filter*>(filter.data()),
        };

        if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == -1) {
            return std::unexpected("Failed to apply SECCOMP_MODE_FILTER: " + std::string(strerror(errno)));
        }

        return {};
    }
};

} // namespace sandbox

int main() {
    std::cout << "Активація C++ cBPF пісочниці...\n";
    auto res = sandbox::RawCbpfSandbox::apply_strict_worker();
    if (!res) {
        std::cerr << "Помилка: " << res.error() << '\n';
        return 1;
    }

    constexpr std::string_view msg = "C++ пісочниця активна!\n";
    write(STDOUT_FILENO, msg.data(), msg.size());
    return 0;
}
