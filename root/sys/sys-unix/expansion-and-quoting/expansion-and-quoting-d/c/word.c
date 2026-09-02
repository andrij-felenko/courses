#include "word.h"

#include <ctype.h>
#include <fnmatch.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void word_init(word *w)
{
    memset(w, 0, sizeof *w);
}

void word_free(word *w)
{
    free(w->text);
    free(w->mark);
    word_init(w);
}

const char *word_text(const word *w)
{
    return (w->text != NULL) ? w->text : "";
}

static int word_reserve(word *w, size_t need)
{
    if (need + 1 <= w->cap) {
        return 0;
    }
    size_t cap = (w->cap != 0) ? w->cap : 16;
    while (cap < need + 1) {
        cap *= 2;
    }

    char *text = realloc(w->text, cap);
    if (text == NULL) {
        return -1;
    }
    w->text = text;

    unsigned char *mark = realloc(w->mark, cap);
    if (mark == NULL) {
        return -1;   /* text уже переріс — не біда, його звільнить word_free */
    }
    w->mark = mark;
    w->cap = cap;
    return 0;
}

int word_append(word *w, const char *bytes, size_t n, unsigned flags)
{
    if (word_reserve(w, w->len + n) != 0) {
        return -1;
    }
    if (n != 0) {
        memcpy(w->text + w->len, bytes, n);
        memset(w->mark + w->len, (int)flags, n);
        w->len += n;
    }
    w->text[w->len] = '\0';
    return 0;
}

int word_has_active(const word *w, const char *set)
{
    for (size_t i = 0; i < w->len; ++i) {
        if ((w->mark[i] & WORD_QUOTED) == 0 && strchr(set, w->text[i]) != NULL) {
            return 1;
        }
    }
    return 0;
}

char *word_glob_pattern(const word *w)
{
    char *out = malloc(w->len * 2 + 1);
    if (out == NULL) {
        return NULL;
    }

    size_t k = 0;
    for (size_t i = 0; i < w->len; ++i) {
        /* Захищений метасимвол мусить дійти до glob(3) екранованим — інакше
           зірочка з лапок раптом почала б шукати файли. */
        if ((w->mark[i] & WORD_QUOTED) != 0 && strchr("*?[]\\", w->text[i]) != NULL) {
            out[k++] = '\\';
        }
        out[k++] = w->text[i];
    }
    out[k] = '\0';
    return out;
}

void wordlist_init(wordlist *l)
{
    memset(l, 0, sizeof *l);
}

void wordlist_free(wordlist *l)
{
    for (size_t i = 0; i < l->count; ++i) {
        word_free(&l->item[i]);
    }
    free(l->item);
    wordlist_init(l);
}

int wordlist_adopt(wordlist *l, word *w)
{
    if (l->count == l->cap) {
        const size_t cap = (l->cap != 0) ? l->cap * 2 : 8;
        word *grown = realloc(l->item, cap * sizeof *grown);
        if (grown == NULL) {
            word_free(w);
            return -1;
        }
        l->item = grown;
        l->cap = cap;
    }
    l->item[l->count++] = *w;
    word_init(w);
    return 0;
}

static char *dup_n(const char *s, size_t n)
{
    char *out = malloc(n + 1);
    if (out == NULL) {
        return NULL;
    }
    memcpy(out, s, n);
    out[n] = '\0';
    return out;
}

static void say(char *err, size_t errlen, const char *text)
{
    if (err != NULL && errlen != 0) {
        snprintf(err, errlen, "%s", text);
    }
}

/* Ім'я параметра: [A-Za-z_][A-Za-z0-9_]* */
static size_t name_length(const char *s)
{
    if (!(isalpha((unsigned char)s[0]) || s[0] == '_')) {
        return 0;
    }
    size_t n = 1;
    while (isalnum((unsigned char)s[n]) || s[n] == '_') {
        ++n;
    }
    return n;
}

