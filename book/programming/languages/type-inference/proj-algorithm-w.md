# ⚙️ Реалізація рушія виведення типів Hindley — Milner (Алгоритм W)

Алгоритм виведення типів Hindley — Milner (зокрема його класична синтаксично керована форма — алгоритм W) часто сприймається як теоретична абстракція, доки його не реалізовано у вигляді конкретного інтерпретатора. Проте за його строгими математичними формулами стоїть надзвичайно компактний і логічний механізм: обхід абстрактного синтаксичного дерева (AST), генерація свіжих змінних типів, накопичення глобальної підстановки та розв'язання рівнянь методом уніфікації на кожному кроці.

Нижче наведено робочу реалізацію повнофункціонального типізатора для розширеного лямбда-числення. Рушій підтримує базові числові та булеві типи, лямбда-абстракції, виклики функцій та поліморфне зв'язування `let` (ранг-1 поліморфізм).

## 1. Архітектура компонентів типізатора

Рушій виведення складається з п'яти взаємопов'язаних шарів:

1. **Модель типів (`Type`):**
   - Примітивні типи (`Int`, `Bool`).
   - Змінні типів (`TypeVar` із числовим індексом: `t0`, `t1`, `t2`...).
   - Функціональні стрілки (`ArrowType`: `From -> To`).
2. **Підстановки (`Subst`) та композиція:**
   - Словник відображень `var_id ↦ Type`. Композиція підстановок `s2 ∘ s1` дозволяє послідовно уточнювати типи виразів у процесі аналізу AST.
3. **Схеми типів (`Scheme`) та контекст оточення (`TypeEnv`):**
   - Поліморфна схема `∀α₁ α₂ ... αₙ. τ`, яка фіксує квантифіковані змінні типу.
   - Оточення `TypeEnv` зв'язує імена змінних у вихідному коді з їхніми схемами.
4. **Уніфікатор Робінсона (`unify`):**
   - Структурне зіставлення двох типів з обов'язковою перевіркою циклічності (`occurs-check`).
5. **Алгоритм W (`infer_w`):**
   - Головна рекурсивна функція `infer_w(env, expr) -> (Subst, Type)`, що приймає синтаксичний вузол і повертає накопичену підстановку та виведений тип.

## 2. Програмна реалізація мовами C++ та Python

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <map>
#include <set>
#include <stdexcept>
#include <sstream>
#include <algorithm>

// ── 1. Модель типів ──────────────────────────────────────────────────────────

enum class PrimKind { Int, Bool };

struct Type;
using TypePtr = std::shared_ptr<Type>;

struct Type {
    enum class Kind { Prim, Var, Arrow } kind;
    PrimKind prim;
    int var_id = -1;
    TypePtr from = nullptr;
    TypePtr to = nullptr;

    static TypePtr make_prim(PrimKind p) {
        auto t = std::make_shared<Type>();
        t->kind = Kind::Prim;
        t->prim = p;
        return t;
    }

    static TypePtr make_var(int id) {
        auto t = std::make_shared<Type>();
        t->kind = Kind::Var;
        t->var_id = id;
        return t;
    }

    static TypePtr make_arrow(TypePtr f, TypePtr to_type) {
        auto t = std::make_shared<Type>();
        t->kind = Kind::Arrow;
        t->from = f;
        t->to = to_type;
        return t;
    }

    std::string to_string() const {
        if (kind == Kind::Prim) {
            return (prim == PrimKind::Int) ? "Int" : "Bool";
        }
        if (kind == Kind::Var) {
            return "t" + std::to_string(var_id);
        }
        if (kind == Kind::Arrow) {
            std::string l = (from->kind == Kind::Arrow) ? "(" + from->to_string() + ")" : from->to_string();
            return l + " -> " + to->to_string();
        }
        return "?";
    }
};

// ── 2. Підстановки (Substitutions) ────────────────────────────────────────────

using Subst = std::map<int, TypePtr>;

TypePtr apply_subst(const Subst& s, TypePtr t) {
    if (!t) return nullptr;
    if (t->kind == Kind::Prim) return t;
    if (t->kind == Kind::Var) {
        auto it = s.find(t->var_id);
        if (it != s.end()) {
            return apply_subst(s, it->second);
        }
        return t;
    }
    if (t->kind == Kind::Arrow) {
        return Type::make_arrow(apply_subst(s, t->from), apply_subst(s, t->to));
    }
    return t;
}

