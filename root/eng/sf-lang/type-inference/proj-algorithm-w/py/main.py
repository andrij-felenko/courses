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
