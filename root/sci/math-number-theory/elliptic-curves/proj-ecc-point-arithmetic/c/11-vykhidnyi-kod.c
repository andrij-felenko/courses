#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// Точка на еліптичній кривій y^2 = x^3 + a*x + b (mod p)
typedef struct {
    int64_t x;
    int64_t y;
    bool is_infinity; // true відповідає точці на нескінченності O
} Point;

// Корректне обчислення a mod p з гарантією додатності результату [0, p-1]
static int64_t mod_pos(int64_t a, int64_t p) {
    int64_t r = a % p;
    return r < 0 ? r + p : r;
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

    if (r > 1) return -1; // Элемент не має оберненого
    return mod_pos(t, p);
}

// Перевірка рівності двох точок
bool point_equals(Point p1, Point p2) {
    if (p1.is_infinity && p2.is_infinity) return true;
    if (p1.is_infinity || p2.is_infinity) return false;
    return p1.x == p2.x && p1.y == p2.y;
}

// Подвоєння точки: R = 2*P mod p
Point point_double(Point p1, int64_t a, int64_t p) {
    if (p1.is_infinity || p1.y == 0) {
        return (Point){0, 0, true};
    }

    // lambda = (3*x1^2 + a) * (2*y1)^-1 mod p
    int64_t num = mod_pos(3 * p1.x * p1.x + a, p);
    int64_t den = mod_pos(2 * p1.y, p);
    int64_t den_inv = mod_inverse(den, p);

    if (den_inv == -1) return (Point){0, 0, true};

    int64_t lambda = mod_pos(num * den_inv, p);

    // x3 = lambda^2 - 2*x1 mod p
    int64_t x3 = mod_pos(lambda * lambda - 2 * p1.x, p);
    // y3 = lambda*(x1 - x3) - y1 mod p
    int64_t y3 = mod_pos(lambda * (p1.x - x3) - p1.y, p);

    return (Point){x3, y3, false};
}

// Додавання двох точок: R = P + Q mod p
Point point_add(Point p1, Point p2, int64_t a, int64_t p) {
    if (p1.is_infinity) return p2;
    if (p2.is_infinity) return p1;

    // Якщо x1 == x2
    if (p1.x == p2.x) {
        if (mod_pos(p1.y + p2.y, p) == 0) {
            return (Point){0, 0, true}; // P + (-P) = O
        }
        return point_double(p1, a, p);
    }

    // lambda = (y2 - y1) * (x2 - x1)^-1 mod p
    int64_t num = mod_pos(p2.y - p1.y, p);
    int64_t den = mod_pos(p2.x - p1.x, p);
    int64_t den_inv = mod_inverse(den, p);

    if (den_inv == -1) return (Point){0, 0, true};

    int64_t lambda = mod_pos(num * den_inv, p);

    // x3 = lambda^2 - x1 - x2 mod p
    int64_t x3 = mod_pos(lambda * lambda - p1.x - p2.x, p);
    // y3 = lambda*(x1 - x3) - y1 mod p
    int64_t y3 = mod_pos(lambda * (p1.x - x3) - p1.y, p);

    return (Point){x3, y3, false};
}

// Скалярне множення R = k * P методом Double-and-Add (двійкова драбина)
Point scalar_multiply(int64_t k, Point p1, int64_t a, int64_t p) {
    Point result = {0, 0, true}; // O
    Point addend = p1;

    while (k > 0) {
        if (k & 1) {
            result = point_add(result, addend, a, p);
        }
        addend = point_double(addend, a, p);
        k >>= 1;
    }
    return result;
}

int main(void) {
    // Параметри кривої y^2 = x^3 + 2*x + 3 (mod 97)
    int64_t a = 2, b = 3, p = 97;

    // Базова точка P = (3, 6)
    Point P = {3, 6, false};

    printf("Початкова точка P: (%lld, %lld)\n", P.x, P.y);

    Point P2 = point_double(P, a, p);
    printf("2*P: (%lld, %lld)\n", P2.x, P2.y);

    Point P3 = point_add(P2, P, a, p);
    printf("3*P (додавання P2 + P): (%lld, %lld)\n", P3.x, P3.y);

    Point P5 = scalar_multiply(5, P, a, p);
    printf("5*P (скалярне множення): (%lld, %lld)\n", P5.x, P5.y);

    return 0;
}