// Композиція: (s2 ∘ s1)(t) = s2(s1(t))
Subst compose_subst(const Subst& s2, const Subst& s1) {
    Subst res;
    for (const auto& [var, type] : s1) {
        res[var] = apply_subst(s2, type);
    }
    for (const auto& [var, type] : s2) {
        if (res.find(var) == res.end()) {
            res[var] = type;
        }
    }
    return res;
}

std::set<int> free_type_vars(TypePtr t) {
    if (!t || t->kind == Kind::Prim) return {};
    if (t->kind == Kind::Var) return { t->var_id };
    if (t->kind == Kind::Arrow) {
        auto l = free_type_vars(t->from);
        auto r = free_type_vars(t->to);
        l.insert(r.begin(), r.end());
        return l;
    }
    return {};
}

// ── 3. Схеми типів (Scheme) та Оточення (Env) ─────────────────────────────────

struct Scheme {
    std::set<int> quantified_vars;
    TypePtr type;
};

using TypeEnv = std::map<std::string, Scheme>;

std::set<int> free_type_vars_env(const TypeEnv& env) {
    std::set<int> ftv;
    for (const auto& [_, sc] : env) {
        auto t_ftv = free_type_vars(sc.type);
        for (int v : sc.quantified_vars) {
            t_ftv.erase(v);
        }
        ftv.insert(t_ftv.begin(), t_ftv.end());
    }
    return ftv;
}

TypeEnv apply_subst_env(const Subst& s, const TypeEnv& env) {
    TypeEnv res;
    for (const auto& [name, sc] : env) {
        Subst s_clean = s;
        for (int q : sc.quantified_vars) {
            s_clean.erase(q);
        }
        res[name] = Scheme{sc.quantified_vars, apply_subst(s_clean, sc.type)};
    }
    return res;
}

// ── 4. Генератор змінних, Узагальнення та Інстанціювання ─────────────────────

int g_var_counter = 0;
TypePtr fresh_var() {
    return Type::make_var(g_var_counter++);
}

// Інстанціювання схеми ∀α. τ у новий конкретний екземпляр
TypePtr instantiate(const Scheme& sc) {
    Subst s;
    for (int q : sc.quantified_vars) {
        s[q] = fresh_var();
    }
    return apply_subst(s, sc.type);
}

// Узагальнення типу в схему: закриваємо квантором всі змінні, яких немає в оточенні
Scheme generalize(const TypeEnv& env, TypePtr t) {
    auto env_ftv = free_type_vars_env(env);
    auto t_ftv = free_type_vars(t);
    std::set<int> quantified;
    for (int v : t_ftv) {
        if (env_ftv.find(v) == env_ftv.end()) {
            quantified.insert(v);
        }
    }
    return Scheme{quantified, t};
}

// ── 5. Уніфікація Робінсона (Unification) ────────────────────────────────────

Subst bind_var(int var_id, TypePtr t) {
    if (t->kind == Kind::Var && t->var_id == var_id) {
        return {};
    }
    auto ftv = free_type_vars(t);
    if (ftv.find(var_id) != ftv.end()) {
        throw std::runtime_error("Occurs-Check Error: нескінченний тип t" + 
                                 std::to_string(var_id) + " = " + t->to_string());
    }
    return { {var_id, t} };
}

Subst unify(TypePtr t1, TypePtr t2) {
    if (t1->kind == Kind::Prim && t2->kind == Kind::Prim) {
        if (t1->prim == t2->prim) return {};
        throw std::runtime_error("Розбіжність типів: " + t1->to_string() + " та " + t2->to_string());
    }
    if (t1->kind == Kind::Var) {
        return bind_var(t1->var_id, t2);
    }
    if (t2->kind == Kind::Var) {
        return bind_var(t2->var_id, t1);
    }
    if (t1->kind == Kind::Arrow && t2->kind == Kind::Arrow) {
        Subst s1 = unify(t1->from, t2->from);
        Subst s2 = unify(apply_subst(s1, t1->to), apply_subst(s1, t2->to));
        return compose_subst(s2, s1);
    }
    throw std::runtime_error("Неможливо уніфікувати: " + t1->to_string() + " та " + t2->to_string());
}

// ── 6. AST Виразів та Алгоритм W ────────────────────────────────────────────

struct Expr;
using ExprPtr = std::shared_ptr<Expr>;

struct Expr {
    enum class Kind { LitInt, LitBool, Var, Lam, App, If, Let } kind;
    int int_val = 0;
    bool bool_val = false;
    std::string name;
    std::string param_name;
    ExprPtr body = nullptr;
    ExprPtr left = nullptr;
    ExprPtr right = nullptr;
    ExprPtr cond = nullptr, then_b = nullptr, else_b = nullptr;
    ExprPtr let_val = nullptr, let_body = nullptr;