/* ${VAR#маска} і ${VAR##маска}. Маску зіставляє fnmatch(3) — той самий
   матчер, яким оболонка судить і імена файлів. */
static char *trim_prefix(const char *value, const char *pattern, int longest)
{
    const size_t len = strlen(value);
    char *probe = malloc(len + 1);
    if (probe == NULL) {
        return NULL;
    }

    size_t best = (size_t)-1;
    for (size_t cut = 0; cut <= len; ++cut) {
        memcpy(probe, value, cut);
        probe[cut] = '\0';
        if (fnmatch(pattern, probe, 0) == 0) {
            best = cut;
            if (!longest) {
                break;
            }
        }
    }
    free(probe);

    const size_t from = (best == (size_t)-1) ? 0 : best;
    return dup_n(value + from, len - from);
}

static char *trim_suffix(const char *value, const char *pattern, int longest)
{
    const size_t len = strlen(value);
    size_t best = (size_t)-1;

    for (size_t cut = 0; cut <= len; ++cut) {
        if (fnmatch(pattern, value + len - cut, 0) == 0) {
            best = cut;
            if (!longest) {
                break;
            }
        }
    }
    return dup_n(value, (best == (size_t)-1) ? len : len - best);
}

/* Парна '}' усередині ${…}. Лапок тут не судимо: усе, що всередині,
   і так дістанеться модифікаторам як текст. */
static size_t brace_close(const char *s, size_t open)
{
    int depth = 0;
    for (size_t i = open; s[i] != '\0'; ++i) {
        if (s[i] == '{') {
            ++depth;
        } else if (s[i] == '}' && --depth == 0) {
            return i;
        }
    }
    return (size_t)-1;
}

/* Аргумент модифікатора сам проходить розгортання: ${A:-$B/типове}. */
static char *expand_fragment(const char *fragment, char *err, size_t errlen, int *fail)
{
    word tmp;
    const int rc = word_expand(fragment, &tmp, err, errlen);
    if (rc != 0) {
        *fail = rc;
        word_free(&tmp);
        return NULL;
    }

    char *out = dup_n(word_text(&tmp), tmp.len);
    if (out == NULL) {
        *fail = -1;
    }
    word_free(&tmp);
    return out;
}

