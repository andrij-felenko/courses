#include "quoting.h"

int quoting_is_blank(char c)
{
    return c == ' ' || c == '\t' || c == '\n';
}

size_t quoting_skip(const char *line, size_t i)
{
    switch (line[i]) {
    case '\\':
        /* Екран забирає рівно один наступний байт; слеш у кінці рядка
           лишається звичайним символом. */
        return (line[i + 1] == '\0') ? i + 1 : i + 2;

    case '\'': {
        size_t j = i + 1;
        while (line[j] != '\0' && line[j] != '\'') {
            ++j;
        }
        /* Усередині одинарних лапок екрана немає: навіть \' не рятує. */
        return (line[j] == '\0') ? j : j + 1;
    }

    case '"': {
        size_t j = i + 1;
        while (line[j] != '\0' && line[j] != '"') {
            j += (line[j] == '\\' && line[j + 1] != '\0') ? 2 : 1;
        }
        return (line[j] == '\0') ? j : j + 1;
    }

    default:
        return i + 1;
    }
}

int quoting_split_words(const char *line, strvec *out)
{
    size_t i = 0;

    while (line[i] != '\0') {
        while (quoting_is_blank(line[i])) {
            ++i;
        }
        if (line[i] == '\0') {
            break;
        }

        const size_t start = i;
        /* Пробіл усередині лапок словом не ділить — quoting_skip перестрибує
           весь захищений шматок цілком. */
        while (line[i] != '\0' && !quoting_is_blank(line[i])) {
            i = quoting_skip(line, i);
        }

        if (strvec_push_n(out, line + start, i - start) != 0) {
            return -1;
        }
    }
    return 0;
}
