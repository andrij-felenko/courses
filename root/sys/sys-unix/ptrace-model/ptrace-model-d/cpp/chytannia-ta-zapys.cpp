#include <iostream>
#include <system_error>
#include <sys/ptrace.h>
#include <sys/user.h>

void inspect_registers_cpp(pid_t pid) {
    user_regs_struct regs{};
    if (::ptrace(PTRACE_GETREGS, pid, nullptr, &regs) < 0) {
        throw std::system_error(errno, std::generic_category(), "PTRACE_GETREGS failed");
    }
    std::cout << "RIP (Instruction Pointer): 0x" << std::hex << regs.rip << "\n"
              << "RSP (Stack Pointer):       0x" << regs.rsp << "\n"
              << "RAX (Syscall/Return):      0x" << regs.rax << std::dec << "\n";
}