    static ExprPtr make_int(int v) {
        auto e = std::make_shared<Expr>(); e->kind = Kind::LitInt; e->int_val = v; return e;
    }
    static ExprPtr make_bool(bool b) {
        auto e = std::make_shared<Expr>(); e->kind = Kind::LitBool; e->bool_val = b; return e;
    }
    static ExprPtr make_var(const std::string& n) {
        auto e = std::make_shared<Expr>(); e->kind = Kind::Var; e->name = n; return e;
    }
    static ExprPtr make_lam(const std::string& p, ExprPtr b) {
        auto e = std::make_shared<Expr>(); e->kind = Kind::Lam; e->param_name = p; e->body = b; return e;
    }
    static ExprPtr make_app(ExprPtr f, ExprPtr arg) {
        auto e = std::make_shared<Expr>(); e->kind = Kind::App; e->left = f; e->right = arg; return e;
    }
    static ExprPtr make_let(const std::string& n, ExprPtr val, ExprPtr b) {
        auto e = std::make_shared<Expr>(); e->kind = Kind::Let; e->name = n; e->let_val = val; e->let_body = b; return e;
    }
};

struct InferResult {
    Subst subst;
    TypePtr type;
};

// Рекурсивна функція W: Γ ⊢ e : τ
InferResult infer_w(const TypeEnv& env, ExprPtr e) {
    if (e->kind == Expr::Kind::LitInt) {
        return { {}, Type::make_prim(PrimKind::Int) };
    }
    if (e->kind == Expr::Kind::LitBool) {
        return { {}, Type::make_prim(PrimKind::Bool) };
    }
    if (e->kind == Expr::Kind::Var) {
        auto it = env.find(e->name);
        if (it == env.end()) {
            throw std::runtime_error("Невідома змінна: " + e->name);
        }
        return { {}, instantiate(it->second) };
    }
    if (e->kind == Expr::Kind::Lam) {
        TypePtr a = fresh_var();
        TypeEnv new_env = env;
        new_env[e->param_name] = Scheme{ {}, a };
        auto [s1, t_body] = infer_w(new_env, e->body);
        return { s1, Type::make_arrow(apply_subst(s1, a), t_body) };
    }
    if (e->kind == Expr::Kind::App) {
        TypePtr out_type = fresh_var();
        auto [s1, t_fn] = infer_w(env, e->left);
        auto [s2, t_arg] = infer_w(apply_subst_env(s1, env), e->right);

        Subst s3 = unify(apply_subst(s2, t_fn), Type::make_arrow(t_arg, out_type));
        Subst s_final = compose_subst(s3, compose_subst(s2, s1));
        return { s_final, apply_subst(s3, out_type) };
    }
    if (e->kind == Expr::Kind::Let) {
        auto [s1, t_val] = infer_w(env, e->let_val);
        TypeEnv env1 = apply_subst_env(s1, env);
        Scheme sc = generalize(env1, t_val);

        TypeEnv new_env = env1;
        new_env[e->name] = sc;

        auto [s2, t_body] = infer_w(new_env, e->let_body);
        return { compose_subst(s2, s1), t_body };
    }
    throw std::runtime_error("Непідтримуваний тип вузла AST");
}

int main() {
    try {
        TypeEnv env;

        // Тест 1: let id = \x -> x in id 42
        auto id_expr = Expr::make_lam("x", Expr::make_var("x"));
        auto test1 = Expr::make_let("id", id_expr, Expr::make_app(Expr::make_var("id"), Expr::make_int(42)));
        
        auto res1 = infer_w(env, test1);
        std::cout << "Тест 1 (let id in id 42) -> " << res1.type->to_string() << "\n";

        // Тест 2: Виведення функції вищого порядку \f -> \x -> f (f x)
        auto twice_expr = Expr::make_lam("f", 
            Expr::make_lam("x", 
                Expr::make_app(Expr::make_var("f"), 
                    Expr::make_app(Expr::make_var("f"), Expr::make_var("x")))));
        
        auto res2 = infer_w(env, twice_expr);
        std::cout << "Тест 2 (twice / \\f -> \\x -> f (f x)) -> " << res2.type->to_string() << "\n";

        // Тест 3: Перевірка Occurs-Check: \x -> x x (повинна викликати помилку)
        std::cout << "Тест 3 (\\x -> x x) -> очікуємо помилку Occurs-Check...\n";
        auto self_app = Expr::make_lam("x", Expr::make_app(Expr::make_var("x"), Expr::make_var("x")));
        try {
            infer_w(env, self_app);
            std::cout << "Помилка: тип виведено помилково!\n";
        } catch (const std::exception& ex) {
            std::cout << "Успішно перехоплено: " << ex.what() << "\n";
        }

    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }
    return 0;
}
```
```py
from dataclasses import dataclass
from typing import Dict, Set, Optional, Tuple, Union

