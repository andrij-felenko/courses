# N-фазний зсув: один такт ділимо на N рівних інтервалів.
# TIMER_TOP — значення лічильника за повний такт (=1/f).
N_PHASES = 4
TIMER_TOP = 1000   # тактів таймера на один період комутації

def phase_start(i):
    """Поріг старту фази i: рівномірний зсув на 360°/N."""
    # i-та фаза починає свій такт на (i * TIMER_TOP / N)
    return i * TIMER_TOP // N_PHASES

def setup_phase_offsets():
    for i in range(N_PHASES):
        # кожній фазі — власний зсув фази ШІМ у її таймері/каналі
        pwm_set_phase(i, phase_start(i))   # 0, 250, 500, 750 тактів
