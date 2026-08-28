#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

typedef enum {
    VAL_NIL,
    VAL_NUM,
    VAL_SYM,
    VAL_PAIR,
    VAL_PRIM,
    VAL_CLOSURE
} ValType;

struct Value;
struct Env;

typedef struct Value* (*PrimFn)(struct Value* args, struct Env* env);

typedef struct Value {
    ValType type;
    union {
        long num;
        char* sym;
        struct {
            struct Value* car;
            struct Value* cdr;
        } pair;
        PrimFn prim;
        struct {
            struct Value* params;
            struct Value* body;
            struct Env* env;
        } closure;
    } as;
} Value;

typedef struct Env {
    struct Value* vars;  /* Список символів (param1 param2 ...) */
    struct Value* vals;  /* Список значень (val1 val2 ...) */
    struct Env* parent;  /* Батьківське лексичне оточення */
} Env;

static Value val_nil_singleton = { VAL_NIL, { .num = 0 } };
#define NIL (&val_nil_singleton)

Value* make_num(long n) {
    Value* v = (Value*)malloc(sizeof(Value));
    v->type = VAL_NUM;
    v->as.num = n;
    return v;
}

Value* make_sym(const char* name) {
    Value* v = (Value*)malloc(sizeof(Value));
    v->type = VAL_SYM;
    v->as.sym = strdup(name);
    return v;
}

Value* make_pair(Value* car, Value* cdr) {
    Value* v = (Value*)malloc(sizeof(Value));
    v->type = VAL_PAIR;
    v->as.pair.car = car;
    v->as.pair.cdr = cdr;
    return v;
}

Value* make_prim(PrimFn fn) {
    Value* v = (Value*)malloc(sizeof(Value));
    v->type = VAL_PRIM;
    v->as.prim = fn;
    return v;
}

Value* make_closure(Value* params, Value* body, Env* env) {
    Value* v = (Value*)malloc(sizeof(Value));
    v->type = VAL_CLOSURE;
    v->as.closure.params = params;
    v->as.closure.body = body;
    v->as.closure.env = env;
    return v;
}

/* Робота з оточенням */
Env* make_env(Value* vars, Value* vals, Env* parent) {
    Env* e = (Env*)malloc(sizeof(Env));
    e->vars = vars;
    e->vals = vals;
    e->parent = parent;
    return e;
}

Value* env_get(Env* env, const char* sym) {
    for (Env* e = env; e != NULL; e = e->parent) {
        Value* p_var = e->vars;
        Value* p_val = e->vals;
        while (p_var != NIL && p_val != NIL) {
            if (p_var->as.pair.car->type == VAL_SYM &&
                strcmp(p_var->as.pair.car->as.sym, sym) == 0) {
                return p_val->as.pair.car;
            }
            p_var = p_var->as.pair.cdr;
            p_val = p_val->as.pair.cdr;
        }
    }
    return NULL;
}

void env_set(Env* env, const char* sym, Value* val) {
    env->vars = make_pair(make_sym(sym), env->vars);
    env->vals = make_pair(val, env->vals);
}

/* Парсер: перетворення тексту на S-вирази */
const char* skip_ws(const char* s) {
    while (*s && (isspace((unsigned char)*s) || *s == ';')) {
        if (*s == ';') {
            while (*s && *s != '\n') s++;
        } else {
            s++;
        }
    }
    return s;
}

Value* read_expr(const char** src);

Value* read_list(const char** src) {
    *src = skip_ws(*src);
    if (**src == ')') {
        (*src)++;
        return NIL;
    }
    Value* car = read_expr(src);
    Value* cdr = read_list(src);
    return make_pair(car, cdr);
}

Value* read_expr(const char** src) {
    *src = skip_ws(*src);
    if (!**src) return NIL;

    if (**src == '(') {
        (*src)++;
        return read_list(src);
    }
    if (**src == '\'') {
        (*src)++;
        return make_pair(make_sym("quote"), make_pair(read_expr(src), NIL));
    }

    /* Число або символ */
    const char* start = *src;
    while (**src && !isspace((unsigned char)**src) && **src != '(' && **src != ')') {
        (*src)++;
    }
    int len = (int)(*src - start);
    char buf[128];
    if (len >= 127) len = 126;
    strncpy(buf, start, len);
    buf[len] = '\0';

    char* endp;
    long num = strtol(buf, &endp, 10);
    if (*endp == '\0' && len > 0 && (isdigit((unsigned char)buf[0]) || (buf[0] == '-' && len > 1))) {
        return make_num(num);
    }
    return make_sym(buf);
}

/* Обчислення: eval та apply */
Value* eval(Value* exp, Env* env);

