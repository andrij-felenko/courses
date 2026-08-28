from typing import Optional, Tuple

class Point:
    def __init__(self, coord: Optional[Tuple[int, int]] = None):
        self.coord = coord  # None відповідає точці O (нескінченність)

    @property
    def is_infinity(self) -> bool:
        return self.coord is None

    def __repr__(self) -> str:
        if self.is_infinity:
            return "Point(O)"
        return f"Point({self.coord[0]}, {self.coord[1]})"


class EllipticCurve:
    def __init__(self, a: int, b: int, p: int):
        self.a = a
        self.b = b
        self.p = p

    def _mod_inverse(self, val: int) -> int:
        # Вбудований розширений алгоритм Евкліда в Python 3.8+
        return pow(val, -1, self.p)

    def double_point(self, P: Point) -> Point:
        if P.is_infinity or P.coord[1] == 0:
            return Point(None)

        x1, y1 = P.coord
        num = (3 * x1**2 + self.a) % self.p
        den = (2 * y1) % self.p
        lambda_val = (num * self._mod_inverse(den)) % self.p

        x3 = (lambda_val**2 - 2 * x1) % self.p
        y3 = (lambda_val * (x1 - x3) - y1) % self.p

        return Point((x3, y3))

    def add(self, P: Point, Q: Point) -> Point:
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P

        x1, y1 = P.coord
        x2, y2 = Q.coord

        if x1 == x2:
            if (y1 + y2) % self.p == 0:
                return Point(None)
            return self.double_point(P)

        num = (y2 - y1) % self.p
        den = (x2 - x1) % self.p
        lambda_val = (num * self._mod_inverse(den)) % self.p

        x3 = (lambda_val**2 - x1 - x2) % self.p
        y3 = (lambda_val * (x1 - x3) - y1) % self.p

        return Point((x3, y3))

    def scalar_multiply(self, k: int, P: Point) -> Point:
        result = Point(None)
        addend = P

        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.double_point(addend)
            k >>= 1

        return result


if __name__ == "__main__":
    curve = EllipticCurve(a=2, b=3, p=97)
    P = Point((3, 6))

    print(f"Початкова точка P: {P}")
    P2 = curve.double_point(P)
    print(f"2*P: {P2}")
    P3 = curve.add(P2, P)
    print(f"3*P: {P3}")
    P5 = curve.scalar_multiply(5, P)
    print(f"5*P (Double-and-Add): {P5}")
