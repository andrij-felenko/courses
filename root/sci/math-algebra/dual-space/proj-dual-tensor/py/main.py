import numpy as np

class Vector:
    """Контраваріантний вектор v у просторі V (компоненти-стовпчик)."""
    def __init__(self, data):
        self.data = np.array(data, dtype=float).reshape(-1, 1)

    def __getitem__(self, idx):
        return self.data[idx, 0]

    def __repr__(self):
        return f"Vector({self.data.ravel().tolist()})"

class Covector:
    """Коваріантний ковектор p у дуальному просторі V* (компоненти-рядок)."""
    def __init__(self, data):
        self.data = np.array(data, dtype=float).reshape(1, -1)

    def __getitem__(self, idx):
        return self.data[0, idx]

    def __repr__(self):
        return f"Covector({self.data.ravel().tolist()})"

def evaluate(p: Covector, v: Vector) -> float:
    """Дуальна пара <p, v> = p_i * v^i (скалярний результат дії функціонала)."""
    return float(p.data @ v.data)

def dual_basis(basis_matrix: np.ndarray) -> np.ndarray:
    """Обчислює матрицю дуального базису E* за прямою матрицею базису E."""
    # Рядки оберненої матриці є ковекторами дуального базису
    return np.linalg.inv(basis_matrix)

def transform_vector(v: Vector, P: np.ndarray) -> Vector:
    """Контраваріантне перетворення координат вектора: v' = P^(-1) * v."""
    P_inv = np.linalg.inv(P)
    return Vector((P_inv @ v.data).ravel())

def transform_covector(p: Covector, P: np.ndarray) -> Covector:
    """Коваріантне перетворення компонент ковектора: p' = p * P."""
    return Covector((p.data @ P).ravel())

def lower_index(v: Vector, g: np.ndarray) -> Covector:
    """Опускання індексу через метричний тензор: v_flat = g * v."""
    return Covector((g @ v.data).ravel())

def raise_index(p: Covector, g: np.ndarray) -> Vector:
    """Підняття індексу через обернену метрику: p_sharp = g^(-1) * p^T."""
    g_inv = np.linalg.inv(g)
    return Vector((g_inv @ p.data.T).ravel())

if __name__ == "__main__":
    # 1. Початкові вектор і ковектор
    v = Vector([2.0, 3.0])
    p = Covector([4.0, -1.0])
    
    print(f"Початковий вектор:   {v}")
    print(f"Початковий ковектор: {p}")
    pairing = evaluate(p, v)
    print(f"Згортка <p, v>:      {pairing:.4f} (4*2 + (-1)*3 = 5.0)")

    # 2. Зміна базису: вісь x1 розтягуємо у 2 рази, x2 повертаємо
    P = np.array([[2.0, 0.0],
                  [0.0, 1.0]])

    v_prime = transform_vector(v, P)
    p_prime = transform_covector(p, P)

    print("\nПісля зміни базису матрицею P:")
    print(f"Вектор v' (контраваріантний): {v_prime}")
    print(f"Ковектор p' (коваріантний):   {p_prime}")
    new_pairing = evaluate(p_prime, v_prime)
    print(f"Згортка <p', v'>:             {new_pairing:.4f} (інваріант збережено!)")

    # 3. Метрика та музичні ізоморфізми
    g = np.array([[2.0, 1.0],
                  [1.0, 3.0]])

    p_flat = lower_index(v, g)
    v_restored = raise_index(p_flat, g)

    print("\nМузичні ізоморфізми з метрикою g:")
    print(f"v_flat (опускання індексу):   {p_flat}")
    print(f"v_sharp (підняття індексу):   {v_restored}")
    print(f"Помилка відновлення:          {np.linalg.norm(v.data - v_restored.data):.2e}")
