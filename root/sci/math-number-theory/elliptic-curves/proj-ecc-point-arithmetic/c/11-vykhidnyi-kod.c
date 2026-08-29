#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// Структури даних точкової арифметики на еліптичній кривій
// ============================================================================

// Точка в афінних координатах: (x, y) або O (нескінченність)
typedef struct {
    int64_t x;
    int64_t y;
    bool is_infinity;
} Point;

// Точка у проективних координатах Якобі: (X : Y : Z), де x = X/Z^2, y = Y/Z^3
typedef struct {
    int64_t X;
    int64_t Y;
    int64_t Z;
    bool is_infinity;
} JacobianPoint;

// Параметри кривої Вейєрштрасса: y^2 = x^3 + a*x + b (mod p)
typedef struct {
    int64_t a;
    int64_t b;
    int64_t p;
    int64_t order; // Порядок базової точки (підгрупи)
} EllipticCurve;

// ============================================================================
// Модульна арифметика над скінченним полем F_p
// ============================================================================

// Нормалізація залишку в інтервал [0, p - 1]
static inline int64_t mod_pos(int64_t a, int64_t p) {
    int64_t r = a % p;
    return (r < 0) ? (r + p) : r;
}

// Модульне додавання: (a + b) mod p
static inline int64_t mod_add(int64_t a, int64_t b, int64_t p) {
    return mod_pos(a + b, p);
}

// Модульне віднімання: (a - b) mod p
static inline int64_t mod_sub(int64_t a, int64_t b, int64_t p) {
    return mod_pos(a - b, p);
}

// Модульне множення: (a * b) mod p
static inline int64_t mod_mul(int64_t a, int64_t b, int64_t p) {
    return mod_pos((int64_t)(((__int128)a * b) % p), p);
}

// Піднесення до степеня за модулем p методом двійкового піднесення: base^exp mod p
static int64_t mod_pow(int64_t base, int64_t exp, int64_t p) {
    int64_t res = 1;
    int64_t b = mod_pos(base, p);
    int64_t e = exp;
    while (e > 0) {
        if (e & 1) {
            res = mod_mul(res, b, p);
        }
        b = mod_mul(b, b, p);
        e >>= 1;
    }
    return res;
}

// Розширений алгоритм Евкліда для знаходження b^-1 mod p
static int64_t mod_inverse(int64_t b, int64_t p) {
    int64_t t = 0, newt = 1;
    int64_t r = p, newr = mod_pos(b, p);

    while (newr != 0) {
        int64_t quotient = r / newr;
        int64_t temp_t = t - quotient * newt;
        t = newt;
        newt = temp_t;

        int64_t temp_r = r - quotient * newr;
        r = newr;
        newr = temp_r;
    }

    if (r > 1) return -1; // Обернений елемент не існує (gcd(b, p) > 1)
    return mod_pos(t, p);
}

// Обчислення квадратного кореня mod p (для p = 4k + 3 або загальний випадок)
static int64_t mod_sqrt(int64_t a, int64_t p) {
    int64_t n = mod_pos(a, p);
    if (n == 0) return 0;
    // Критерій Ейлера: перевірка чи є n квадратичним лишком
    if (mod_pow(n, (p - 1) / 2, p) != 1) {
        return -1; // Не є квадратом
    }
    // Для p = 3 (mod 4): sqrt(n) = n^((p + 1) / 4) mod p
    if (p % 4 == 3) {
        return mod_pow(n, (p + 1) / 4, p);
    }
    // Алгоритм Тонеллі-Шенкса для довільного простого p
    int64_t q = p - 1;
    int64_t s = 0;
    while ((q & 1) == 0) {
        s++;
        q >>= 1;
    }
    int64_t z = 2;
    while (mod_pow(z, (p - 1) / 2, p) != p - 1) {
        z++;
    }
    int64_t m = s;
    int64_t c = mod_pow(z, q, p);
    int64_t t = mod_pow(n, q, p);
    int64_t r = mod_pow(n, (q + 1) / 2, p);

    while (t != 0 && t != 1) {
        int64_t t2i = t;
        int64_t i = 0;
        for (i = 1; i < m; i++) {
            t2i = mod_mul(t2i, t2i, p);
            if (t2i == 1) break;
        }
        int64_t b_exp = 1LL << (m - i - 1);
        int64_t b = mod_pow(c, b_exp, p);
        m = i;
        c = mod_mul(b, b, p);
        t = mod_mul(t, c, p);
        r = mod_mul(r, b, p);
    }
    return r;
}

// ============================================================================
// Афінна точкова арифметика
// ============================================================================

