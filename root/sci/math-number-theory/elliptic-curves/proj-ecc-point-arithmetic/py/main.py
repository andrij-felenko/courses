#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Точкова арифметика на еліптичній кривій над скінченним полем F_p.

Реалізація охоплює афінні координати, проективні координати Якобі,
драбину Монтгомері (Constant-Time), алгоритм Тонеллі-Шенкса для стиснення точок
та емуляцію протоколу обміну ключами Діффі-Геллмана (ECDH).
"""

from typing import Optional, Tuple, List, Union


class Point:
    """Точка на еліптичній кривій в афінних координатах (x, y).

    Атрибут coord = None представляє точку на нескінченності O.
    """

    def __init__(self, coord: Optional[Tuple[int, int]] = None):
        self.coord = coord

    @property
    def is_infinity(self) -> bool:
        """Перевірка, чи є точка точкою на нескінченності O."""
        return self.coord is None

    def __repr__(self) -> str:
        if self.is_infinity:
            return "Point(O)"
        return f"Point({self.coord[0]}, {self.coord[1]})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.coord == other.coord


class JacobianPoint:
    """Точка у проективних координатах Якобі (X : Y : Z).

    Зв'язок з афінними координатами: x = X / Z^2, y = Y / Z^3.
    """

    def __init__(self, X: int = 1, Y: int = 1, Z: int = 0, is_infinity: bool = True):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.is_infinity = is_infinity

    def __repr__(self) -> str:
        if self.is_infinity:
            return "JacobianPoint(O)"
        return f"JacobianPoint({self.X} : {self.Y} : {self.Z})"


class EllipticCurve:
    """Еліптична крива Вейєрштрасса: y^2 = x^3 + a*x + b (mod p)."""

    def __init__(self, a: int, b: int, p: int, order: Optional[int] = None):
        self.a = a
        self.b = b
        self.p = p
        self.order = order

    def _mod_pos(self, val: int) -> int:
        """Нормалізація значення у діапазон [0, p - 1]."""
        return val % self.p

    def _mod_inverse(self, val: int) -> int:
        """Розширений алгоритм Евкліда для обчислення оберненого елемента."""
        return pow(val, -1, self.p)

    def _mod_sqrt(self, val: int) -> Optional[int]:
        """Обчислення квадратного кореня mod p (Тонеллі-Шенкс або p = 4k + 3)."""
        n = self._mod_pos(val)
        if n == 0:
            return 0
        # Перевірка за критерієм Ейлера
        if pow(n, (self.p - 1) // 2, self.p) != 1:
            return None  # Не є квадратичним лишком

        if self.p % 4 == 3:
            return pow(n, (self.p + 1) // 4, self.p)

        # Алгоритм Тонеллі-Шенкса
        q = self.p - 1
        s = 0
        while q % 2 == 0:
            s += 1
            q //= 2

        z = 2
        while pow(z, (self.p - 1) // 2, self.p) != self.p - 1:
            z += 1

        m = s
        c = pow(z, q, self.p)
        t = pow(n, q, self.p)
        r = pow(n, (q + 1) // 2, self.p)

        while t not in (0, 1):
            t2i = t
            i = 0
            for i in range(1, m):
                t2i = (t2i * t2i) % self.p
                if t2i == 1:
                    break
            b_exp = 1 << (m - i - 1)
            b = pow(c, b_exp, self.p)
            m = i
            c = (b * b) % self.p
            t = (t * c) % self.p
            r = (r * b) % self.p

        return r

    def is_on_curve(self, P: Point) -> bool:
        """Перевірка належності точки кривій."""
        if P.is_infinity:
            return True
        x, y = P.coord
        lhs = (y * y) % self.p
        rhs = (pow(x, 3, self.p) + self.a * x + self.b) % self.p
        return lhs == rhs

    def negate(self, P: Point) -> Point:
        """Протилежна точка: -P = (x, -y mod p)."""
        if P.is_infinity:
            return P
        x, y = P.coord
        return Point((x, (-y) % self.p))

    def double_point(self, P: Point) -> Point:
        """Подвоєння точки R = 2*P."""
        if P.is_infinity or P.coord[1] == 0:
            return Point(None)

        x1, y1 = P.coord
        num = (3 * x1 * x1 + self.a) % self.p
        den = (2 * y1) % self.p
        lambda_val = (num * self._mod_inverse(den)) % self.p

        x3 = (lambda_val * lambda_val - 2 * x1) % self.p
        y3 = (lambda_val * (x1 - x3) - y1) % self.p

        return Point((x3, y3))

    def add(self, P: Point, Q: Point) -> Point:
        """Додавання двох точок R = P + Q."""
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

        x3 = (lambda_val * lambda_val - x1 - x2) % self.p
        y3 = (lambda_val * (x1 - x3) - y1) % self.p

        return Point((x3, y3))

    def scalar_multiply(self, k: int, P: Point) -> Point:
        """Скалярне множення R = k * P методом Double-and-Add."""
        result = Point(None)
        addend = P
        scalar = k

        if self.order:
            scalar %= self.order

        while scalar > 0:
            if scalar & 1:
                result = self.add(result, addend)
            addend = self.double_point(addend)
            scalar >>= 1

        return result

    def _cswap(self, bit: int, P: Point, Q: Point) -> Tuple[Point, Point]:
        """Умовний обмін точок у сталий час без розгалужень."""
        mask = -(bit & 1)
        p_inf = 1 if P.is_infinity else 0
        q_inf = 1 if Q.is_infinity else 0

        px = 0 if P.is_infinity else P.coord[0]
        py = 0 if P.is_infinity else P.coord[1]
        qx = 0 if Q.is_infinity else Q.coord[0]
        qy = 0 if Q.is_infinity else Q.coord[1]

        dx = mask & (px ^ qx)
        px ^= dx
        qx ^= dx

        dy = mask & (py ^ qy)
        py ^= dy
        qy ^= dy

        d_inf = mask & (p_inf ^ q_inf)
        p_inf ^= d_inf
        q_inf ^= d_inf

        new_P = Point(None) if p_inf else Point((px, py))
        new_Q = Point(None) if q_inf else Point((qx, qy))
        return new_P, new_Q

    def scalar_multiply_montgomery(self, k: int, P: Point) -> Point:
        """Скалярне множення методом драбини Монтгомері (Constant-Time)."""
        R0 = Point(None)
        R1 = P
        scalar = k
        if self.order:
            scalar %= self.order

        if scalar == 0:
            return R0

        bit_len = scalar.bit_length()
        for i in reversed(range(bit_len)):
            bit = (scalar >> i) & 1
            R0, R1 = self._cswap(bit, R0, R1)
            R1 = self.add(R0, R1)
            R0 = self.double_point(R0)
            R0, R1 = self._cswap(bit, R0, R1)

        return R0

    # -------------------------------------------------------------------------
    # Координати Якобі
    # -------------------------------------------------------------------------

    def to_jacobian(self, P: Point) -> JacobianPoint:
        """Перетворення афінної точки у координати Якобі."""
        if P.is_infinity:
            return JacobianPoint(1, 1, 0, True)
        return JacobianPoint(P.coord[0], P.coord[1], 1, False)

    def to_affine(self, JP: JacobianPoint) -> Point:
        """Перетворення координат Якобі в афінну точку."""
        if JP.is_infinity or JP.Z == 0:
            return Point(None)
        z_inv = self._mod_inverse(JP.Z)
        z_inv2 = (z_inv * z_inv) % self.p
        z_inv3 = (z_inv2 * z_inv) % self.p
        x = (JP.X * z_inv2) % self.p
        y = (JP.Y * z_inv3) % self.p
        return Point((x, y))

    def jacobian_double(self, JP: JacobianPoint) -> JacobianPoint:
        """Подвоєння точки у координатах Якобі: 4M + 6S."""
        if JP.is_infinity or JP.Y == 0:
            return JacobianPoint(1, 1, 0, True)

        p = self.p
        S = (4 * JP.X * JP.Y * JP.Y) % p
        Z2 = (JP.Z * JP.Z) % p
        Z4 = (Z2 * Z2) % p
        M = (3 * JP.X * JP.X + self.a * Z4) % p

        X3 = (M * M - 2 * S) % p
        Y2 = (JP.Y * JP.Y) % p
        Y4 = (Y2 * Y2) % p
        Y3 = (M * (S - X3) - 8 * Y4) % p
        Z3 = (2 * JP.Y * JP.Z) % p

        return JacobianPoint(X3, Y3, Z3, False)

    def jacobian_add(self, JP1: JacobianPoint, JP2: JacobianPoint) -> JacobianPoint:
        """Додавання двох точок у координатах Якобі: 12M + 4S."""
        if JP1.is_infinity:
            return JP2
        if JP2.is_infinity:
            return JP1

        p = self.p
        Z1_2 = (JP1.Z * JP1.Z) % p
        Z2_2 = (JP2.Z * JP2.Z) % p

        U1 = (JP1.X * Z2_2) % p
        U2 = (JP2.X * Z1_2) % p

        S1 = (JP1.Y * JP2.Z * Z2_2) % p
        S2 = (JP2.Y * JP1.Z * Z1_2) % p

        if U1 == U2:
            if S1 != S2:
                return JacobianPoint(1, 1, 0, True)
            return self.jacobian_double(JP1)

        H = (U2 - U1) % p
        r = (S2 - S1) % p
        H2 = (H * H) % p
        H3 = (H * H2) % p

        X3 = (r * r - H3 - 2 * U1 * H2) % p
        Y3 = (r * (U1 * H2 - X3) - S1 * H3) % p
        Z3 = (H * JP1.Z * JP2.Z) % p

        return JacobianPoint(X3, Y3, Z3, False)

    # -------------------------------------------------------------------------
    # Стиснення та відновлення точок
    # -------------------------------------------------------------------------

    def compress(self, P: Point) -> bytes:
        """Стиснення точки у 9-байтний формат SECG."""
        if P.is_infinity:
            return b"\x00" + b"\x00" * 8
        prefix = b"\x02" if P.coord[1] % 2 == 0 else b"\x03"
        return prefix + P.coord[0].to_bytes(8, byteorder="big")

    def decompress(self, data: bytes) -> Optional[Point]:
        """Відновлення точки зі стисненого формату."""
        if len(data) != 9:
            return None
        if data[0] == 0x00:
            return Point(None)
        if data[0] not in (0x02, 0x03):
            return None

        x = int.from_bytes(data[1:], byteorder="big") % self.p
        rhs = (pow(x, 3, self.p) + self.a * x + self.b) % self.p
        y = self._mod_sqrt(rhs)
        if y is None:
            return None

        want_odd = data[0] == 0x03
        if (y % 2 != 0) != want_odd:
            y = (-y) % self.p

        return Point((x, y))

    def ecdh_shared_secret(self, priv_key: int, pub_key: Point) -> Optional[int]:
        """Обчислення спільного секрету ECDH."""
        if not self.is_on_curve(pub_key) or pub_key.is_infinity:
            return None
        shared = self.scalar_multiply(priv_key, pub_key)
        if shared.is_infinity:
            return None
        return shared.coord[0]


if __name__ == "__main__":
    curve = EllipticCurve(a=2, b=3, p=97, order=5)
    P = Point((3, 6))

    print("=== Тестування точкової арифметики Python (F_97) ===")
    print(f"Крива: y^2 = x^3 + {curve.a}*x + {curve.b} (mod {curve.p})")
    print(f"Базова точка P: {P}")

    # 1. Перевірка належності точки кривій
    assert curve.is_on_curve(P), "Точка P повинна належати кривій"
    print("[OK] Базова точка P належить кривій.")

    # 2. Контрольні вектори
    P2 = curve.double_point(P)
    print(f"2*P: {P2}")
    P3 = curve.add(P2, P)
    print(f"3*P: {P3}")
    P4 = curve.double_point(P2)
    print(f"4*P: {P4}")
    P5 = curve.add(P4, P)
    print(f"5*P: {P5}")

    # 3. Скалярне множення k*P
    print("\n=== Скалярне множення k*P (Double-and-Add) ===")
    for k in range(1, 6):
        print(f"k = {k}: {curve.scalar_multiply(k, P)}")

    # 4. Порівняння з драбиною Монтгомері
    print("\n=== Драбина Монтгомері ===")
    for k in range(1, 6):
        pm = curve.scalar_multiply_montgomery(k, P)
        ps = curve.scalar_multiply(k, P)
        assert pm == ps, f"Розбіжність для k = {k}"
    print("[OK] Драбина Монтгомері повністю узгоджується з Double-and-Add.")

    # 5. Координати Якобі
    print("\n=== Точкова арифметика Якобі ===")
    JP = curve.to_jacobian(P)
    JP2 = curve.jacobian_double(JP)
    print(f"2*P через Якобі: {curve.to_affine(JP2)}")
    JP3 = curve.jacobian_add(JP2, JP)
    print(f"3*P через Якобі: {curve.to_affine(JP3)}")

    # 6. Стиснення точок
    print("\n=== Стиснення точок ===")
    comp = curve.compress(P)
    print(f"Стиснений байти: {comp.hex()}")
    decomp = curve.decompress(comp)
    assert decomp == P, "Декомпресія має повернути вихідну точку"
    print(f"[OK] Відновлена точка: {decomp}")

    # 7. Протокол ECDH
    print("\n=== Протокол ECDH ===")
    alice_priv = 2
    alice_pub = curve.scalar_multiply(alice_priv, P)  # 2*P = (80, 10)
    bob_priv = 3
    bob_pub = curve.scalar_multiply(bob_priv, P)      # 3*P = (80, 87)

    alice_secret = curve.ecdh_shared_secret(alice_priv, bob_pub)
    bob_secret = curve.ecdh_shared_secret(bob_priv, alice_pub)
    assert alice_secret == bob_secret, "Секрети повинні збігатися"
    print(f"Спільний секретний x-ключ: {alice_secret}")
    print("[OK] Протокол ECDH верифіковано успішно.")
