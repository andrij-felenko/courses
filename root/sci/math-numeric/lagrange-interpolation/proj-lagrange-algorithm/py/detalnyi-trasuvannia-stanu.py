class BarycentricInterpolator:
    """Виробнича барицентрична інтерполяція мовою Python."""
    def __init__(self):
        self.x: list[float] = []
        self.y: list[float] = []
        self.weights: list[float] = []

    def add_point(self, new_x: float, new_y: float) -> bool:
        for existing_x in self.x:
            if abs(existing_x - new_x) < 1e-12:
                return False

        n = len(self.x)
        self.x.append(new_x)
        self.y.append(new_y)

        new_w = 1.0
        for k in range(n):
            diff = self.x[k] - new_x
            self.weights[k] /= diff
            new_w /= (new_x - self.x[k])
        self.weights.append(new_w)
        return True

    def eval(self, target_x: float) -> float:
        if not self.x:
            raise ValueError("Інтерполятор порожній.")

        num = 0.0
        den = 0.0

        for k in range(len(self.x)):
            diff = target_x - self.x[k]
            if abs(diff) < 1e-12:
                return self.y[k]
            term = self.weights[k] / diff
            num += term * self.y[k]
            den += term

        return num / den

if __name__ == "__main__":
    interp = BarycentricInterpolator()
    for x_i, y_i in [(1.0, 1.0), (2.0, 4.0), (4.0, 16.0)]:
        interp.add_point(x_i, y_i)

    print(f"Python Барицентричний P(3.0) = {interp.eval(3.0):.4f}")
