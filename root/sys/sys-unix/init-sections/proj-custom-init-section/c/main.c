#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <stdint.h>

/* Оголошення зовнішніх символів лінкера для меж секції my_init */
extern char __start_my_init[];
extern char __stop_my_init[];

/* Макрос для розміщення коду та даних у секції my_init із вирівнюванням */
#define __my_init __attribute__((section("my_init"), aligned(4096)))

/* Дані ініціалізації, які зберігаються у спеціальній секції */
static const char init_msg[] __my_init = "Початкове конфігурування системи та перевірка обладнання...";

/* Функція ініціалізації, яка виконує початкове налаштування */
static void __my_init run_early_setup(void)
{
    printf("[INIT] %s\n", init_msg);
    printf("[INIT] Виконано розпакування початкових структур даних.\n");
}

/* Механізм самоочищення пам'яті ініціалізації */
static void purge_init_sections(void)
{
    uintptr_t start = (uintptr_t)__start_my_init;
    uintptr_t end = (uintptr_t)__stop_my_init;
    size_t page_size = sysconf(_SC_PAGESIZE);

    /* Вирівнюємо початок вниз, а кінець вгору до меж сторінок */
    uintptr_t page_start = start & ~(page_size - 1);
    uintptr_t page_end = (end + page_size - 1) & ~(page_size - 1);
    size_t len = page_end - page_start;

    printf("[SYSTEM] Звільнення init-пам'яті: %lu байтів (початок: %p)...\n",
           (unsigned long)len, (void *)page_start);

    /* Демонтаж сторінок з адресного простору процесу */
    if (munmap((void *)page_start, len) == 0) {
        printf("[SYSTEM] Init-пам'ять успішно звільнена та повернута ОС.\n");
    } else {
        perror("[ERROR] Системний виклик munmap не вдався");
    }
}

int main(void)
{
    /* Етап 1: Виконання ініціалізації */
    run_early_setup();

    /* Етап 2: Звільнення пам'яті секції */
    purge_init_sections();

    /* Етап 3: Робочий цикл системи */
    printf("[MAIN] Основний робочий цикл запущено. Init-код більше недоступний.\n");
    return 0;
}
