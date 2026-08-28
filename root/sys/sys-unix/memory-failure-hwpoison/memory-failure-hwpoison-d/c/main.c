#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

void sigbus_handler(int sig, siginfo_t *si, void *context) {
    if (sig == SIGBUS) {
        if (si->si_code == BUS_MCEERR_AR) {
            printf("Критична апаратна помилка (Action Required) за адресою: %p\n", si->si_addr);
            // Тут можна спробувати коректно впасти або зберегти стан
            _exit(1);
        } else if (si->si_code == BUS_MCEERR_AO) {
            printf("Фонова апаратна помилка (Action Optional) за адресою: %p\n", si->si_addr);
            // Можна спробувати звільнити цей регіон, якщо програма це підтримує
        } else {
            printf("Інший SIGBUS\n");
            _exit(1);
        }
    }
}
