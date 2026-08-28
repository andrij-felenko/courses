import cmath
import math
import random

# Нормовані точки сузір'я QPSK з одиничною середньою енергією E_s = 1
INV_SQRT2 = 1.0 / math.sqrt(2.0)
QPSK_CONSTELLATION = [
    complex( INV_SQRT2,  INV_SQRT2),  # Символ 0 (біти 00)
    complex(-INV_SQRT2,  INV_SQRT2),  # Символ 1 (біти 01)
    complex( INV_SQRT2, -INV_SQRT2),  # Символ 2 (біти 10)
    complex(-INV_SQRT2, -INV_SQRT2),  # Символ 3 (біти 11)
]

def hard_slice_qpsk(val: complex) -> complex:
    """Поточкове порогове квантування у найближчу точку сузір'я QPSK."""
    re = INV_SQRT2 if val.real >= 0.0 else -INV_SQRT2
    im = INV_SQRT2 if val.imag >= 0.0 else -INV_SQRT2
    return complex(re, im)

def mat2x2_inv(a: complex, b: complex, c: complex, d: complex):
    """Аналітичне обернення комплексної матриці 2x2: [[a, b], [c, d]]."""
    det = a * d - b * c
    if abs(det) < 1e-12:
        det = complex(1e-12, 0.0)  # Захист від ділення на нуль
    inv_det = 1.0 / det
    return d * inv_det, -b * inv_det, -c * inv_det, a * inv_det

def detect_zf_2x2(H: list, y: list) -> list:
    """Zero-Forcing детектор: x̂ = (Hᴴ·H)⁻¹ · Hᴴ · y."""
    h11, h12 = H[0][0], H[0][1]
    h21, h22 = H[1][0], H[1][1]

    # Обчислення матриці Грама G = Hᴴ · H
    g11 = h11.conjugate() * h11 + h21.conjugate() * h21
    g12 = h11.conjugate() * h12 + h21.conjugate() * h22
    g21 = h12.conjugate() * h11 + h22.conjugate() * h21
    g22 = h12.conjugate() * h12 + h22.conjugate() * h22

    ig11, ig12, ig21, ig22 = mat2x2_inv(g11, g12, g21, g22)

    # Узгоджена просторова фільтрація y_mf = Hᴴ · y
    y1, y2 = y[0], y[1]
    ymf1 = h11.conjugate() * y1 + h21.conjugate() * y2
    ymf2 = h12.conjugate() * y1 + h22.conjugate() * y2

    # Оцінка переданих символів
    x1_est = ig11 * ymf1 + ig12 * ymf2
    x2_est = ig21 * ymf1 + ig22 * ymf2

    return [hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est)]

def detect_mmse_2x2(H: list, y: list, snr_lin: float) -> list:
    """Linear MMSE детектор: x̂ = (Hᴴ·H + (1/SNR)·I)⁻¹ · Hᴴ · y."""
    h11, h12 = H[0][0], H[0][1]
    h21, h22 = H[1][0], H[1][1]

    alpha = 1.0 / max(snr_lin, 1e-4)

    # Регуляризована матриця (Hᴴ·H + α·I)
    g11 = (h11.conjugate() * h11 + h21.conjugate() * h21) + alpha
    g12 = h11.conjugate() * h12 + h21.conjugate() * h22
    g21 = h12.conjugate() * h11 + h22.conjugate() * h21
    g22 = (h12.conjugate() * h12 + h22.conjugate() * h22) + alpha

    ig11, ig12, ig21, ig22 = mat2x2_inv(g11, g12, g21, g22)

    y1, y2 = y[0], y[1]
    ymf1 = h11.conjugate() * y1 + h21.conjugate() * y2
    ymf2 = h12.conjugate() * y1 + h22.conjugate() * y2

    x1_est = ig11 * ymf1 + ig12 * ymf2
    x2_est = ig21 * ymf1 + ig22 * ymf2

    return [hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est)]

def detect_ml_2x2(H: list, y: list) -> list:
    """Maximum Likelihood: повний перебір векторів сузір'я s ∈ Q²."""
    h11, h12 = H[0][0], H[0][1]
    h21, h22 = H[1][0], H[1][1]
    y1, y2 = y[0], y[1]

    best_dist = float("inf")
    best_s = [QPSK_CONSTELLATION[0], QPSK_CONSTELLATION[0]]

    for s1 in QPSK_CONSTELLATION:
        for s2 in QPSK_CONSTELLATION:
            # Очікуваний вектор безшумного відгуку r = H · s
            r1 = h11 * s1 + h12 * s2
            r2 = h21 * s1 + h22 * s2

            dist = abs(y1 - r1)**2 + abs(y2 - r2)**2
            if dist < best_dist:
                best_dist = dist
                best_s = [s1, s2]

    return best_s

def run_simulation(num_packets=10000, snr_db=14.0):
    """Монте-Карло симуляція 2x2 MIMO системи з релеївським каналом."""
    snr_lin = 10.0 ** (snr_db / 10.0)
    sigma_noise = math.sqrt(1.0 / (2.0 * snr_lin))

    err_zf = 0
    err_mmse = 0
    err_ml = 0
    total_symbols = num_packets * 2

    for _ in range(num_packets):
        tx_syms = [random.choice(QPSK_CONSTELLATION), random.choice(QPSK_CONSTELLATION)]

        # Релеївський канал H (комплексні гаусові відліки CN(0, 1))
        H = [
            [complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071)),
             complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071))],
            [complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071)),
             complex(random.gauss(0, 0.7071), random.gauss(0, 0.7071))]
        ]

        n1 = complex(random.gauss(0, sigma_noise), random.gauss(0, sigma_noise))
        n2 = complex(random.gauss(0, sigma_noise), random.gauss(0, sigma_noise))

        y1 = H[0][0] * tx_syms[0] + H[0][1] * tx_syms[1] + n1
        y2 = H[1][0] * tx_syms[0] + H[1][1] * tx_syms[1] + n2
        y = [y1, y2]

        hat_zf = detect_zf_2x2(H, y)
        hat_mmse = detect_mmse_2x2(H, y, snr_lin)
        hat_ml = detect_ml_2x2(H, y)

        for i in range(2):
            if abs(hat_zf[i] - tx_syms[i]) > 1e-4:
                err_zf += 1
            if abs(hat_mmse[i] - tx_syms[i]) > 1e-4:
                err_mmse += 1
            if abs(hat_ml[i] - tx_syms[i]) > 1e-4:
                err_ml += 1

    return {
        "SER_ZF": err_zf / total_symbols,
        "SER_MMSE": err_mmse / total_symbols,
        "SER_ML": err_ml / total_symbols,
    }

if __name__ == "__main__":
    res = run_simulation(num_packets=5000, snr_db=14.0)
    print(f"Результати при SNR = 14 дБ:")
    print(f"  Zero-Forcing SER: {res['SER_ZF']:.4e}")
    print(f"  MMSE SER:         {res['SER_MMSE']:.4e}")
    print(f"  Max-Likelihood:   {res['SER_ML']:.4e}")
