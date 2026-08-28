# базові функції
def Z(*_):  return 0                  # нуль-функція: за будь-яких аргументів 0
def S(x):   return x + 1              # наступник — єдиний атом арифметики
def Proj(i):                          # проєкція: i-й з аргументів
    return lambda *a: a[i]

# способи будувати нові функції з наявних
def Comp(f, gs):                      # композиція:  f(g₁(…), …, gₖ(…))
    return lambda *a: f(*(g(*a) for g in gs))

def PrimRec(f, g):                    # примітивна рекурсія по останньому аргументу
    def h(*a):
        *xs, y = a
        if y == 0: return f(*xs)                   # h(xs, 0)   = f(xs)
        return g(*xs, y - 1, h(*xs, y - 1))        # h(xs, y+1) = g(xs, y, h(xs, y))
    return h

def Mu(f):                            # μ: найменше y, за якого f(…, y) = 0
    def m(*a):
        y = 0
        while f(*a, y) != 0: y += 1   # може не спинитися ніколи
        return y
    return m

# add(a, 0) = a ;  add(a, S b) = S(add(a, b))
add = PrimRec(Proj(0), Comp(S, [Proj(2)]))

print(add(2, 3))   # 5
