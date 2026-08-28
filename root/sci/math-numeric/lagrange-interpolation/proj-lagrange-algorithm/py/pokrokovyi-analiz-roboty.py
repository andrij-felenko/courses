def lagrange_naive_eval(x_nodes: list[float], y_nodes: list[float], target_x: float) -> float:
    """Обчислення наївної інтерполяції Лагранжа мовою Python."""
    n = len(x_nodes)
    if n != len(y_nodes) or n == 0:
        raise ValueError("Розміри масивів повинні збігатися і бути додатними.")

    result = 0.0
    for k in range(n):
        if abs(target_x - x_nodes[k]) < 1e-12:
            return y_nodes[k]

        term = y_nodes[k]
        for j in range(n):
            if j != k:
                denom = x_nodes[k] - x_nodes[j]
                if abs(denom) < 1e-15:
                    raise ValueError(f"Дубльований вузол x[{k}] == x[{j}]")
                term *= (target_x - x_nodes[j]) / denom
        result += term

    return result

if __name__ == "__main__":
    x = [1.0, 2.0, 4.0]
    y = [1.0, 4.0, 16.0]
    print(f"P(3.0) = {lagrange_naive_eval(x, y, 3.0):.4f}")
