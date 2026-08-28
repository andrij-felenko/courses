import socket
import json
import math
import random
import time

class SensorNoiseModel:
    def __init__(self, std_noise: float, std_bias: float, tau_s: float):
        self.std_noise = std_noise
        self.std_bias = std_bias
        self.tau = tau_s
        self.bias = 0.0

    def update(self, true_val: float, dt: float) -> float:
        # Дискретний процес випадкового блукання першого порядку Гаусса-Маркова
        drift = self.std_bias * math.sqrt(2.0 * dt / self.tau) * random.gauss(0.0, 1.0)
        self.bias = (1.0 - dt / self.tau) * self.bias + drift
        white_noise = random.gauss(0.0, self.std_noise)
        return true_val + self.bias + white_noise

def run_sitl_bridge():
    print("[Python SITL Bridge] Слухаємо 127.0.0.1:9003, відправляємо в 9002...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 9003))
    target_addr = ("127.0.0.1", 9002)

    accel_noise_x = SensorNoiseModel(0.08, 0.005, 300.0)
    accel_noise_y = SensorNoiseModel(0.08, 0.005, 300.0)
    accel_noise_z = SensorNoiseModel(0.08, 0.005, 300.0)
    
    gyro_noise_x = SensorNoiseModel(0.003, 0.0002, 200.0)
    gyro_noise_y = SensorNoiseModel(0.003, 0.0002, 200.0)
    gyro_noise_z = SensorNoiseModel(0.003, 0.0002, 200.0)

    baro_noise = SensorNoiseModel(0.4, 0.05, 600.0)

    dt = 0.0025 # 400 Гц
    timestamp = 0.0
    alt_m = 0.0

    while True:
        data, _ = sock.recvfrom(2048)
        if not data:
            continue

        timestamp += dt
        
        # Генерація показників акселерометра з урахуванням реакції опори (+1g вгору)
        meas_ax = accel_noise_x.update(0.0, dt)
        meas_ay = accel_noise_y.update(0.0, dt)
        meas_az = accel_noise_z.update(-9.80665, dt)

        meas_gx = gyro_noise_x.update(0.0, dt)
        meas_gy = gyro_noise_y.update(0.0, dt)
        meas_gz = gyro_noise_z.update(0.0, dt)

        # Атмосферний тиск за поточною висотою польоту
        true_pressure = 101325.0 * (1.0 - 0.0065 * alt_m / 288.15) ** 5.255
        meas_pressure = baro_noise.update(true_pressure, dt)

        packet = {
            "timestamp": timestamp,
            "imu": {
                "gyro": [meas_gx, meas_gy, meas_gz],
                "accel_body": [meas_ax, meas_ay, meas_az]
            },
            "baro": {
                "pressure_pa": meas_pressure
            },
            "position": [0.0, 0.0, -alt_m]
        }

        sock.sendto(json.dumps(packet).encode('utf-8'), target_addr)

if __name__ == "__main__":
    run_sitl_bridge()
