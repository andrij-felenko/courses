# ⚙️ Мінімальний інтерпретатор Lisp: токенізатор, S-вирази та цикл eval/apply

Найшвидший і найбільш наочний спосіб вивчити внутрішню архітектуру Lisp — побудувати мінімальний повнофункціональний інтерпретатор. У більшості традиційних імперативних мов компілятор або інтерпретатор вимагає тисяч рядків коду: складні лексичні аналізатори, LALR/LL-парсери, таблиці пріоритетів операторів та десятки різнорідних класів для кожного типу вузла абстрактного синтаксичного дерева (AST).

У Lisp уся система обчислення базується на єдиній універсальній структурі — списку парних комірок (**cons cells**), а весь процес інтерпретації вичерпується чотирма фазами класичного циклу **REPL** (*Read-Eval-Print Loop*):

1. **Read (Читання):** текстовий потік символів перетворюється на живе дерево cons-структур у динамічній пам'яті.
2. **Eval (Обчислення):** дерево S-виразів рекурсивно обчислюється відносно поточного середовища (оточення) змінних.
3. **Print (Друк):** результуюча структура даних серіалізується назад у дужковий рядок.
4. **Loop (Цикл):** повернення до очікування нового вводу користувача.

Нижче наведено повну реалізацію мінімального інтерпретатора мовами C та C++, здатного виконувати арифметику, створювати змінні, обробляти умовні розгалуження та підтримувати анонімні функції (лямбди) з повноцінними лексичними замиканнями.

## Модель пам'яті та представлення значень

Кожен об'єкт у Lisp є динамічно типізованим значенням (`Value`). В інтерпретаторі підтримуються шість базових типів:
- **VAL_NIL:** синглтон порожнього списку, який одночасно виступає булевим значенням хибності;
- **VAL_NUM:** 64-бітне ціле число;
- **VAL_SYM:** ідентифікатор (символ), що використовується як ім'я змінної або оператора;
- **VAL_PAIR:** комірка cons із двома покажчиками (`car` — голова списку або елемент, `cdr` — хвіст або наступна пара);
- **VAL_PRIM:** вказівник на системну функцію (примітив середовища виконання);
- **VAL_CLOSURE:** користувацька функція, утворена спеціальною формою `lambda`, що інкапсулює формальні параметри, вирази тіла та вказівник на лексичне оточення, в якому вона була створена.

## Лексичне оточення (Environment)

Оточення в Lisp організоване як зв'язаний ланцюжок фреймів (**frames**). Кожен фрейм містить локальну таблицю зіставлення «символ → значення» та покажчик на батьківський фрейм (`parent`). 

Під час пошуку значення змінної функція `env_get` спершу шукає символ у поточному фреймі. Якщо його там немає, пошук рекурсивно піднімається батьківськими зв'язками до глобального рівня. Якщо символ не знайдено і в глобальному оточенні, генерується помилка незв'язаної змінної (*unbound variable*).

Коли викликається користувацька функція (лямбда), інтерпретатор створює новий локальний фрейм, батьком якого стає оточення, збережене всередині замикання в момент визначення функції (а не оточення місця виклику). Саме це забезпечує **лексичну область видимості** (*lexical scoping*).

## Робота парсера (Reader)

Парсер Lisp надзвичайно простий і реалізується методом рекурсивного спуску. Оскільки мова не має інфіксних операторів та складних граматичних правил, рідерові достатньо розрізняти лише три синтаксичні ситуації:
- Зустрілася відкриваюча дужка `(` — викликається функція `read_list`, яка рекурсивно зчитує вирази до зустрічі закриваючої дужки `)` і з'єднує їх у ланцюжок cons-пар.
- Зустрілася одинарна лапка `'` — парсер перетворює цукор `'x` на еквівалентний S-вираз `(quote x)`.
- Зустрілася послідовність символів — якщо вона складається з цифр, вона перетворюється на число (`VAL_NUM`), інакше реєструється як символ (`VAL_SYM`).

## Повний вихідний код інтерпретатора

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <variant>
#include <unordered_map>
#include <sstream>

struct Value;
using ValuePtr = std::shared_ptr<Value>;
struct Env;
using EnvPtr = std::shared_ptr<Env>;

using PrimFn = ValuePtr(*)(const std::vector<ValuePtr>&, EnvPtr);

struct Nil {};
struct Pair { ValuePtr car; ValuePtr cdr; };
struct Closure {
    std::vector<std::string> params;
    std::vector<ValuePtr> body;
    EnvPtr env;
};

