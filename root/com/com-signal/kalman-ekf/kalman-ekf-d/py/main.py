# скалярний EKF-такт із нелінійним виміром z = h/cos(theta)
import math

R = 0.25                                  # шум далекоміра, м²
theta = math.radians(30.0)

class RangeEKF:
    def __init__(self):
        self.h = 40.0                     # оцінка висоти
        self.P = 4.0                      # її дисперсія

    def range_update(self, z_meas):
        c = math.cos(theta)
        H = 1.0 / c                       # якобіан виміру в точці оцінки
        z_hat = self.h / c                # очікуваний вимір — через ТОЧНУ модель
        S = H * self.P * H + R            # невпевненість інновації
        K = self.P * H / S                # підсилення Калмана
        self.h += K * (z_meas - z_hat)    # корекція стану
        self.P = (1.0 - K * H) * self.P   # невпевненість падає
