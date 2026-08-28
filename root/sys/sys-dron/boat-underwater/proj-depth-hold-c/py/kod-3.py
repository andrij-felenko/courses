# --- Склеювання: один такт режиму Depth Hold ---
g_ds = None
g_pid = None
g_target_depth = 2.0   # задана глибина, м


def depth_hold_setup():
    global g_ds, g_pid
    # морська вода; α=0.25 — помірне згладжування; τ_d=0.08 c
    g_ds = DepthSensor(1025.0, 9.81, 0.25)
    # kp,ki,kd підбирають під апарат; межі тяги −1..+1;
    # інтеграл обмежуємо так, щоб він міг дати щонайбільше ~половину тяги
    g_pid = DepthPID(4.0, 1.2, 2.5, 0.08,
                     -0.5, 0.5, -1.0, 1.0)


def depth_hold_arm(p_abs_now):
    """Викликати на поверхні перед зануренням."""
    g_ds.tare(p_abs_now)
    g_pid.reset(0.0)


def depth_hold_step(dt):
    """Гарячий такт: dt — фактичний крок, с; read_pressure_pa() — ваш давач."""
    p_abs = read_pressure_pa()                    # сирий тиск, Па
    depth = g_ds.depth_from_pressure(p_abs)       # → згладжена глибина
    u = g_pid.step(g_target_depth, depth, dt)
    return u   # → на вертикальні рушії через мікшер