// Створення точки на нескінченності O
Point point_infinity(void) {
    Point pt = {0, 0, true};
    return pt;
}

// Створення звичайної афінної точки (x, y)
Point point_create(int64_t x, int64_t y) {
    Point pt = {x, y, false};
    return pt;
}

// Перевірка рівності двох точок
bool point_equals(Point p1, Point p2) {
    if (p1.is_infinity && p2.is_infinity) return true;
    if (p1.is_infinity || p2.is_infinity) return false;
    return (p1.x == p2.x) && (p1.y == p2.y);
}

// Протилежна точка: -P = (x, -y mod p)
Point point_negate(Point p, int64_t p_mod) {
    if (p.is_infinity) return p;
    return point_create(p.x, mod_pos(-p.y, p_mod));
}

// Перевірка належності точки еліптичній кривій: y^2 = x^3 + a*x + b (mod p)
bool point_is_on_curve(Point pt, const EllipticCurve* curve) {
    if (pt.is_infinity) return true;
    int64_t lhs = mod_mul(pt.y, pt.y, curve->p);
    int64_t rhs = mod_add(mod_add(mod_pow(pt.x, 3, curve->p), mod_mul(curve->a, pt.x, curve->p), curve->p), curve->b, curve->p);
    return lhs == rhs;
}

// Подвоєння точки: R = 2*P mod p
Point point_double(Point p1, const EllipticCurve* curve) {
    if (p1.is_infinity || p1.y == 0) {
        return point_infinity();
    }

    // lambda = (3*x1^2 + a) * (2*y1)^-1 mod p
    int64_t num = mod_add(mod_mul(3, mod_mul(p1.x, p1.x, curve->p), curve->p), curve->a, curve->p);
    int64_t den = mod_mul(2, p1.y, curve->p);
    int64_t den_inv = mod_inverse(den, curve->p);

    if (den_inv == -1) return point_infinity();

    int64_t lambda = mod_mul(num, den_inv, curve->p);

    // x3 = lambda^2 - 2*x1 mod p
    int64_t x3 = mod_sub(mod_mul(lambda, lambda, curve->p), mod_mul(2, p1.x, curve->p), curve->p);
    // y3 = lambda*(x1 - x3) - y1 mod p
    int64_t y3 = mod_sub(mod_mul(lambda, mod_sub(p1.x, x3, curve->p), curve->p), p1.y, curve->p);

    return point_create(x3, y3);
}

// Додавання двох точок: R = P + Q mod p
Point point_add(Point p1, Point p2, const EllipticCurve* curve) {
    if (p1.is_infinity) return p2;
    if (p2.is_infinity) return p1;

    // Якщо x1 == x2
    if (p1.x == p2.x) {
        if (mod_add(p1.y, p2.y, curve->p) == 0) {
            return point_infinity(); // P + (-P) = O
        }
        return point_double(p1, curve);
    }

    // lambda = (y2 - y1) * (x2 - x1)^-1 mod p
    int64_t num = mod_sub(p2.y, p1.y, curve->p);
    int64_t den = mod_sub(p2.x, p1.x, curve->p);
    int64_t den_inv = mod_inverse(den, curve->p);

    if (den_inv == -1) return point_infinity();

    int64_t lambda = mod_mul(num, den_inv, curve->p);

    // x3 = lambda^2 - x1 - x2 mod p
    int64_t x3 = mod_sub(mod_sub(mod_mul(lambda, lambda, curve->p), p1.x, curve->p), p2.x, curve->p);
    // y3 = lambda*(x1 - x3) - y1 mod p
    int64_t y3 = mod_sub(mod_mul(lambda, mod_sub(p1.x, x3, curve->p), curve->p), p1.y, curve->p);

    return point_create(x3, y3);
}

// Скалярне множення R = k * P методом Double-and-Add (двійкова драбина)
Point scalar_multiply(int64_t k, Point p1, const EllipticCurve* curve) {
    Point result = point_infinity();
    Point addend = p1;
    int64_t scalar = k;

    if (curve->order > 0) {
        scalar = scalar % curve->order;
        if (scalar < 0) scalar += curve->order;
    }

    while (scalar > 0) {
        if (scalar & 1) {
            result = point_add(result, addend, curve);
        }
        addend = point_double(addend, curve);
        scalar >>= 1;
    }
    return result;
}

