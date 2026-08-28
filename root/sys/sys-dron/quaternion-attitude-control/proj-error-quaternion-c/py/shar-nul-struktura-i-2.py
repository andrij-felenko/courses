import math

# повернути кватерніон на одиничну сферу: q ← q / |q|
def quat_normalize(q: Quat) -> None:
    n2 = q.w*q.w + q.x*q.x + q.y*q.y + q.z*q.z
    # захист від ділення на нуль (виродження — майже неможливе, але дешеве)
    if n2 < 1e-12:
        q.w, q.x, q.y, q.z = QUAT_IDENTITY.w, QUAT_IDENTITY.x, QUAT_IDENTITY.y, QUAT_IDENTITY.z
        return
    inv = 1.0 / math.sqrt(n2)
    q.w *= inv; q.x *= inv; q.y *= inv; q.z *= inv
