import numpy as np

def hilbert_matrix(n: int, dtype=np.float64) -> np.ndarray:
    """Генерація матриці Гільберта H[i, j] = 1 / (i + j + 1)."""
    i, j = np.ogrid[:n, :n]
    return (1.0 / (i + j + 1)).astype(dtype)

def solve_gaussian_elimination(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Метод Гаусса з вибором головного елемента по стовпцю (частковий півотинг)."""
    A_work = A.copy()
    b_work = b.copy()
    n = len(b_work)

    for k in range(n - 1):
        # Вибір головного елемента
        pivot = np.argmax(np.abs(A_work[k:, k])) + k
        if np.abs(A_work[pivot, k]) < 1e-15:
            raise ValueError("Матриця чисельно сингулярна")
        
        # Перестановка рядків
        if pivot != k:
            A_work[[k, pivot]] = A_work[[pivot, k]]
            b_work[[k, pivot]] = b_work[[pivot, k]]

        # Прямий хід виключення
        for i in range(k + 1, n):
            factor = A_work[i, k] / A_work[k, k]
            A_work[i, k:] -= factor * A_work[k, k:]
            b_work[i] -= factor * b_work[k]

    # Зворотна підстановка
    x = np.zeros_like(b_work)
    for i in range(n - 1, -1, -1):
        x[i] = (b_work[i] - np.dot(A_work[i, i + 1:], x[i + 1:])) / A_work[i, i]

    return x

def tikhonov_regularization(A: np.ndarray, b: np.ndarray, lam: float) -> np.ndarray:
    """Регуляризація Тихонова: (AᵀA + λ²I) x = Aᵀb."""
    n = A.shape[1]
    AtA = np.dot(A.T, A)
    Atb = np.dot(A.T, b)
    reg_matrix = AtA + (lam ** 2) * np.eye(n, dtype=A.dtype)
    return solve_gaussian_elimination(reg_matrix, Atb)

def run_experiment():
    print("=== ТЕСТУВАННЯ МАТРИЦЬ ГІЛЬБЕРТА ТА ЧИСЛА ОБУМОВЛЕНОСТІ ===")
    print(f"{'Розмір n':>8} | {'cond_2(H_n)':>14} | {'Похибка float32':>18} | {'Похибка float64':>18}")
    print("-" * 68)

    for n in range(2, 11):
        # Подвійна точність (float64)
        H64 = hilbert_matrix(n, dtype=np.float64)
        x_exact64 = np.ones(n, dtype=np.float64)
        b64 = np.dot(H64, x_exact64)
        
        # Одинарна точність (float32)
        H32 = hilbert_matrix(n, dtype=np.float32)
        x_exact32 = np.ones(n, dtype=np.float32)
        b32 = np.dot(H32, x_exact32)

        # Обчислення точного cond_2 через SVD
        U, s, Vt = np.linalg.svd(H64)
        cond2 = s[0] / s[-1]

        # Розв'язання в float32
        try:
            x_comp32 = solve_gaussian_elimination(H32, b32)
            err32 = np.linalg.norm(x_comp32 - x_exact32) / np.linalg.norm(x_exact32)
            str_err32 = f"{err32:.2e}"
        except Exception:
            str_err32 = "FAIL (SINGULAR)"

        # Розв'язання в float64
        try:
            x_comp64 = solve_gaussian_elimination(H64, b64)
            err64 = np.linalg.norm(x_comp64 - x_exact64) / np.linalg.norm(x_exact64)
            str_err64 = f"{err64:.2e}"
        except Exception:
            str_err64 = "FAIL (SINGULAR)"

        print(f"{n:>8} | {cond2:>14.2e} | {str_err32:>18} | {str_err64:>18}")

if __name__ == "__main__":
    run_experiment()