// Умовний обмін точок без розгалуження (Constant-Time CSWAP)
void cswap_points(uint64_t bit, Point* P, Point* Q) {
    uint64_t mask = -(uint64_t)(bit & 1);
    uint64_t delta_x = mask & ((uint64_t)P->x ^ (uint64_t)Q->x);
    P->x = (int64_t)((uint64_t)P->x ^ delta_x);
    Q->x = (int64_t)((uint64_t)Q->x ^ delta_x);

    uint64_t delta_y = mask & ((uint64_t)P->y ^ (uint64_t)Q->y);
    P->y = (int64_t)((uint64_t)P->y ^ delta_y);
    Q->y = (int64_t)((uint64_t)Q->y ^ delta_y);

    uint8_t delta_inf = (uint8_t)(mask & ((uint8_t)P->is_infinity ^ (uint8_t)Q->is_infinity));
    P->is_infinity = (bool)((uint8_t)P->is_infinity ^ delta_inf);
    Q->is_infinity = (bool)((uint8_t)Q->is_infinity ^ delta_inf);
}

// Скалярне множення методом драбини Монтгомері (Montgomery Ladder) у сталий час
Point scalar_multiply_montgomery(int64_t k, Point P, const EllipticCurve* curve) {
    Point R0 = point_infinity();
    Point R1 = P;
    int64_t scalar = k;

    if (curve->order > 0) {
        scalar = scalar % curve->order;
        if (scalar < 0) scalar += curve->order;
    }

    // Знаходимо найстарший значущий біт
    int msb = 62;
    while (msb >= 0 && !((scalar >> msb) & 1)) {
        msb--;
    }

    for (int i = msb; i >= 0; i--) {
        uint64_t bit = (uint64_t)((scalar >> i) & 1);
        cswap_points(bit, &R0, &R1);
        R1 = point_add(R0, R1, curve);
        R0 = point_double(R0, curve);
        cswap_points(bit, &R0, &R1);
    }
    return R0;
}

// ============================================================================
// Проективна арифметика Якобі: (X : Y : Z)
// ============================================================================

// Перетворення афінної точки у координати Якобі
JacobianPoint affine_to_jacobian(Point p) {
    if (p.is_infinity) {
        JacobianPoint jp = {1, 1, 0, true};
        return jp;
    }
    JacobianPoint jp = {p.x, p.y, 1, false};
    return jp;
}

// Перетворення координат Якобі в афінні координати
Point jacobian_to_affine(JacobianPoint jp, const EllipticCurve* curve) {
    if (jp.is_infinity || jp.Z == 0) {
        return point_infinity();
    }
    int64_t z_inv = mod_inverse(jp.Z, curve->p);
    int64_t z_inv2 = mod_mul(z_inv, z_inv, curve->p);
    int64_t z_inv3 = mod_mul(z_inv2, z_inv, curve->p);

    int64_t x = mod_mul(jp.X, z_inv2, curve->p);
    int64_t y = mod_mul(jp.Y, z_inv3, curve->p);
    return point_create(x, y);
}

// Подвоєння точки у координатах Якобі: 4M + 6S
JacobianPoint jacobian_double(JacobianPoint jp, const EllipticCurve* curve) {
    if (jp.is_infinity || jp.Y == 0) {
        JacobianPoint inf = {1, 1, 0, true};
        return inf;
    }

    int64_t p = curve->p;
    int64_t S = mod_mul(4, mod_mul(jp.X, mod_mul(jp.Y, jp.Y, p), p), p);
    int64_t Z2 = mod_mul(jp.Z, jp.Z, p);
    int64_t Z4 = mod_mul(Z2, Z2, p);
    int64_t M = mod_add(mod_mul(3, mod_mul(jp.X, jp.X, p), p), mod_mul(curve->a, Z4, p), p);

    int64_t X3 = mod_sub(mod_mul(M, M, p), mod_mul(2, S, p), p);
    int64_t Y2 = mod_mul(jp.Y, jp.Y, p);
    int64_t Y4 = mod_mul(Y2, Y2, p);
    int64_t Y3 = mod_sub(mod_mul(M, mod_sub(S, X3, p), p), mod_mul(8, Y4, p), p);
    int64_t Z3 = mod_mul(2, mod_mul(jp.Y, jp.Z, p), p);

    JacobianPoint res = {X3, Y3, Z3, false};
    return res;
}