# ── 1. Модель типів ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PrimType:
    name: str  # "Int" або "Bool"
    def __str__(self): return self.name

@dataclass(frozen=True)
class TypeVar:
    id: int
    def __str__(self): return f"t{self.id}"

@dataclass(frozen=True)
class ArrowType:
    from_t: 'Type'
    to_t: 'Type'
    def __str__(self):
        l = f"({self.from_t})" if isinstance(self.from_t, ArrowType) else str(self.from_t)
        return f"{l} -> {self.to_t}"

Type = Union[PrimType, TypeVar, ArrowType]

# ── 2. Підстановки (Substitutions) ────────────────────────────────────────────

Subst = Dict[int, Type]

def apply_subst(s: Subst, t: Type) -> Type:
    if isinstance(t, PrimType):
        return t
    if isinstance(t, TypeVar):
        return apply_subst(s, s[t.id]) if t.id in s else t
    if isinstance(t, ArrowType):
        return ArrowType(apply_subst(s, t.from_t), apply_subst(s, t.to_t))
    return t

def compose_subst(s2: Subst, s1: Subst) -> Subst:
    res = {v: apply_subst(s2, t) for v, t in s1.items()}
    res.update({v: t for v, t in s2.items() if v not in res})
    return res

def free_type_vars(t: Type) -> Set[int]:
    if isinstance(t, PrimType): return set()
    if isinstance(t, TypeVar): return {t.id}
    if isinstance(t, ArrowType): return free_type_vars(t.from_t) | free_type_vars(t.to_t)
    return set()

# ── 3. Схеми та Оточення ─────────────────────────────────────────────────────

@dataclass
class Scheme:
    quantified: Set[int]
    type: Type

TypeEnv = Dict[str, Scheme]

def free_type_vars_env(env: TypeEnv) -> Set[int]:
    ftv = set()
    for sc in env.values():
        ftv |= (free_type_vars(sc.type) - sc.quantified)
    return ftv

def apply_subst_env(s: Subst, env: TypeEnv) -> TypeEnv:
    return {name: Scheme(sc.quantified, apply_subst({k: v for k, v in s.items() if k not in sc.quantified}, sc.type))
            for name, sc in env.items()}

# ── 4. Генератор змінних, Узагальнення та Інстанціювання ─────────────────────

_counter = 0
def fresh_var() -> TypeVar:
    global _counter
    v = TypeVar(_counter)
    _counter += 1
    return v

def instantiate(sc: Scheme) -> Type:
    s = {q: fresh_var() for q in sc.quantified}
    return apply_subst(s, sc.type)

def generalize(env: TypeEnv, t: Type) -> Scheme:
    quantified = free_type_vars(t) - free_type_vars_env(env)
    return Scheme(quantified, t)

# ── 5. Уніфікація Робінсона ──────────────────────────────────────────────────

def bind_var(var_id: int, t: Type) -> Subst:
    if isinstance(t, TypeVar) and t.id == var_id:
        return {}
    if var_id in free_type_vars(t):
        raise TypeError(f"Occurs-Check Error: нескінченний тип t{var_id} = {t}")
    return {var_id: t}

def unify(t1: Type, t2: Type) -> Subst:
    if isinstance(t1, PrimType) and isinstance(t2, PrimType):
        if t1.name == t2.name: return {}
        raise TypeError(f"Розбіжність типів: {t1} та {t2}")
    if isinstance(t1, TypeVar):
        return bind_var(t1.id, t2)
    if isinstance(t2, TypeVar):
        return bind_var(t2.id, t1)
    if isinstance(t1, ArrowType) and isinstance(t2, ArrowType):
        s1 = unify(t1.from_t, t2.from_t)
        s2 = unify(apply_subst(s1, t1.to_t), apply_subst(s1, t2.to_t))
        return compose_subst(s2, s1)
    raise TypeError(f"Неможливо уніфікувати: {t1} та {t2}")

# ── 6. AST та Алгоритм W ─────────────────────────────────────────────────────

