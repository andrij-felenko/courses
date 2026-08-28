# Стан трьох ПІД живе МІЖ викликами (накопичений інтеграл і попередній кут).
class PID:
    def __init__(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.integ = 0.0
        self.prev_meas = 0.0

    # Один такт одного ПІД: похибка -> команда осі. dt — фактичний крок (с).
    def step(self, target, meas, dt):
        e = target - meas                              # похибка кута
        self.integ += e * dt                           # I: накопичуємо площу похибки
        self.integ = clamp(self.integ, -I_MAX, I_MAX)  # антивіндап (інакше дикий переліт)
        deriv = -(meas - self.prev_meas) / dt          # D від ВИМІРУ (без ривка на зміні завдання)
        self.prev_meas = meas
        return self.kp * e + self.ki * self.integ + self.kd * deriv  # P + I + D = команда осі


# Три ОКРЕМІ контури — по одному на вісь. Викликати РІВНОМІРНО з таймера.
def attitude_step(meas, target, throttle, dt):
    # 1) три незалежні ПІД: кожен бачить ЛИШЕ свою вісь
    roll  = pid_roll.step(target[0],  meas[0], dt)
    pitch = pid_pitch.step(target[1], meas[1], dt)
    yaw   = pid_yaw.step(target[2],   meas[2], dt)

    # 2) МІКШЕР: три команди + база -> тяга кожного мотора (знаки = геометрія рами)
    motor = [
        throttle - roll - pitch - yaw,   # M1 спереду-справа
        throttle - roll + pitch + yaw,   # M2 ззаду-справа
        throttle + roll + pitch - yaw,   # M3 ззаду-зліва
        throttle + roll - pitch + yaw,   # M4 спереду-зліва
    ]

    # 3) затиск у фізичні межі ESC (мотор не вміє менше 0 чи більше за повну тягу)
    return [clamp(m, MOTOR_MIN, MOTOR_MAX) for m in motor]