struct Value {
    std::variant<Nil, long, std::string, Pair, PrimFn, Closure> data;

    bool is_nil() const { return std::holds_alternative<Nil>(data); }
    bool is_num() const { return std::holds_alternative<long>(data); }
    bool is_sym() const { return std::holds_alternative<std::string>(data); }
    bool is_pair() const { return std::holds_alternative<Pair>(data); }
};

ValuePtr make_nil() { return std::make_shared<Value>(Value{Nil{}}); }
ValuePtr make_num(long n) { return std::make_shared<Value>(Value{n}); }
ValuePtr make_sym(std::string s) { return std::make_shared<Value>(Value{std::move(s)}); }
ValuePtr make_pair(ValuePtr car, ValuePtr cdr) { return std::make_shared<Value>(Value{Pair{std::move(car), std::move(cdr)}}); }

struct Env : std::enable_shared_from_this<Env> {
    std::unordered_map<std::string, ValuePtr> bindings;
    EnvPtr parent;

    Env(EnvPtr p = nullptr) : parent(std::move(p)) {}

    ValuePtr get(const std::string& name) const {
        auto it = bindings.find(name);
        if (it != bindings.end()) return it->second;
        if (parent) return parent->get(name);
        throw std::runtime_error("Невідома змінна: " + name);
    }

    void set(const std::string& name, ValuePtr val) {
        bindings[name] = std::move(val);
    }
};

/* Токенізатор та парсер */
std::vector<std::string> tokenize(const std::string& input) {
    std::vector<std::string> tokens;
    std::string cur;
    for (size_t i = 0; i < input.size(); ++i) {
        char ch = input[i];
        if (std::isspace(ch)) continue;
        if (ch == ';') {
            while (i < input.size() && input[i] != '\n') ++i;
            continue;
        }
        if (ch == '(' || ch == ')' || ch == '\'') {
            tokens.push_back(std::string(1, ch));
        } else {
            cur.clear();
            while (i < input.size() && !std::isspace(input[i]) &&
                   input[i] != '(' && input[i] != ')' && input[i] != ';') {
                cur += input[i++];
            }
            --i;
            tokens.push_back(cur);
        }
    }
    return tokens;
}

ValuePtr parse_tokens(const std::vector<std::string>& tokens, size_t& pos) {
    if (pos >= tokens.size()) return make_nil();
    const auto& tok = tokens[pos++];
    if (tok == "(") {
        std::vector<ValuePtr> list;
        while (pos < tokens.size() && tokens[pos] != ")") {
            list.push_back(parse_tokens(tokens, pos));
        }
        if (pos < tokens.size() && tokens[pos] == ")") ++pos;
        ValuePtr tail = make_nil();
        for (auto it = list.rbegin(); it != list.rend(); ++it) {
            tail = make_pair(*it, tail);
        }
        return tail;
    }
    if (tok == "'") {
        return make_pair(make_sym("quote"), make_pair(parse_tokens(tokens, pos), make_nil()));
    }
    try {
        size_t idx = 0;
        long num = std::stol(tok, &idx);
        if (idx == tok.size()) return make_num(num);
    } catch (...) {}
    return make_sym(tok);
}

/* Обчислення: eval та apply */
ValuePtr eval(ValuePtr exp, EnvPtr env);

std::vector<ValuePtr> pair_to_vec(ValuePtr p) {
    std::vector<ValuePtr> res;
    while (p && p->is_pair()) {
        const auto& pr = std::get<Pair>(p->data);
        res.push_back(pr.car);
        p = pr.cdr;
    }
    return res;
}

ValuePtr apply(ValuePtr fn, const std::vector<ValuePtr>& args, EnvPtr env) {
    if (std::holds_alternative<PrimFn>(fn->data)) {
        return std::get<PrimFn>(fn->data)(args, env);
    }
    if (std::holds_alternative<Closure>(fn->data)) {
        const auto& cl = std::get<Closure>(fn->data);
        auto call_env = std::make_shared<Env>(cl.env);
        for (size_t i = 0; i < cl.params.size() && i < args.size(); ++i) {
            call_env->set(cl.params[i], args[i]);
        }
        ValuePtr res = make_nil();
        for (const auto& b : cl.body) {
            res = eval(b, call_env);
        }
        return res;
    }
    throw std::runtime_error("Спроба виклику не-функціонального значення");
}

