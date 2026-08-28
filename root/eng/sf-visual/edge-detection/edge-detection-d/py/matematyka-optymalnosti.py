import math


# SNR ≈ A·|сума додатних ваг| / (n0·√(сума квадратів ваг))
def snr(k, A, n0):
    sig = sum(w for w in k if w > 0)   # внесок у відгук на сходинку
    energy = sum(w * w for w in k)     # пропускання шуму
    return A * sig / (n0 * math.sqrt(energy))


if __name__ == "__main__":
    sobel = [-1, 0, 1]
    wide = [-1, -2, 0, 2, 1]
    print(f"вузьке  [-1 0 1]:      SNR = {snr(sobel, 100, 10):.2f}")
    print(f"ширше   [-1 -2 0 2 1]: SNR = {snr(wide, 100, 10):.2f}")
