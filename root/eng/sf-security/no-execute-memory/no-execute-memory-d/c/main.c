#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <ucontext.h>

/* Глобальний прапорець перехоплення апаратного збою */
static volatile sig_atomic_t g_caught_fault = 0;

/* Обробник сигналу сторінкового збою SIGSEGV */
static void segv_handler(int sig, siginfo_t *info, void *ucontext_raw) {
    g_caught_fault = 1;

    printf("\n[!] Апаратне перехоплення MMU: Отримано сигнал SIGSEGV (номер %d)\n", sig);
    printf("    Адреса збою (Faulting Address): %p\n", info->si_addr);

    /* Перевірка коду причини збою:
     * SEGV_ACCERR = 2 (Порушення прав доступу / Access Permissions Fault)
     * SEGV_MAPERR = 1 (Звернення за адресою, не відображеною в пам'ять)
     */
    if (info->si_code == SEGV_ACCERR) {
        printf("    Причина збою (si_code): SEGV_ACCERR (Порушення прав доступу до сторінки)\n");
        printf("    Висновок: Біт NX активний у PTE. Виконання коду зі стека заблоковано апаратно.\n");
    } else {
        printf("    Причина збою (si_code): %d\n", info->si_code);
    }

    /* Безпечний вихід із програми після фіксації перехоплення */
    _exit(EXIT_SUCCESS);
}

int main(void) {
    /* 1. Реєстрація розширеного обробника сигналу SIGSEGV */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = segv_handler;
    sa.sa_flags = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGSEGV, &sa, NULL) < 0) {
        perror("Помилка встановлення sigaction");
        return EXIT_FAILURE;
    }

    /* 2. Розміщення машинного коду на стеку (локальний масив)
     * Код інструкцій x86-64:
     *   0x90 - NOP (No Operation)
     *   0x90 - NOP
     *   0xC3 - RET (Повернення з функції)
     */
    uint8_t stack_code[] = { 0x90, 0x90, 0xC3 };

    printf("[+] Масив інструкцій розміщено на стеку за адресою: %p\n", (void *)stack_code);
    printf("[+] Спроба передачі керування процесора на стек (Instruction Fetch)...\n");

    /* 3. Приведення покажчика на масив стека до покажчика на функцію */
    typedef void (*func_ptr_t)(void);
    func_ptr_t execute_stack = (func_ptr_t)stack_code;

    /* 4. Спроба виконання: процесор завантажить адресу стека в RIP */
    execute_stack();

    /* Цей рядок ніколи не буде досягнутий, якщо біт NX увімкнено */
    printf("[-] ПОМИЛКА БЕЗПЕКИ: Код на стеку успішно виконався! Біт NX вимкнено.\n");
    return EXIT_FAILURE;
}
