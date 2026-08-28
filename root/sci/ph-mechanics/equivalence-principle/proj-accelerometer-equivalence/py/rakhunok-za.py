import math

g = 9.81                              # тут g — величина поля; напрямок задаємо вектором

def rot(v, ang):
    """Повернути 2D-вектор на кут ang (рад)."""
    c, s = math.cos(ang), math.sin(ang)
    x, z = v
    return (c*x - s*z, s*x + c*z)

def reading_body(tilt, a_world):
    """Показ акселерометра у ВЛАСНИХ осях: f = a − g, повернуте у тіло.
    tilt — справжній нахил давача (рад); a_world — справжнє прискорення у світі."""
    g_world = (0.0, -g)
    f_world = (a_world[0] - g_world[0], a_world[1] - g_world[1])
    return rot(f_world, -tilt)        # світ → тіло: поворот на −tilt

def recover_accel(f_body, tilt_hat):
    """Відновити прискорення у світі з показу, знаючи ОЦІНКУ орієнтації."""
    fw = rot(f_body, tilt_hat)        # тіло → світ за оцінкою
    return (fw[0], fw[1] - g)         # додати поле назад: a = f + g_world