static size_t expand_braced(const char *raw, size_t i, word *out, unsigned flags,
                            char *err, size_t errlen, int *fail)
{
    const size_t close = brace_close(raw, i + 1);
    if (close == (size_t)-1) {
        say(err, errlen, "незакрита конструкція ${…}");
        *fail = -2;
        return i;
    }

    char *inner = dup_n(raw + i + 2, close - (i + 2));
    if (inner == NULL) {
        *fail = -1;
        return i;
    }

    /* ${#VAR} — довжина значення. Рахуємо БАЙТИ; Bash у багатобайтній
       локалі рахує символи, і на кирилиці числа розійдуться вдвічі. */
    if (inner[0] == '#' && inner[1] != '\0') {
        const char *value = getenv(inner + 1);
        char buf[32];
        snprintf(buf, sizeof buf, "%zu", (value != NULL) ? strlen(value) : (size_t)0);
        if (word_append(out, buf, strlen(buf), flags | WORD_SUBST) != 0) {
            *fail = -1;
        }
        free(inner);
        return (*fail == 0) ? close + 1 : i;
    }

    const size_t n = name_length(inner);
    if (n == 0) {
        say(err, errlen, "у ${…} немає імені параметра");
        *fail = -2;
        free(inner);
        return i;
    }

    const char *rest = inner + n;
    int colon = 0;
    if (rest[0] == ':' && rest[1] != '\0' && strchr("-=+?", rest[1]) != NULL) {
        colon = 1;
        ++rest;
    }

    const char op = rest[0];
    const char *arg = (op != '\0') ? rest + 1 : rest;
    int longest = 0;
    if ((op == '#' || op == '%') && arg[0] == op) {
        longest = 1;
        ++arg;
    }

    char *name = dup_n(inner, n);
    if (name == NULL) {
        *fail = -1;
        free(inner);
        return i;
    }

    const char *value = getenv(name);
    const int unset = (value == NULL);
    const int blank = unset || value[0] == '\0';
    /* Двокрапка розширює перевірку з «не задано» на «не задано або порожнє». */
    const int missing = colon ? blank : unset;

    char *produced = NULL;
    const char *direct = NULL;

    switch (op) {
    case '\0':
        direct = unset ? "" : value;
        break;
    case '-':
        if (missing) {
            produced = expand_fragment(arg, err, errlen, fail);
        } else {
            direct = value;
        }
        break;
    case '=':
        if (missing) {
            produced = expand_fragment(arg, err, errlen, fail);
            /* := не лише підставляє, а й присвоює — побічний ефект тут навмисний. */
            if (produced != NULL && setenv(name, produced, 1) != 0) {
                *fail = -1;
            }
        } else {
            direct = value;
        }
        break;
    case '+':
        if (missing) {
            direct = "";
        } else {
            produced = expand_fragment(arg, err, errlen, fail);
        }
        break;
    case '?':
        if (missing) {
            say(err, errlen, (arg[0] != '\0') ? arg : "параметр не задано");
            *fail = -2;
        } else {
            direct = value;
        }
        break;
    case '#':
        produced = trim_prefix(unset ? "" : value, arg, longest);
        if (produced == NULL) {
            *fail = -1;
        }
        break;
    case '%':
        produced = trim_suffix(unset ? "" : value, arg, longest);
        if (produced == NULL) {
            *fail = -1;
        }
        break;
    default:
        say(err, errlen, "невідомий модифікатор у ${…}");
        *fail = -2;
        break;
    }

    if (*fail == 0) {
        const char *text = (produced != NULL) ? produced : direct;
        if (text != NULL && word_append(out, text, strlen(text), flags | WORD_SUBST) != 0) {
            *fail = -1;
        }
    }

    free(produced);
    free(name);
    free(inner);
    return (*fail == 0) ? close + 1 : i;
}

/* Розгортає конструкцію, що починається з '$' на позиції i. */
static size_t expand_dollar(const char *raw, size_t i, word *out, unsigned flags,
                            char *err, size_t errlen, int *fail)
{
    const char next = raw[i + 1];

    if (next == '(') {
        /* І $(cmd), і $((expr)) свідомо лишаються за межами прикладу:
           перше — це запуск процесу, друге — окремий обчислювач виразів.
           Обидва показує сусідній приклад на wordexp(3). */
        say(err, errlen, "підстановка команд і арифметика тут не виконуються");
        *fail = -2;
        return i;
    }
    if (next == '{') {
        return expand_braced(raw, i, out, flags, err, errlen, fail);
    }

    const size_t n = name_length(raw + i + 1);
    if (n == 0) {
        /* Долар, за яким немає імені, — звичайний символ. */
        if (word_append(out, "$", 1, flags) != 0) {
            *fail = -1;
        }
        return i + 1;
    }

    char *name = dup_n(raw + i + 1, n);
    if (name == NULL) {
        *fail = -1;
        return i;
    }
    const char *value = getenv(name);
    free(name);

    /* Незадана змінна дає порожнечу, а не помилку: WRDE_UNDEF це вибір
       того, хто кличе wordexp(3), а оболонка за замовчуванням мовчить. */
    if (value != NULL && word_append(out, value, strlen(value), flags | WORD_SUBST) != 0) {
        *fail = -1;
    }
    return i + 1 + n;
}

