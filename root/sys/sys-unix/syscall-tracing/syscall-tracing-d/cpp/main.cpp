// Ідіоматичний C++ еквівалент модифікації регістрів
#include <sys/ptrace.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <system_error>
#include <cerrno>

void modifySyscallArg(pid_t traceePid) {
    user_regs_struct regs{};
    if (ptrace(PTRACE_GETREGS, traceePid, nullptr, &regs) < 0) {
        throw std::system_error(errno, std::generic_category(), "PTRACE_GETREGS failed");
    }

    // Якщо це системний виклик write (SYS_write == 1 на x86_64)
    if (regs.orig_rax == 1) {
        regs.rdx = 0; // Зменшуємо розмір запису до 0
        if (ptrace(PTRACE_SETREGS, traceePid, nullptr, &regs) < 0) {
            throw std::system_error(errno, std::generic_category(), "PTRACE_SETREGS failed");
        }
    }
}
