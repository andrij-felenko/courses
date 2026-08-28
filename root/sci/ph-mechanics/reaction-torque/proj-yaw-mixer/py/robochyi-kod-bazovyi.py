# Один рядок матриці змішувача: внесок мотора в кожен канал.
# (throttle, roll, pitch, yaw) — коефіцієнти:
#   throttle завжди +1: спільний газ
#   roll  ±1: лівий/правий бік рами
#   pitch ±1: передній/задній бік рами
#   yaw   +1 для CCW-гвинта, −1 для CW-гвинта

# X-рама, 4 мотори. Порядок m1..m4 — як у таблиці вище.
#      throttle  roll  pitch  yaw
MIX = (
    (+1.0, -1.0, +1.0, +1.0),  # m1: зад-право,  CCW
    (+1.0, -1.0, -1.0, -1.0),  # m2: перед-право, CW
    (+1.0, +1.0, +1.0, -1.0),  # m3: зад-ліво,   CW
    (+1.0, +1.0, -1.0, +1.0),  # m4: перед-ліво,  CCW
)


# Вхід: команди від регулятора орієнтації, кожна вже масштабована в частку.
# throttle ∈ [0..1]; roll/pitch/yaw ∈ [−1..+1] (нуль = без моменту).
def mix_naive(throttle, roll, pitch, yaw):
    motor = [0.0] * 4
    for i, (kt, kr, kp, ky) in enumerate(MIX):
        motor[i] = (kt * throttle
                    + kr * roll
                    + kp * pitch
                    + ky * yaw)
    return motor
