#include "expand.h"

#include <string.h>

int expand_line(const char *line, expansion *out)
{
    memset(out, 0, sizeof *out);
    if (line == NULL) {
        return WRDE_SYNTAX;
    }

    int status = wordexp(line, &out->we, WRDE_NOCMD | WRDE_UNDEF);
    if (status != 0) {
        /* Після невдачі вміст wordexp_t не визначений стандартом,
           тож wordfree(3) тут викликати не можна — звільнила його вже сама
           реалізація. Позначаємо структуру як порожню. */
        memset(out, 0, sizeof *out);
        return status;
    }

    out->held  = 1;
    out->words = out->we.we_wordv;
    out->count = out->we.we_wordc;
    return 0;
}

void expansion_free(expansion *e)
{
    if (e->held) {
        wordfree(&e->we);
        e->held = 0;
    }
    e->words = NULL;
    e->count = 0;
}

const char *expand_strerror(int status)
{
    switch (status) {
    case 0:
        return "успіх";
    case WRDE_BADCHAR:
        return "заборонений символ поза лапками: | & ; < > ( ) { } новий рядок";
    case WRDE_BADVAL:
        return "звертання до невизначеної змінної (діє WRDE_UNDEF)";
    case WRDE_CMDSUB:
        return "спроба підстановки команди заблокована прапором WRDE_NOCMD";
    case WRDE_NOSPACE:
        return "бракує пам'яті для вектора слів";
    case WRDE_SYNTAX:
        return "синтаксична помилка: незакриті лапки або обірваний вираз";
    default:
        return "невідомий код помилки wordexp(3)";
    }
}
