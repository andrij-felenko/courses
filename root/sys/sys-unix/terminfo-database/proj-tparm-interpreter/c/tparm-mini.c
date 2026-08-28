/* tparm-mini.c — тлумач рядків terminfo з параметрами.
   Складання:  cc -std=c11 -O2 -Wall -o tparm-mini tparm-mini.c        */

#include <ctype.h>
#include <stdio.h>
#include <string.h>

#define NPARM   9
#define STACKN  64
#define OUTN    1024

typedef struct { long num; const char *str; } Val;  /* str != NULL → рядок */

typedef struct {
    Val         parm[NPARM];
    Val         stack[STACKN];
    int         sp;
    long        dyn[26];               /* %Pa … %Pz                        */
    char        out[OUTN];
    size_t      olen;
    const char *err;
} Vm;

static long svar[26];                  /* %PA … %PZ — поза машиною навмисно */

static Val N(long n)        { Val v = { n, NULL }; return v; }
static Val S(const char *s) { Val v = { 0,  s   }; return v; }

/* ── дрібні дії ─────────────────────────────────────────────────────── */

static void push(Vm *m, Val v)
{
    if (m->sp < STACKN) m->stack[m->sp++] = v;
    else                m->err = "переповнення стека";
}

static void push_num(Vm *m, long n) { push(m, N(n)); }

static Val pop(Vm *m)
{
    if (m->sp > 0) return m->stack[--m->sp];
    m->err = "стек порожній";
    return N(0);                       /* хибний рецепт не валить програму */
}

static long pop_num(Vm *m)
{
    Val v = pop(m);
    if (v.str) { m->err = "потрібне число, а на стеку рядок"; return 0; }
    return v.num;
}

static void emit(Vm *m, int byte)
{
    if (m->olen + 1 < OUTN) m->out[m->olen++] = (char) byte;
    else                    m->err = "переповнення виводу";
}

static void emit_str(Vm *m, const char *s)
{
    while (*s) emit(m, (unsigned char) *s++);
}

/* ── пропуск гілки ──────────────────────────────────────────────────────
   Іде рецептом до межі гілки СВОЄГО рівня вкладеності й повертає позицію
   відразу за нею. want_else — зупинятися і на «%e», а не лише на «%;».   */

static const char *skip_to(const char *p, int want_else)
{
    int depth = 0;

    while (*p) {
        if (*p++ != '%') continue;
        if (!*p) break;
        switch (*p++) {
        case '?':  depth++;                                        break;
        case ';':  if (depth == 0) return p;  depth--;             break;
        case 'e':  if (depth == 0 && want_else) return p;          break;
        case '{':  while (*p && *p != '}') p++;  if (*p) p++;      break;
        case '\'': if (*p) p++;  if (*p == '\'') p++;              break;
        case 'p': case 'P': case 'g': if (*p) p++;                 break;
        }
    }
    return p;                                   /* рецепт обірвався — стоп */
}

/* ── сама машина ────────────────────────────────────────────────────── */