@dataclass
class LitInt: val: int
@dataclass
class LitBool: val: bool
@dataclass
class Var: name: str
@dataclass
class Lam: param: str; body: any
@dataclass
class App: fn: any; arg: any
@dataclass
class Let: name: str; val: any; body: any

Expr = Union[LitInt, LitBool, Var, Lam, App, Let]

def infer_w(env: TypeEnv, e: Expr) -> Tuple[Subst, Type]:
    if isinstance(e, LitInt):
        return {}, PrimType("Int")
    if isinstance(e, LitBool):
        return {}, PrimType("Bool")
    if isinstance(e, Var):
        if e.name not in env:
            raise KeyError(f"Невідома змінна: {e.name}")
        return {}, instantiate(env[e.name])
    if isinstance(e, Lam):
        a = fresh_var()
        new_env = dict(env)
        new_env[e.param] = Scheme(set(), a)
        s1, t_body = infer_w(new_env, e.body)
        return s1, ArrowType(apply_subst(s1, a), t_body)
    if isinstance(e, App):
        out_type = fresh_var()
        s1, t_fn = infer_w(env, e.fn)
        s2, t_arg = infer_w(apply_subst_env(s1, env), e.arg)
        s3 = unify(apply_subst(s2, t_fn), ArrowType(t_arg, out_type))
        s_final = compose_subst(s3, compose_subst(s2, s1))
        return s_final, apply_subst(s3, out_type)
    if isinstance(e, Let):
        s1, t_val = infer_w(env, e.val)
        env1 = apply_subst_env(s1, env)
        sc = generalize(env1, t_val)
        new_env = dict(env1)
        new_env[e.name] = sc
        s2, t_body = infer_w(new_env, e.body)
        return compose_subst(s2, s1), t_body
    raise TypeError(f"Невідомий вираз: {e}")

if __name__ == "__main__":
    env: TypeEnv = {}
    test1 = Let("id", Lam("x", Var("x")), App(Var("id"), LitInt(42)))
    _, t1 = infer_w(env, test1)
    print("Тест 1 (let id in id 42) ->", t1)

    twice = Lam("f", Lam("x", App(Var("f"), App(Var("f"), Var("x")))))
    _, t2 = infer_w(env, twice)
    print("Тест 2 (twice) ->", t2)

    self_app = Lam("x", App(Var("x"), Var("x")))
    try:
        infer_w(env, self_app)
    except TypeError as e:
        print("Тест 3 (self_app) перехоплено:", e)