ValuePtr eval(ValuePtr exp, EnvPtr env) {
    if (exp->is_nil() || exp->is_num()) return exp;
    if (exp->is_sym()) return env->get(std::get<std::string>(exp->data));

    if (exp->is_pair()) {
        auto elements = pair_to_vec(exp);
        if (elements.empty()) return exp;

        auto op = elements[0];
        if (op->is_sym()) {
            const auto& sym = std::get<std::string>(op->data);
            if (sym == "quote") return elements.at(1);
            if (sym == "if") {
                auto cond = eval(elements.at(1), env);
                bool truthy = !cond->is_nil() && (!cond->is_num() || std::get<long>(cond->data) != 0);
                return truthy ? eval(elements.at(2), env) : (elements.size() > 3 ? eval(elements.at(3), env) : make_nil());
            }
            if (sym == "define") {
                auto val = eval(elements.at(2), env);
                env->set(std::get<std::string>(elements.at(1)->data), val);
                return val;
            }
            if (sym == "lambda") {
                auto param_nodes = pair_to_vec(elements.at(1));
                std::vector<std::string> params;
                for (const auto& p : param_nodes) params.push_back(std::get<std::string>(p->data));
                std::vector<ValuePtr> body(elements.begin() + 2, elements.end());
                return std::make_shared<Value>(Value{Closure{std::move(params), std::move(body), env}});
            }
        }

        auto fn = eval(op, env);
        std::vector<ValuePtr> evaled_args;
        for (size_t i = 1; i < elements.size(); ++i) {
            evaled_args.push_back(eval(elements[i], env));
        }
        return apply(fn, evaled_args, env);
    }
    return exp;
}
```
:::

## Покроковий розбір виконання виразу

Розгляньмо, як саме інтерпретатор обробляє зв'язування та наступне виконання функції обчислення квадрата числа:

```lisp
(define sqr (lambda (x) (* x x)))
(sqr 5)
```

1. **Фаза читання (Read):**
   - Рідер отримує перший рядок, розбиває його на потік токенів і формує ієрархію парних комірок: перший вузол списку містить символ `define`, другий — символ `sqr`, а третій — вкладений підсписок `(lambda (x) (* x x))`.

2. **Обчислення спеціальної форми `define`:**
   - Функція `eval` бачить символ `define` на першій позиції списку. Вона не обчислює ім'я `sqr`, а передає його як сирий символ.
   - Другий аргумент `(lambda (x) (* x x))` передається у рекурсивний виклик `eval`.
   - Обробник форми `lambda` не обчислює вираз `(* x x)`. Замість цього він створює екземпляр замикання (`VAL_CLOSURE`), куди пакує список формальних параметрів `(x)`, тіло `((* x x))` та збережений покажчик на глобальне оточення `env`.
   - Функція `env_set` створює нову пару в глобальному оточенні, пов'язуючи ім'я `"sqr"` зі створеним замиканням.

3. **Обчислення виклику `(sqr 5)`:**
   - `eval` аналізує список виклику. Перший елемент `sqr` не є спеціальною формою, тому інтерпретатор переходить до стандартного обчислення оператора та аргументів.
   - `eval(sqr, env)` знаходить у глобальній таблиці змінних замикання функції `sqr`.
   - `eval(5, env)` повертає числове значення `5`.
   - Інтерпретатор передає замикання та список аргументів `(5)` у функцію `apply`.

4. **Застосування функції (Apply) та повернення результату:**
   - Функція `apply` бачить тип `VAL_CLOSURE`. Вона виділяє новий фрейм оточення `call_env`, батьківським для якого призначається `closure->env`.
   - У новому фреймі формальний параметр `x` зв'язується з фактичним значенням `5`.
   - Інтерпретатор послідовно викликає `eval` для виразів тіла функції у створеному оточенні `call_env`.
   - Під час обчислення `(* x x)` символ `*` резолвиться у системний примітив `prim_mul`, а обидва входження `x` знаходять значення `5` у найближчому фреймі.
   - Множення `5 · 5` повертає числове значення `25`, яке виводиться користувачеві в терміналі.

## Керування пам'яттю та виклики без збирача сміття

У наведеній демонстраційній реалізації мовою C для кожної cons-комірки, символу та фрейму оточення викликається системний `malloc`. Оскільки в іграшковому прикладі немає збирача сміття, кожна операція в REPL створює нові витоки пам'яті. 

У повноцінному Lisp ручне вивільнення пам'яті за допомогою `free` неможливе через наявність спільних підструктур: один і той самий список може одночасно бути хвостом іншого списку, тілом кількох різних замикань і значенням у глобальній змінній. Саме тому інтеграція збирача сміття (Mark-and-Sweep або копіюючого GC) є обов'язковою складовою будь-якого промислового середовища виконання Lisp.