static const char *expand(Vm *m, const char *recipe, int argc, const Val *argv)
{
    const char *p = recipe;
    int i;

    memset(m, 0, sizeof *m);
    for (i = 0; i < argc && i < NPARM; i++) m->parm[i] = argv[i];

    while (!m->err && *p) {
        long x, y;
        Val  v;
        char buf[24];
        int  c;

        if (*p != '%') { emit(m, (unsigned char) *p++); continue; }
        p++;                                        /* пропустити сам «%» */

        switch (c = (unsigned char) *p++) {

        case '%': emit(m, '%');                                       break;
        case 'i': m->parm[0].num++; m->parm[1].num++;                 break;

        case 'p': c = *p++ - '1';
                  if (c < 0 || c >= NPARM) m->err = "хибний номер параметра";
                  else push(m, m->parm[c]);                           break;

        case 'P': c = (unsigned char) *p++;
                  if      (islower(c)) m->dyn[c - 'a'] = pop_num(m);
                  else if (isupper(c)) svar[c - 'A']   = pop_num(m);
                  else m->err = "хибне ім'я змінної";                 break;

        case 'g': c = (unsigned char) *p++;
                  if      (islower(c)) push_num(m, m->dyn[c - 'a']);
                  else if (isupper(c)) push_num(m, svar[c - 'A']);
                  else m->err = "хибне ім'я змінної";                 break;

        case '{': x = 0;
                  while (isdigit((unsigned char) *p)) x = x * 10 + (*p++ - '0');
                  if (*p == '}') p++; else m->err = "не закрито «}»";
                  push_num(m, x);                                     break;

        case '\'': if (!*p) { m->err = "обірваний рецепт"; break; }
                   push_num(m, (unsigned char) *p++);
                   if (*p == '\'') p++; else m->err = "не закрито лапку";
                                                                      break;

        case 'l': v = pop(m); push_num(m, v.str ? (long) strlen(v.str) : 0);
                                                                      break;

        /* друк: знімає верхівку */
        case 'd': snprintf(buf, sizeof buf, "%ld", pop_num(m));
                  emit_str(m, buf);                                   break;
        case 's': v = pop(m); emit_str(m, v.str ? v.str : "");        break;
        case 'c': emit(m, (int) (pop_num(m) & 0xff));                 break;

        /* двомісні: ПЕРШИЙ знятий — правий операнд («%gx%{5}%-» = x−5) */
        case '+': x = pop_num(m); y = pop_num(m); push_num(m, y +  x); break;
        case '-': x = pop_num(m); y = pop_num(m); push_num(m, y -  x); break;
        case '*': x = pop_num(m); y = pop_num(m); push_num(m, y *  x); break;
        case '/': x = pop_num(m); y = pop_num(m); push_num(m, x ? y / x : 0);
                                                                       break;
        case 'm': x = pop_num(m); y = pop_num(m); push_num(m, x ? y % x : 0);
                                                                       break;
        case '&': x = pop_num(m); y = pop_num(m); push_num(m, y &  x); break;
        case '|': x = pop_num(m); y = pop_num(m); push_num(m, y |  x); break;
        case '^': x = pop_num(m); y = pop_num(m); push_num(m, y ^  x); break;
        case '=': x = pop_num(m); y = pop_num(m); push_num(m, y == x); break;
        case '<': x = pop_num(m); y = pop_num(m); push_num(m, y <  x); break;
        case '>': x = pop_num(m); y = pop_num(m); push_num(m, y >  x); break;
        case 'A': x = pop_num(m); y = pop_num(m); push_num(m, y && x); break;
        case 'O': x = pop_num(m); y = pop_num(m); push_num(m, y || x); break;
        case '!': push_num(m, !pop_num(m));                            break;
        case '~': push_num(m, ~pop_num(m));                            break;

        case '?':                     /* лише позначка: код умови йде далі */
                                                                       break;
        case 't': if (!pop_num(m)) p = skip_to(p, 1);                  break;
        case 'e': p = skip_to(p, 0);  /* сюди доходять по виконаній гілці */
                                                                       break;
        case ';':                                                      break;

        default:  m->err = "невідомий оператор";                       break;
        }
    }

    m->out[m->olen] = '\0';
    return m->err ? NULL : m->out;      /* довжина — в m->olen, не strlen */
}

/* ── перевірка ──────────────────────────────────────────────────────── */

static void show(const char *label, const char *bytes)
{
    const unsigned char *b;

    printf("%-12s", label);
    if (!bytes) { printf("(помилка розбору)\n"); return; }
    for (b = (const unsigned char *) bytes; *b; b++) printf("%02x ", *b);
    printf(" | ");
    for (b = (const unsigned char *) bytes; *b; b++)
        putchar(*b == 0x1b ? '^' : *b);
    putchar('\n');
}

int main(void)
{
    static const char cup[]   = "\033[%i%p1%d;%p2%dH";
    static const char setaf[] = "\033[%?%p1%{8}%<%t3%p1%d"
                                "%e%p1%{16}%<%t9%p1%{8}%-%d"
                                "%e38;5;%p1%d%;m";
    /* вигаданий рецепт у дусі pfx: номер клавіші байтом, тоді довжина
       й сам рядок — щоб перевірити рядковий параметр і «%l»            */
    static const char pfx[]   = "\033Z%p1%'0'%+%c%p2%l%d;%p2%s";
    Vm  m;
    Val a[2];

    a[0] = N(9); a[1] = N(2);
    show("cup 9 2",   expand(&m, cup,   2, a));

    a[0] = N(1);   show("setaf 1",   expand(&m, setaf, 1, a));
    a[0] = N(9);   show("setaf 9",   expand(&m, setaf, 1, a));
    a[0] = N(200); show("setaf 200", expand(&m, setaf, 1, a));

    a[0] = N(3); a[1] = S("ls");
    show("pfx 3 ls",  expand(&m, pfx,   2, a));
    return 0;
}
