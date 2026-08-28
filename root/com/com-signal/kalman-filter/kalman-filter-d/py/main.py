# одновимірний фільтр Калмана: стан theta, дисперсія P (град², град)
Q, R = 7.0, 9.0                          # шум моделі та виміру за такт

class Kalman1D:
    def __init__(self):
        self.theta = 16.0
        self.P = 9.0

    def tick(self, gyro_dps, dt, accel_deg):
        # 1. передбачення: модель штовхає оцінку, невпевненість росте
        self.theta += gyro_dps * dt
        self.P += Q
        # 2. оновлення: посилення зважує два джерела за певністю
        K = self.P / (self.P + R)            # коефіцієнт Калмана, 0..1
        self.theta += K * (accel_deg - self.theta)  # підтягуємо до виміру на частку K
        self.P *= (1.0 - K)                  # невпевненість падає
