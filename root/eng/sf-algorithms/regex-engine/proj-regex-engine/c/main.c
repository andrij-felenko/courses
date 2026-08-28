#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

/* Опокоди спеціальних переходів НКА */
#define MATCH_TOKEN 256
#define SPLIT_TOKEN 257

/* Структура стану НКА Томпсона */
typedef struct State {
    int opcode;          /* Звичайний символ (0..255), MATCH_TOKEN або SPLIT_TOKEN */
    struct State *out;   /* Перший вихідний перехід */
    struct State *out1;  /* Другий вихідний перехід (тільки для SPLIT_TOKEN) */
    int last_step;       /* Маркер для відсікання дубльованих відвідувань */
} State;

/* Фрагмент НКА із незавершеними вихідними переходами */
typedef struct Fragment {
    State *start;
    State **out_list;
} Fragment;

/* Динамічна множина активних станів на поточному кроці */
typedef struct StateList {
    State **states;
    int count;
    int capacity;
} StateList;

/* Створення нового стану автомата в купі */
static State* create_state(int opcode, State *out, State *out1) {
    State *s = (State*)malloc(sizeof(State));
    if (!s) {
        fprintf(stderr, "Помилка виділення пам'яті під стан НКА\n");
        exit(EXIT_FAILURE);
    }
    s->opcode = opcode;
    s->out = out;
    s->out1 = out1;
    s->last_step = 0;
    return s;
}

/* З'єднання списку вихідних дуг із цільовим станом */
static void patch(State **l, State *s) {
    *l = s;
}

/* Перетворення інфіксного шаблону в постфіксний із вставкою крапок конкатенації */
static char* re2post(const char *re) {
    int nalt = 0, natom = 0;
    static char buf[8000];
    char *dst = buf;
    struct {
        int nalt;
        int natom;
    } paren[100], *p = paren;

    if (strlen(re) >= 1000) return NULL;

    for (; *re; re++) {
        switch (*re) {
            case '(':
                if (natom > 1) {
                    natom--;
                    *dst++ = '.';
                }
                if (p >= paren + 100) return NULL;
                p->nalt = nalt;
                p->natom = natom;
                p++;
                nalt = 0;
                natom = 0;
                break;
            case '|':
                if (natom == 0) return NULL;
                while (--natom > 0) *dst++ = '.';
                nalt++;
                break;
            case ')':
                if (p == paren || natom == 0) return NULL;
                while (--natom > 0) *dst++ = '.';
                for (; nalt > 0; nalt--) *dst++ = '|';
                --p;
                nalt = p->nalt;
                natom = p->natom;
                natom++;
                break;
            case '*':
            case '+':
            case '?':
                if (natom == 0) return NULL;
                *dst++ = *re;
                break;
            default:
                if (natom > 1) {
                    natom--;
                    *dst++ = '.';
                }
                *dst++ = *re;
                natom++;
                break;
        }
    }
    while (--natom > 0) *dst++ = '.';
    for (; nalt > 0; nalt--) *dst++ = '|';
    *dst = '\0';
    return buf;
}

/* Перетворення постфіксного регулярного виразу в НКА Томпсона */
static State* transform_postfix_to_nfa(const char *postfix_regex) {
    Fragment stack[1000];
    Fragment *stack_ptr = stack;

    for (const char *p = postfix_regex; *p != '\0'; p++) {
        switch (*p) {
            case '|': { /* Оператор вибору (альтернація) */
                Fragment e2 = *--stack_ptr;
                Fragment e1 = *--stack_ptr;
                State *s = create_state(SPLIT_TOKEN, e1.start, e2.start);
                *stack_ptr++ = (Fragment){ s, e2.out_list };
                break;
            }
            case '*': { /* Оператор ітерації Кліні */
                Fragment e = *--stack_ptr;
                State *s = create_state(SPLIT_TOKEN, e.start, NULL);
                patch(e.out_list, s);
                *stack_ptr++ = (Fragment){ s, &s->out1 };
                break;
            }
            case '.': { /* Явна або неявна конкатенація */
                Fragment e2 = *--stack_ptr;
                Fragment e1 = *--stack_ptr;
                patch(e1.out_list, e2.start);
                *stack_ptr++ = (Fragment){ e1.start, e2.out_list };
                break;
            }
            default: { /* Звичайний символьний літерал */
                State *s = create_state((unsigned char)*p, NULL, NULL);
                *stack_ptr++ = (Fragment){ s, &s->out };
                break;
            }
        }
    }

    Fragment e = *--stack_ptr;
    State *match_state = create_state(MATCH_TOKEN, NULL, NULL);
    patch(e.out_list, match_state);
    return e.start;
}

/* Обчислення ε-замикання: додавання стану та його ε-переходів у множину */
static void add_state(StateList *l, State *s, int step) {
    if (!s || s->last_step == step) return;
    s->last_step = step;

    if (s->opcode == SPLIT_TOKEN) {
        add_state(l, s->out, step);
        add_state(l, s->out1, step);
        return;
    }

    if (l->count < l->capacity) {
        l->states[l->count++] = s;
    }
}

/* Симуляція віртуальної машини Pike VM над вхідним текстом */
bool match_nfa(State *start_state, const char *text) {
    int max_states = 4096;
    StateList current_list = { (State**)malloc(max_states * sizeof(State*)), 0, max_states };
    StateList next_list = { (State**)malloc(max_states * sizeof(State*)), 0, max_states };
    int step = 1;

    add_state(&current_list, start_state, step);

    for (const char *p = text; *p != '\0'; p++) {
        step++;
        next_list.count = 0;

        for (int i = 0; i < current_list.count; i++) {
            State *s = current_list.states[i];
            if (s->opcode == (unsigned char)*p) {
                add_state(&next_list, s->out, step);
            }
        }

        StateList tmp = current_list;
        current_list = next_list;
        next_list = tmp;

        if (current_list.count == 0) break;
    }

    bool matched = false;
    for (int i = 0; i < current_list.count; i++) {
        if (current_list.states[i]->opcode == MATCH_TOKEN) {
            matched = true;
            break;
        }
    }

    free(current_list.states);
    free(next_list.states);
    return matched;
}

/* Очищення пам'яті графа НКА */
void free_nfa(State *s, int cleanup_step) {
    if (!s || s->last_step == cleanup_step) return;
    s->last_step = cleanup_step;
    free_nfa(s->out, cleanup_step);
    free_nfa(s->out1, cleanup_step);
    free(s);
}

int main(void) {
    const char *infix_pattern = "(a|b)*abb";
    const char *postfix = re2post(infix_pattern);
    printf("Інфіксний шаблон: '%s'\n", infix_pattern);
    printf("Постфіксний вираз: '%s'\n", postfix);

    State *nfa_start = transform_postfix_to_nfa(postfix);

    const char *test_pass = "ababb";
    const char *test_fail = "ababa";

    printf("Тест 1 ('%s'): %s\n", test_pass, match_nfa(nfa_start, test_pass) ? "ЗБІГ" : "НЕМАЄ ЗБІГУ");
    printf("Тест 2 ('%s'): %s\n", test_fail, match_nfa(nfa_start, test_fail) ? "ЗБІГ" : "НЕМАЄ ЗБІГУ");

    free_nfa(nfa_start, 99999);
    return 0;
}
