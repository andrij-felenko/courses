import math

def qmul(a, b):                       # добуток кватерніонів a ⊗ b
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw*bw - ax*bx - ay*by - az*bz,
            aw*bx + ax*bw + ay*bz - az*by,
            aw*by - ax*bz + ay*bw + az*bx,
            aw*bz + ax*by - ay*bx + az*bw)

def qunit(q):                         # повернути до одиничної довжини
    inv = 1.0 / math.sqrt(sum(c*c for c in q))
    return tuple(c*inv for c in q)

def qrot(q, v):                       # повернути вектор тіла у світ
    w, x, y, z = q
    r = qmul(qmul(q, (0.0,) + tuple(v)), (w, -x, -y, -z))
    return (r[1], r[2], r[3])

def quat_delta(rotvec):               # точний приріст із θ = ω·dt
    a = math.sqrt(sum(c*c for c in rotvec))
    if a < 1e-12:                     # мала межа: θ/2 у векторну частину
        return (1.0, 0.5*rotvec[0], 0.5*rotvec[1], 0.5*rotvec[2])
    s = math.sin(a/2) / a
    return (math.cos(a/2), rotvec[0]*s, rotvec[1]*s, rotvec[2]*s)
