from itertools import count

# терм: змінна, абстракція (λ), застосування
class Var:
    def __init__(s, name): s.name = name
class Lam:
    def __init__(s, param, body): s.param, s.body = param, body
class App:
    def __init__(s, fn, arg): s.fn, s.arg = fn, arg

def free(t):                       # вільні (незв'язані) змінні терма
    if isinstance(t, Var): return {t.name}
    if isinstance(t, Lam): return free(t.body) - {t.param}
    return free(t.fn) | free(t.arg)

_n = count()
def fresh(base): return f"{base}#{next(_n)}"

def subst(t, x, s):                # t[x := s], без захоплення змінних
    if isinstance(t, Var):
        return s if t.name == x else t
    if isinstance(t, App):
        return App(subst(t.fn, x, s), subst(t.arg, x, s))
    if t.param == x:               # x перекрито цією λ — далі не чіпаємо
        return t
    if t.param in free(s):         # підстановка спіймала б вільну змінну —
        p = fresh(t.param)         # перейменовуємо зв'язану, щоб не захопити
        body = subst(t.body, t.param, Var(p))
        return Lam(p, subst(body, x, s))
    return Lam(t.param, subst(t.body, x, s))

def step(t):                       # один крок нормального порядку (лівий-зовнішній)
    if isinstance(t, App):
        if isinstance(t.fn, Lam):                   # ось він, зовнішній редекс
            return subst(t.fn.body, t.fn.param, t.arg)
        f = step(t.fn)
        if f is not None: return App(f, t.arg)
        a = step(t.arg)
        if a is not None: return App(t.fn, a)
        return None
    if isinstance(t, Lam):
        b = step(t.body)
        return Lam(t.param, b) if b is not None else None
    return None                                     # Var — нема куди редукувати

def normalize(t, limit=100_000):
    for _ in range(limit):
        nt = step(t)
        if nt is None: return t                     # нормальна форма
        t = nt
    raise RuntimeError("нормальної форми не видно — можливо, її й немає")

# число Черча n = λf.λx. f (f (… x …))  — рівно n застосувань f
def church(n):
    body = Var("x")
    for _ in range(n): body = App(Var("f"), body)
    return Lam("f", Lam("x", body))

add = Lam("a", Lam("b", Lam("f", Lam("x",
        App(App(Var("a"), Var("f")),
            App(App(Var("b"), Var("f")), Var("x")))))))

def to_int(t):                     # нормалізуй і полічи застосування f
    t = normalize(t)
    f, inner = t.param, t.body
    x, cur, n = inner.param, inner.body, 0
    while isinstance(cur, App) and cur.fn.name == f:
        n, cur = n + 1, cur.arg
    return n

print(to_int(App(App(add, church(2)), church(3))))   # 5