// Додавання точок у координатах Якобі: 12M + 4S
JacobianPoint jacobian_add(JacobianPoint jp1, JacobianPoint jp2, const EllipticCurve* curve) {
    if (jp1.is_infinity) return jp2;
    if (jp2.is_infinity) return jp1;

    int64_t p = curve->p;
    int64_t Z1_2 = mod_mul(jp1.Z, jp1.Z, p);
    int64_t Z2_2 = mod_mul(jp2.Z, jp2.Z, p);

    int64_t U1 = mod_mul(jp1.X, Z2_2, p);
    int64_t U2 = mod_mul(jp2.X, Z1_2, p);

    int64_t S1 = mod_mul(jp1.Y, mod_mul(jp2.Z, Z2_2, p), p);
    int64_t S2 = mod_mul(jp2.Y, mod_mul(jp1.Z, Z1_2, p), p);

    if (U1 == U2) {
        if (S1 != S2) {
            JacobianPoint inf = {1, 1, 0, true};
            return inf;
        }
        return jacobian_double(jp1, curve);
    }

    int64_t H = mod_sub(U2, U1, p);
    int64_t r = mod_sub(S2, S1, p);
    int64_t H2 = mod_mul(H, H, p);
    int64_t H3 = mod_mul(H, H2, p);

    int64_t X3 = mod_sub(mod_sub(mod_mul(r, r, p), H3, p), mod_mul(2, mod_mul(U1, H2, p), p), p);
    int64_t Y3 = mod_sub(mod_mul(r, mod_sub(mod_mul(U1, H2, p), X3, p), p), mod_mul(S1, H3, p), p);
    int64_t Z3 = mod_mul(H, mod_mul(jp1.Z, jp2.Z, p), p);

    JacobianPoint res = {X3, Y3, Z3, false};
    return res;
}

// ============================================================================
// Стиснення точок (Point Compression) та протокол ECDH
// ============================================================================

// Стиснення афінної точки у формат: префікс (0x02 парний y, 0x03 непарний y) + x
void point_compress(Point p, uint8_t* out_bytes) {
    if (p.is_infinity) {
        out_bytes[0] = 0x00;
        memset(out_bytes + 1, 0, 8);
        return;
    }
    out_bytes[0] = (p.y % 2 == 0) ? 0x02 : 0x03;
    for (int i = 0; i < 8; i++) {
        out_bytes[1 + i] = (uint8_t)((p.x >> (8 * (7 - i))) & 0xFF);
    }
}

// Відновлення афінної точки зі стисненого формату
bool point_decompress(const uint8_t* in_bytes, const EllipticCurve* curve, Point* out_p) {
    if (in_bytes[0] == 0x00) {
        *out_p = point_infinity();
        return true;
    }
    if (in_bytes[0] != 0x02 && in_bytes[0] != 0x03) {
        return false; // Некоректний префікс стиснення
    }

    int64_t x = 0;
    for (int i = 0; i < 8; i++) {
        x = (x << 8) | in_bytes[1 + i];
    }
    x = mod_pos(x, curve->p);

    // rhs = x^3 + a*x + b mod p
    int64_t rhs = mod_add(mod_add(mod_pow(x, 3, curve->p), mod_mul(curve->a, x, curve->p), curve->p), curve->b, curve->p);
    int64_t y = mod_sqrt(rhs, curve->p);

    if (y == -1) {
        return false; // Точка не належить кривій (rhs не є квадратичним лишком)
    }

    // Вибір парного чи непарного кореня відповідно до заголовного байта
    bool y_is_odd = (y % 2 != 0);
    bool want_odd = (in_bytes[0] == 0x03);
    if (y_is_odd != want_odd) {
        y = mod_pos(curve->p - y, curve->p);
    }

    *out_p = point_create(x, y);
    return true;
}

// Обчислення спільного таємного ключа ECDH: Secret = d_A * Q_B
bool ecdh_shared_secret(int64_t priv_key, Point pub_key, const EllipticCurve* curve, int64_t* out_secret_x) {
    if (!point_is_on_curve(pub_key, curve) || pub_key.is_infinity) {
        return false; // Захист від атаки на некоректні криві (Invalid Curve Attack)
    }
    Point shared = scalar_multiply(priv_key, pub_key, curve);
    if (shared.is_infinity) {
        return false;
    }
    *out_secret_x = shared.x;
    return true;
}

// ============================================================================
// Допоміжний друк та верифікація тестових векторів
// ============================================================================

static void print_point(const char* label, Point p) {
    if (p.is_infinity) {
        printf("%s: O (точка на нескінченності)\n", label);
    } else {
        printf("%s: (%lld, %lld)\n", label, (long long)p.x, (long long)p.y);
    }
}