```
:::

## 3. Детальний аналіз інженерних пасток

Під час реалізації алгоритму W розробники найчастіше припускаються трьох критичних помилок:

### Пастка 1: Злиття словників замість композиції підстановок

Поширена помилка — об'єднувати дві підстановки простим копіюванням пар ключ-значення (`map.insert` або Python `dict.update`). Це грубо порушує інваріант транзитивності.

Якщо `s1 = { 0: t1 }` (змінна 0 замінюється на змінну 1), а наступний крок знаходить `s2 = { 1: Int }` (змінна 1 замінюється на Int), просте злиття дасть `{ 0: t1, 1: Int }`. Якщо тепер застосувати цю підстановку до типу `t0`, отримаємо `t1`, а не `Int`!

Правильна композиція `s2 ∘ s1` зобов'язана попередньо застосувати `s2` до всіх значень `s1`, отримуючи точний результат: `{ 0: Int, 1: Int }`.

### Пастка 2: Пропуск оновлення оточення між лівою та правою гілками виклику

У виразі застосування функції `App(fn, arg)` аналіз лівої гілки `fn` повертає підстановку `s1`. Під час переходу до аналізу аргументу `arg` необхідно передавати не вихідне оточення `env`, а обов'язково оновлене оточення `apply_subst_env(s1, env)`.

Якщо цього не зробити, змінні, які отримали конкретні типи в тілі `fn`, залишаться вільними під час аналізу `arg`, що призведе до створення конфліктуючих паралельних змінних типів і хибних помилок типізації.

Аналогічно, перед уніфікацією результату `s3 = unify(apply_subst(s2, t_fn), ArrowType(t_arg, out_type))` необхідно обов'язково застосувати підстановку `s2` до типу `t_fn`, оскільки виведення типу аргументу `arg` могло уточнити поліморфні змінні самої функції.

### Пастка 3: Передчасне узагальнення змінних оточення (Unsound Generalization)

Функція `generalize(env, t)` вираховує вільні змінні типу `t` і закриває їх квантором `∀`. Проте квантифікувати дозволено **лише ті змінні, які не входять до вільного контексту оточення** `free_type_vars_env(env)`.

Якщо цей фільтр пропустити й узагальнити змінну, зв'язану зовнішньою лямбдою `\x -> let y = x in ...`, змінна `x` помилково стане поліморфною всередині локального блоку. Це дозволить використовувати `x` одночасно як ціле число та рядок тексту, повністю зруйнувавши статичну безпеку типізатора (*unsoundness*).

## 4. Обробка рекурсії (`let rec`) та розгалужень (`if-then-else`)

У практичних мовах програмування лямбда-числення розширюється конструкціями розгалуження та рекурсії:

### Типізація виразу `If(cond, then_branch, else_branch)`

Правило виведення для умовного виразу вимагає двох послідовних уніфікацій:
1. Тип умови `t_cond` повинен уніфікуватися з примітивним типом `Bool`: `s_cond = unify(t_cond, Prim(Bool))`.
2. Типи обох гілок повинні бути узгоджені між собою: `s_branches = unify(apply_subst(s_then, t_then), apply_subst(s_else, t_else))`.
3. Результуючий тип виразу `if` є уніфікованим типом будь-якої з гілок після застосування фінальної композиції всіх підстановок.

### Рекурсивні зв'язування (`let rec`)

У стандартній конструкції `let f = e₁ in e₂` вираз `e₁` не бачить імені `f` у своєму оточенні. Якщо функція є рекурсивною (кличе саму себе), компілятор застосовує розширене правило:
1. Створюється свіжа змінна типу `β` для майбутньої функції `f`.
2. Вираз `e₁` типізується в тимчасовому оточенні `env ∪ { f ↦ Scheme({}, β) }`, повертаючи тип `t₁` та підстановку `s₁`.
3. Змінна `β` уніфікується з отриманим типом: `s₂ = unify(apply_subst(s₁, β), t₁)`.
4. Отриманий результуючий тип узагальнюється функцією `generalize` у схему і додається в оточення для аналізу тіла `e₂`.

## 5. Інтеграція в конвеєр компіляції

У реальному компіляторі робота типізатора не завершується простим виведенням рядка типу. Отримані підстановки застосовуються назад до кожного вузла AST, перетворюючи безтипове або частково анотоване дерево на **типізоване проміжне представлення** (наприклад, Core у GHC чи Typed AST в OCaml).

Наявність точних статичних типів на кожному вузлі відкриває компілятору можливість виконувати критичні низькорівневі оптимізації:
- **Мономорфізація та розпакування:** заміна універсальних покажчиків прямими машинними регістрами (unboxed primitives), коли параметричний тип виведено як конкретний `Int` чи `Float`.
- **Усунення динамічних перевірок:** компілятор упевнений у коректності типів і генерує прямі машинні інструкції виклику замість важких рантайм-перевірок тегів.

## 6. Покроковий розбір результатів тестів

1. **Тест 1 (`let id = \x -> x in id 42`):**
   - Аналіз `\x -> x` повертає тип `t0 -> t0`.
   - Оскільки `env` порожній, `generalize` створює схему `∀t0. t0 -> t0`.
   - При аналізі `id 42` схема інстанціюється у свіжі змінні `t1 -> t1`.
   - Уніфікація `t1 -> t1` зі стрілкою `Int -> t2` знаходить `t1 = Int, t2 = Int`.
   - Результат: `Int`.

2. **Тест 2 (`\f -> \x -> f (f x)`):**
   - Створюються свіжі змінні: `f : t0`, `x : t1`.
   - Внутрішній виклик `f x` вимагає `t0 = t1 -> t2`.
   - Зовнішній виклик `f (f x)` передає результат типу `t2` знову у функцію `f`. Це генерує друге рівняння уніфікатора: `t0 = t2 -> t3`.
   - Уніфікуючи `t1 -> t2` та `t2 -> t3`, алгоритм знаходить `t1 = t2 = t3`.
   - Результат: `(t3 -> t3) -> t3 -> t3` (класичний числовий комбінатор Черча для двійки).

3. **Тест 3 (`\x -> x x`):**
   - Змінна `x` отримує тип `t0`.
   - Застосування `x` до `x` формує рівняння `t0 = t0 -> t1`.
   - Процедура `bind_var` виявляє входження `0 ∈ free_type_vars(t0 -> t1)` і викидає виняток `Occurs-Check Error`, запобігаючи нескінченному зацикленню.
