import numpy as np

G  = 9.81          # м/с²
FF = 1.0           # поріг падіння: ~0.1g, м/с²

def quat_rotate(q, v):               # q = (w,x,y,z), v = (x,y,z)
    w, x, y, z = q
    qv = np.array([x, y, z])
    t  = 2.0 * np.cross(qv, v)
    return v + w * t + np.cross(qv, t)

def quat_conj(q):
    w, x, y, z = q
    return np.array([w, -x, -y, -z])

def gravity_in_body(q):              # світ → корпус = обернений q
    up = np.array([0.0, 0.0, G])
    return quat_rotate(quat_conj(q), up)

def linear_accel(a_b, q):            # чисте прискорення руху в осях корпусу
    return np.asarray(a_b) - gravity_in_body(q)

def is_free_fall(a_b):               # увесь показ майже нульовий
    return np.dot(a_b, a_b) < FF * FF
