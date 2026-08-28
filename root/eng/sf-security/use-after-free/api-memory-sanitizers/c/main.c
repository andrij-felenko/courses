#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

void mte_signal_handler(int sig, siginfo_t *info, void *ucontext) {
    if (sig == SIGSEGV) {
        if (info->si_code == SEGV_MTESERR) {
            printf("[!] MTE Synchronous Fault за адресою: %p\n", info->si_addr);
            printf("[!] Зафіксовано невідповідність тегу (Use-After-Free або Buffer Overflow)!\n");
        } else if (info->si_code == SEGV_MTEAERR) {
            printf("[!] MTE Asynchronous Fault: адреса недоступна в асинхронному режимі.\n");
        }
        exit(1);
    }
}
