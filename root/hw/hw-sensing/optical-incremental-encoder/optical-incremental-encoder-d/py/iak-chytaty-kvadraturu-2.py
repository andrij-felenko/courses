PPR = 1024              # щілин на диску (з паспорта енкодера)
CPR = 4 * PPR           # кроків на оберт після квадратури = 4096

# Поточний кут вала в градусах (0..360), із прив'язкою до мітки Z.
def encoder_angle_deg(position):
    c = position % CPR                  # лишок у межах одного оберту (у Python завжди ≥ 0)
    return (360.0 * c) / CPR            # частка оберту → градуси

# Швидкість в обертах за хвилину за період dt_ms між двома вимірами.
# Викликати періодично; pos_now — знімок position на цей момент.
def encoder_rpm(pos_now, pos_prev, dt_ms):
    dcounts = pos_now - pos_prev        # скільки кроків за dt
    rev = dcounts / CPR                 # у обертах
    return rev * (60000.0 / dt_ms)      # об/хв (60000 мс = 1 хв)