int main(void) {
    // Тестова крива: y^2 = x^3 + 2*x + 3 (mod 97), порядок n = 5 для базової точки P = (3, 6)
    EllipticCurve curve = {2, 3, 97, 5};
    Point P = point_create(3, 6);

    printf("=== Тестування точкової арифметики на еліптичній кривій над F_97 ===\n");
    printf("Крива: y^2 = x^3 + %lld*x + %lld (mod %lld)\n", (long long)curve.a, (long long)curve.b, (long long)curve.p);
    print_point("Базова точка P", P);

    // 1. Перевірка належності точки кривій
    if (point_is_on_curve(P, &curve)) {
        printf("[OK] Базова точка P належить кривій.\n");
    } else {
        printf("[FAIL] Точка P не належить кривій!\n");
        return 1;
    }

    // 2. Послідовні операції подвоєння та додавання (контрольні вектори)
    Point P2 = point_double(P, &curve);
    print_point("2*P (подвоєння)", P2);

    Point P3 = point_add(P2, P, &curve);
    print_point("3*P (додавання P2 + P)", P3);

    Point P4 = point_double(P2, &curve);
    print_point("4*P (подвоєння 2*P)", P4);

    Point P5 = point_add(P4, P, &curve);
    print_point("5*P (додавання 4*P + P)", P5);

    // 3. Перевірка скалярного множення через Double-and-Add
    printf("\n=== Перевірка скалярного множення k*P (Double-and-Add) ===\n");
    for (int64_t k = 1; k <= 5; k++) {
        Point kP = scalar_multiply(k, P, &curve);
        char buf[32];
        snprintf(buf, sizeof(buf), "k = %lld: k*P", (long long)k);
        print_point(buf, kP);
    }

    // 4. Порівняння зі скалярним множенням Монтгомері
    printf("\n=== Перевірка скалярного множення Монтгомері (Constant-Time) ===\n");
    for (int64_t k = 1; k <= 5; k++) {
        Point kP_mont = scalar_multiply_montgomery(k, P, &curve);
        Point kP_std = scalar_multiply(k, P, &curve);
        if (!point_equals(kP_mont, kP_std)) {
            printf("[FAIL] Невідповідність для k = %lld\n", (long long)k);
        }
    }
    printf("[OK] Усі скалярні добутки Монтгомері співпали з Double-and-Add.\n");

    // 5. Перевірка проективних координат Якобі
    printf("\n=== Перевірка точкової арифметики в координатах Якобі ===\n");
    JacobianPoint JP = affine_to_jacobian(P);
    JacobianPoint JP2 = jacobian_double(JP, &curve);
    Point P2_jac = jacobian_to_affine(JP2, &curve);
    print_point("2*P через Якобі", P2_jac);

    JacobianPoint JP3 = jacobian_add(JP2, JP, &curve);
    Point P3_jac = jacobian_to_affine(JP3, &curve);
    print_point("3*P через Якобі", P3_jac);

    // 6. Перевірка стиснення та декомпресії точок
    printf("\n=== Перевірка стиснення та відновлення точок ===\n");
    uint8_t compressed[9];
    point_compress(P, compressed);
    printf("Стиснена точка P: префікс 0x%02X, x = %lld\n", compressed[0], (long long)P.x);

    Point decompressed;
    if (point_decompress(compressed, &curve, &decompressed)) {
        print_point("Відновлена точка", decompressed);
        if (point_equals(P, decompressed)) {
            printf("[OK] Відновлена точка ідентична вихідній P.\n");
        }
    }

    // 7. Демонстрація протоколу обміну ключами ECDH
    printf("\n=== Демонстрація протоколу обміну ключами ECDH ===\n");
    int64_t alice_priv = 2;
    Point alice_pub = scalar_multiply(alice_priv, P, &curve); // 2*P = (80, 10)

    int64_t bob_priv = 3;
    Point bob_pub = scalar_multiply(bob_priv, P, &curve); // 3*P = (80, 87)

    int64_t alice_shared_secret = 0;
    int64_t bob_shared_secret = 0;

    ecdh_shared_secret(alice_priv, bob_pub, &curve, &alice_shared_secret);
    ecdh_shared_secret(bob_priv, alice_pub, &curve, &bob_shared_secret);

    printf("Аліса: приватний d_A = %lld, публічний Q_A = (%lld, %lld)\n", (long long)alice_priv, (long long)alice_pub.x, (long long)alice_pub.y);
    printf("Боб:   приватний d_B = %lld, публічний Q_B = (%lld, %lld)\n", (long long)bob_priv, (long long)bob_pub.x, (long long)bob_pub.y);
    printf("Спільний секретний x-ключ Аліси: %lld\n", (long long)alice_shared_secret);
    printf("Спільний секретний x-ключ Боба:   %lld\n", (long long)bob_shared_secret);

    if (alice_shared_secret == bob_shared_secret) {
        printf("[OK] Обмін ключами ECDH виконано успішно! Секрети ідентичні.\n");
    }

    return 0;
}
