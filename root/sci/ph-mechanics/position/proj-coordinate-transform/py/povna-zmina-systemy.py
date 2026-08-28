def transpose(M):
    return tuple(zip(*M))          # для повороту обернути = транспонувати (див. нижче)

def add(a, b): return tuple(ai + bi for ai, bi in zip(a, b))
def sub(a, b): return tuple(ai - bi for ai, bi in zip(a, b))

def body_to_world(p_body, R, d):
    """Точку з тіла-носія у світ: СПЕРШУ поворот, ТОДІ трансляція."""
    return add(apply(R, p_body), d)          # p_world = R · p_body + d

def world_to_body(p_world, R, d):
    """Зворотний бік: спершу трансляція назад, тоді зворотний поворот (Rᵀ)."""
    return apply(transpose(R), sub(p_world, d))   # p_body = Rᵀ · (p_world − d)