Value* eval_list(Value* list, Env* env) {
    if (list == NIL) return NIL;
    Value* car = eval(list->as.pair.car, env);
    Value* cdr = eval_list(list->as.pair.cdr, env);
    return make_pair(car, cdr);
}

Value* apply(Value* fn, Value* args, Env* env) {
    if (fn->type == VAL_PRIM) {
        return fn->as.prim(args, env);
    }
    if (fn->type == VAL_CLOSURE) {
        Env* call_env = make_env(fn->as.closure.params, args, fn->as.closure.env);
        Value* res = NIL;
        Value* b = fn->as.closure.body;
        while (b != NIL) {
            res = eval(b->as.pair.car, call_env);
            b = b->as.pair.cdr;
        }
        return res;
    }
    fprintf(stderr, "Помилка: спроба виклику не-функції\n");
    return NIL;
}

Value* eval(Value* exp, Env* env) {
    if (exp == NIL) return NIL;
    if (exp->type == VAL_NUM) return exp;
    if (exp->type == VAL_SYM) {
        Value* v = env_get(env, exp->as.sym);
        if (!v) {
            fprintf(stderr, "Помилка: невідома змінна '%s'\n", exp->as.sym);
            return NIL;
        }
        return v;
    }
    if (exp->type == VAL_PAIR) {
        Value* op = exp->as.pair.car;
        Value* args = exp->as.pair.cdr;

        /* Спеціальні форми */
        if (op->type == VAL_SYM) {
            if (strcmp(op->as.sym, "quote") == 0) {
                return args->as.pair.car;
            }
            if (strcmp(op->as.sym, "if") == 0) {
                Value* cond = eval(args->as.pair.car, env);
                if (cond != NIL && (cond->type != VAL_NUM || cond->as.num != 0)) {
                    return eval(args->as.pair.cdr->as.pair.car, env);
                } else {
                    Value* alt = args->as.pair.cdr->as.pair.cdr;
                    return alt != NIL ? eval(alt->as.pair.car, env) : NIL;
                }
            }
            if (strcmp(op->as.sym, "define") == 0) {
                const char* sym = args->as.pair.car->as.sym;
                Value* val = eval(args->as.pair.cdr->as.pair.car, env);
                env_set(env, sym, val);
                return val;
            }
            if (strcmp(op->as.sym, "lambda") == 0) {
                Value* params = args->as.pair.car;
                Value* body = args->as.pair.cdr;
                return make_closure(params, body, env);
            }
        }

        /* Звичайний виклик функції */
        Value* fn = eval(op, env);
        Value* evaled_args = eval_list(args, env);
        return apply(fn, evaled_args, env);
    }
    return exp;
}

/* Вбудовані примітиви */
Value* prim_add(Value* args, Env* env) {
    (void)env;
    long sum = 0;
    while (args != NIL) {
        if (args->as.pair.car->type == VAL_NUM) sum += args->as.pair.car->as.num;
        args = args->as.pair.cdr;
    }
    return make_num(sum);
}

Value* prim_mul(Value* args, Env* env) {
    (void)env;
    long prod = 1;
    while (args != NIL) {
        if (args->as.pair.car->type == VAL_NUM) prod *= args->as.pair.car->as.num;
        args = args->as.pair.cdr;
    }
    return make_num(prod);
}

Value* prim_car(Value* args, Env* env) {
    (void)env;
    Value* p = args->as.pair.car;
    return p->type == VAL_PAIR ? p->as.pair.car : NIL;
}

Value* prim_cdr(Value* args, Env* env) {
    (void)env;
    Value* p = args->as.pair.car;
    return p->type == VAL_PAIR ? p->as.pair.cdr : NIL;
}

Value* prim_cons(Value* args, Env* env) {
    (void)env;
    return make_pair(args->as.pair.car, args->as.pair.cdr->as.pair.car);
}

void print_expr(Value* v) {
    if (v == NIL) { printf("()"); return; }
    switch (v->type) {
        case VAL_NUM: printf("%ld", v->as.num); break;
        case VAL_SYM: printf("%s", v->as.sym); break;
        case VAL_PRIM: printf("<primitive>"); break;
        case VAL_CLOSURE: printf("<closure>"); break;
        case VAL_PAIR:
            printf("(");
            while (v != NIL) {
                if (v->type != VAL_PAIR) {
                    printf(". ");
                    print_expr(v);
                    break;
                }
                print_expr(v->as.pair.car);
                v = v->as.pair.cdr;
                if (v != NIL && v->type == VAL_PAIR) printf(" ");
            }
            printf(")");
            break;
        default: break;
    }
}