/* Фаза 2. Повертає індекс, з якого читати далі. */
static size_t expand_tilde(const char *raw, word *out, int *fail)
{
    if (raw[0] != '~') {
        return 0;
    }

    size_t end = 1;
    while (raw[end] != '\0' && raw[end] != '/') {
        ++end;
    }

    const char *home = NULL;
    char *user = NULL;

    if (end == 1) {
        home = getenv("HOME");
        if (home == NULL) {
            /* $HOME може бути не задано — тоді питаємо системну базу
               користувачів так само, як це робить оболонка. */
            const struct passwd *pw = getpwuid(getuid());
            home = (pw != NULL) ? pw->pw_dir : NULL;
        }
    } else if (end == 2 && raw[1] == '+') {
        home = getenv("PWD");
    } else if (end == 2 && raw[1] == '-') {
        home = getenv("OLDPWD");
    } else {
        user = dup_n(raw + 1, end - 1);
        if (user == NULL) {
            *fail = -1;
            return 0;
        }
        const struct passwd *pw = getpwnam(user);
        home = (pw != NULL) ? pw->pw_dir : NULL;
    }

    size_t consumed = 0;
    if (home != NULL) {
        /* Результат тильди не ділять на слова й не глобять — позначаємо
           його захищеним, хоч жодних лапок у записі не було. */
        if (word_append(out, home, strlen(home), WORD_QUOTED) != 0) {
            *fail = -1;
        }
        consumed = end;
    }
    /* Немає такої змінної чи користувача — тильда лишається текстом. */

    free(user);
    return consumed;
}

int word_expand(const char *raw, word *out, char *err, size_t errlen)
{
    word_init(out);
    if (err != NULL && errlen != 0) {
        err[0] = '\0';
    }

    int fail = 0;
    size_t i = expand_tilde(raw, out, &fail);

    while (raw[i] != '\0' && fail == 0) {
        const char c = raw[i];

        if (c == '\\') {
            if (raw[i + 1] != '\0') {
                if (word_append(out, raw + i + 1, 1, WORD_QUOTED) != 0) {
                    fail = -1;
                }
                i += 2;
            } else {
                if (word_append(out, "\\", 1, 0) != 0) {
                    fail = -1;
                }
                ++i;
            }
        } else if (c == '\'') {
            out->quotes = 1;
            size_t j = i + 1;
            while (raw[j] != '\0' && raw[j] != '\'') {
                ++j;
            }
            if (raw[j] == '\0') {
                say(err, errlen, "незакрита одинарна лапка");
                fail = -2;
                break;
            }
            /* Найжорсткіший захист: усе між лапками — буквальний текст. */
            if (word_append(out, raw + i + 1, j - (i + 1), WORD_QUOTED) != 0) {
                fail = -1;
            }
            i = j + 1;
        } else if (c == '"') {
            out->quotes = 1;
            size_t j = i + 1;
            int closed = 0;

            while (raw[j] != '\0' && fail == 0) {
                if (raw[j] == '"') {
                    closed = 1;
                    ++j;
                    break;
                }
                if (raw[j] == '\\' && raw[j + 1] != '\0'
                    && strchr("$`\"\\", raw[j + 1]) != NULL) {
                    /* У подвійних лапках слеш екранує лише ці чотири символи;
                       перед рештою він сам лишається буквальним. */
                    if (word_append(out, raw + j + 1, 1, WORD_QUOTED) != 0) {
                        fail = -1;
                    }
                    j += 2;
                } else if (raw[j] == '$') {
                    j = expand_dollar(raw, j, out, WORD_QUOTED, err, errlen, &fail);
                } else {
                    if (word_append(out, raw + j, 1, WORD_QUOTED) != 0) {
                        fail = -1;
                    }
                    ++j;
                }
            }

            if (fail == 0 && !closed) {
                say(err, errlen, "незакрита подвійна лапка");
                fail = -2;
                break;
            }
            i = j;
        } else if (c == '$') {
            i = expand_dollar(raw, i, out, 0, err, errlen, &fail);
        } else {
            if (word_append(out, raw + i, 1, 0) != 0) {
                fail = -1;
            }
            ++i;
        }
    }

    if (fail != 0) {
        word_free(out);
        return fail;
    }
    /* Порожній запис "" теж слово: буфер має існувати. */
    if (out->text == NULL && word_append(out, "", 0, 0) != 0) {
        return -1;
    }
    return 0;
}
