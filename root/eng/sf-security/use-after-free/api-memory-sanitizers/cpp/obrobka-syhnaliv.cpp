#include <signal.h>
#include <iostream>
#include <cstdlib>

void mte_cpp_signal_handler(int sig, siginfo_t *info, void *ucontext) {
    if (sig == SIGSEGV) {
        if (info->si_code == SEGV_MTESERR) {
            std::cerr << "[!] MTE Synchronous Fault за адресою: " << info->si_addr << "\n"
                      << "[!] Зафіксовано невідповідність тегу (Use-After-Free або Buffer Overflow)!\n";
        } else if (info->si_code == SEGV_MTEAERR) {
            std::cerr << "[!] MTE Asynchronous Fault: адреса недоступна в асинхронному режимі.\n";
        }
        std::exit(1);
    }
}
