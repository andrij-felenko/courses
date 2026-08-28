#include <stdio.h>
#include <stdlib.h>
#include <wordexp.h>

int safe_tokenize(const char *input_str) {
    wordexp_t p;
    /* Резервуємо 1 слот на початку для імені бінарника в argv */
    p.we_offs = 1;
    int flags = WRDE_NOCMD | WRDE_UNDEF | WRDE_DOOFFS;

    int status = wordexp(input_str, &p, flags);
    if (status != 0) {
        switch (status) {
            case WRDE_CMDSUB:
                fprintf(stderr, "Помилка безпеки: підстановка команд заборонена!\n");
                break;
            case WRDE_BADVAL:
                fprintf(stderr, "Помилка: звернення до невідомої змінної оточення.\n");
                break;
            case WRDE_SYNTAX:
                fprintf(stderr, "Синтаксична помилка у рядку вводу.\n");
                break;
            default:
                fprintf(stderr, "Помилка розгортання: код %d\n", status);
                break;
        }
        return -1;
    }

    /* Заповнюємо зарезервований argv[0] */
    p.we_wordv[0] = "/usr/bin/custom_tool";

    printf("Успішно сформовано argv (всього елементів: %zu):\n", p.we_wordc + p.we_offs);
    for (size_t i = 0; i < p.we_wordc + p.we_offs; i++) {
        printf("  argv[%zu] = %s\n", i, p.we_wordv[i]);
    }

    /* Очищаємо лише динамічні ресурси wordexp. 
       ПРИМІТКА: p.we_wordv[0] не звільняється wordfree, оскільки це літерал */
    wordfree(&p);
    return 0;
}

int main(void) {
    return safe_tokenize("$HOME/*.txt \"аргумент з пробілами\"");
}
