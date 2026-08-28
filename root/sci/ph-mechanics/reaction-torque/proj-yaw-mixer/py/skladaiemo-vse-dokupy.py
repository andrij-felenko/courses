# Повний вихідний тракт: команди осей → газ кожного мотора → ESC.
# Викликається щоцикл керування (типово 1–8 кГц у сучасних FC).
# slew_state — список зі станом обмежувача, живе між викликами.
def motor_output_stage(throttle, roll, pitch, yaw, slew_state, max_step):
    # 1. Змішування з насиченням і пріоритетом осей.
    mixed = mix_saturate(throttle, roll, pitch, yaw)

    # 2. Обмеження наростання — гасимо зайві J·α-ривки.
    limited = slew_limit(mixed, slew_state, max_step)

    # 3. Віддати кожен газ своєму регулятору обертів.
    for i in range(4):
        esc_set_throttle(i, limited[i])   # напр., через DShot
