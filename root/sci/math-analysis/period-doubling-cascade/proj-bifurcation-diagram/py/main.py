import numpy as np

def logistic(x, r):
    return r * x * (1.0 - x)

def logistic_derivative_r(x, r, w):
    return r * (1.0 - 2.0 * x) * w + x * (1.0 - x)

def find_superstable_r(n, r_guess):
    period = 1 << n
    r = r_guess
    for _ in range(100):
        x = 0.5
        w = 0.0
        for _ in range(period):
            w = logistic_derivative_r(x, r, w)
            x = logistic(x, r)
        
        f_val = x - 0.5
        f_prime = w
        if abs(f_val) < 1e-13:
            break
        r = r - f_val / f_prime
    return r

def calculate_lyapunov(r, num_iters=50000):
    x = 0.5
    for _ in range(1000):
        x = logistic(x, r)
    
    sum_log = 0.0
    for _ in range(num_iters):
        deriv = abs(r * (1.0 - 2.0 * x))
        if deriv < 1e-12:
            deriv = 1e-12
        sum_log += np.log(deriv)
        x = logistic(x, r)
    return sum_log / num_iters

if __name__ == "__main__":
    guesses = [2.0, 3.2, 3.498, 3.5546, 3.56666, 3.56924]
    R_vals = [find_superstable_r(i, g) for i, g in enumerate(guesses)]
    
    for i, R in enumerate(R_vals):
        print(f"R_{i} = {R:.12f}")
    
    print("\n=== Обчислення сталої delta ===")
    for i in range(1, len(R_vals) - 1):
        delta = (R_vals[i] - R_vals[i-1]) / (R_vals[i+1] - R_vals[i]);
        print(f"delta_{i} = {delta:.12f}")
