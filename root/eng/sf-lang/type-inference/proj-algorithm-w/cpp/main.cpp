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
