# ⚙️ Сферична лінійна інтерполяція орієнтацій SLERP

Плавна зміна просторової орієнтації між двома станами вимагає руху з постійною кутовою швидкістю навколо фіксованої осі. Звичайна лінійна інтерполяція кутів Ейлера чи компонентів матриць спотворює кутову швидкість і може призвести до заклинювання рамок, тоді як сферична лінійна інтерполяція одиничних кватерніонів (SLERP, *Spherical Linear Interpolation*) гарантує геодезичний рух уздовж великого кола 3-сфери S³.

### Чому наївні методи інтерполяції зазнають поразки

При розробці ігрових рушіїв, анімаційних систем, симуляторів та систем керування роботами постійно виникає задача побудови плавного переходу від початкової орієнтації `R₁` до цільової `R₂` за час `t ∈ [0, 1]`. Розглянемо, чому прості підходи призводять до візуальних або динамічних дефектів:

**1. Лінійна інтерполяція кутів Ейлера (LERP по кутах).**
Якщо ми просто змінюємо крен, тангаж і курс за лінійним законом `ψ(t) = (1-t)ψ₁ + tψ₂`, тіло рухається не навколо однієї фіксованої осі, а здійснює дивне хвилеподібне хитання (так званий ефект прецесії та нутації). Траєкторія руху залежить від обраного порядку осей (наприклад, XYZ чи ZYX). Що гірше: якщо на шляху трапиться конфігурація з тангажем 90°, алгоритм потрапляє в область карданного заклинювання (*gimbal lock*), де навіть нескінченно мале відхилення кута викликає миттєвий стрибок курсу на 180°.

**2. Покомпонентна інтерполяція матриць повороту.**
Якщо спробувати усереднити дві матриці як `R(t) = (1-t)·R₁ + t·R₂`, проміжна матриця `R(t)` перестає бути ортогональною. Її стовпчики втрачають одиничну довжину та перпендикулярність (`R(t)ᵀ·R(t) ≠ I`), а визначник `det(R(t))` зменшується. Під час анімації тривимірна модель спотворюється: сплющується, зменшується в об'ємі на середині шляху, а для повернення до SO(3) доводиться на кожному кадрі виконувати ресурсомістку процедуру Грама-Шмідта або сингулярний розклад (SVD).

**3. Нормалізована лінійна інтерполяція кватерніонів (NLERP).**
Якщо взяти два одиничні кватерніони `q₁` та `q₂` і скласти їх як вектори в ℝ⁴ з наступним нормуванням:

```
Nlerp(q₁, q₂, t) = Normalize( (1 - t)·q₁ + t·q₂ )
```

траєкторія пройде через одиничну сферу, проте швидкість руху вздовж сфери **не буде постійною**. На початку та наприкінці інтервалу кутова швидкість буде меншою, а всередині — більшою. Для анімації камер це створює помітне тремтіння прискорення.

### Геометрична ідея та виведення формули SLERP

Алгоритм SLERP, запропонований Кеном Шумейком (*Ken Shoemake*) у 1985 році на конференції SIGGRAPH, розв'язує задачу геометрично строго: він шукає дугу великого кола на одиничній сфері S³, що з'єднує дві точки `q₁` та `q₂`, і ділить кут між ними пропорційно до часу `t`.

Нехай задано два одиничні кватерніони `q₁` та `q₂`:

```
q₁ = (w₁, x₁, y₁, z₁),    q₂ = (w₂, x₂, y₂, z₂),    ||q₁|| = ||q₂|| = 1
```

Скалярний добуток чотиривимірних векторів у просторі ℝ⁴ визначає косинус кута `Ω` між ними:

```
cos(Ω) = q₁ · q₂ = w₁·w₂ + x₁·x₂ + y₁·y₂ + z₁·z₂
```

Будь-який вектор `q(t)` у площині, утвореній `q₁` та `q₂`, можна розкласти за базисом:

```
q(t) = a(t)·q₁ + b(t)·q₂
```

Вимога того, щоб довжина `||q(t)|| = 1` зберігалася для всіх `t`, а кут між `q₁` та `q(t)` дорівнював `t·Ω`, веде до стандартної тригонометричної системи на одиничному колі:

```
q₁ · q(t) = a(t) + b(t)·cos(Ω) = cos(t·Ω)
q₂ · q(t) = a(t)·cos(Ω) + b(t) = cos((1 - t)·Ω)
```

Розв'язуючи цю систему лінійних рівнянь відносно `a(t)` та `b(t)` за правилом Крамера:

```
det = 1 - cos²(Ω) = sin²(Ω)
a(t) = (cos(t·Ω) - cos((1 - t)·Ω)·cos(Ω)) / sin²(Ω) = sin((1 - t)·Ω) / sin(Ω)
b(t) = (cos((1 - t)·Ω) - cos(t·Ω)·cos(Ω)) / sin²(Ω) = sin(t·Ω) / sin(Ω)
```

Ми дістаємо класичну формулу SLERP:

```
Slerp(q₁, q₂, t) = (sin((1 - t)·Ω) / sin(Ω)) · q₁ + (sin(t·Ω) / sin(Ω)) · q₂
```

### Врахування топології подвійного покриття

Кватерніони `q` та `−q` відповідають **одній і тій самій фізичній орієнтації** в групі SO(3). Це створює важливу геометричну альтернативу: на сфері S³ між точками `q₁` та `q₂` є дві можливі дуги:
- коротка дуга з кутом `Ω ≤ π/2` (кут повороту тіла `θ ≤ 180°`);
- довга дуга через протилежний бік сфери з кутом `Ω > π/2` (поворот у зворотний бік на кут `360° - θ`).

Якщо скалярний добуток `q₁ · q₂ < 0`, це означає, що вектор `q₂` лежить у протилежній півсфері. Щоб інтерполяція обрала найкоротший шлях повороту, кватерніон `q₂` необхідно інвертувати:

```
q₂ ← -q₂
cos(Ω) ← -cos(Ω)
```

Це гарантує, що `cos(Ω) ≥ 0`, а фізичне тіло повернеться найкоротшим шляхом без зайвого оберту на 360°.

### Захист від ділення на нуль при малих кутах

Коли початковий і кінцевий кватерніони майже однакові (`q₁ ≈ q₂`), кут `Ω → 0`, а `sin(Ω) → 0`. Пряме обчислення дробу `sin(t·Ω)/sin(Ω)` призводить до невизначеності типу 0/0 та катастрофічної втрати точності чисел з плаваючою комою.

Тому при `cos(Ω) > 0.9995` (що відповідає куту `Ω < 1.8°`) алгоритм перемикається на нормалізовану лінійну інтерполяцію NLERP. При малих кутах похибка швидкості NLERP менша за `10⁻⁶`, що гарантує ідеальну гладкість та абсолютну числову стабільність.

### Реалізація алгоритму трьома мовами

Нижче наведено промислову реалізацію алгоритму SLERP мовами C, C++ та Python з повним захистом від крайових умов і вибором найкоротшої геодезичної дуги.

:::tabs
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double w, x, y, z;
} Quat;

Quat quat_normalize(Quat q) {
    double mag = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (mag < 1e-12) {
        Quat id = {1.0, 0.0, 0.0, 0.0};
        return id;
    }
    Quat res = {q.w / mag, q.x / mag, q.y / mag, q.z / mag};
    return res;
}

double quat_dot(Quat a, Quat b) {
    return a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z;
}

Quat quat_slerp(Quat q1, Quat q2, double t) {
    double dot = quat_dot(q1, q2);

    /* Вибір найкоротшого шляху на 3-сфері S3 */
    if (dot < 0.0) {
        dot = -dot;
        q2.w = -q2.w;
        q2.x = -q2.x;
        q2.y = -q2.y;
        q2.z = -q2.z;
    }

    /* Захист від похибок переповнення acos() через машинне округлення */
    if (dot > 1.0) {
        dot = 1.0;
    }

    /* Якщо кут майже нульовий, використовуємо стійку NLERP */
    if (dot > 0.9995) {
        Quat result = {
            q1.w + t * (q2.w - q1.w),
            q1.x + t * (q2.x - q1.x),
            q1.y + t * (q2.y - q1.y),
            q1.z + t * (q2.z - q1.z)
        };
        return quat_normalize(result);
    }

    /* Класична формула SLERP */
    double omega = acos(dot);
    double sin_omega = sin(omega);
    double scale1 = sin((1.0 - t) * omega) / sin_omega;
    double scale2 = sin(t * omega) / sin_omega;

    Quat result = {
        scale1 * q1.w + scale2 * q2.w,
        scale1 * q1.x + scale2 * q2.x,
        scale1 * q1.y + scale2 * q2.y,
        scale1 * q1.z + scale2 * q2.z
    };
    return result;
}

int main(void) {
    /* Початкова орієнтація: без повороту (I) */
    Quat q1 = {1.0, 0.0, 0.0, 0.0};
    /* Кінцева орієнтація: поворот на 90° навколо осі Z */
    Quat q2 = {cos(M_PI / 4.0), 0.0, 0.0, sin(M_PI / 4.0)};

    printf("Кроки інтерполяції SLERP (C):\n");
    for (int i = 0; i <= 4; ++i) {
        double t = i * 0.25;
        Quat qt = quat_slerp(q1, q2, t);
        printf("t = %.2f -> (w: %.4f, x: %.4f, y: %.4f, z: %.4f)\n",
               t, qt.w, qt.x, qt.y, qt.z);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>

struct Quaternion {
    double w{1.0};
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] double dot(const Quaternion& other) const noexcept {
        return w * other.w + x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(w * w + x * x + y * y + z * z);
    }

    [[nodiscard]] Quaternion normalized() const noexcept {
        const double mag = norm();
        if (mag < 1e-12) {
            return Quaternion{1.0, 0.0, 0.0, 0.0};
        }
        return Quaternion{w / mag, x / mag, y / mag, z / mag};
    }

    [[nodiscard]] static Quaternion slerp(const Quaternion& q1, Quaternion q2, double t) noexcept {
        double cos_omega = q1.dot(q2);

        // Якщо скалярний добуток від'ємний, інвертуємо цільовий кватерніон
        // для вибору найкоротшої геодезичної дуги (< 180 градусів)
        if (cos_omega < 0.0) {
            cos_omega = -cos_omega;
            q2.w = -q2.w;
            q2.x = -q2.x;
            q2.y = -q2.y;
            q2.z = -q2.z;
        }

        cos_omega = std::clamp(cos_omega, -1.0, 1.0);

        // Область близькості: заміна на NLERP заради числової стабільності
        if (cos_omega > 0.9995) {
            Quaternion res{
                q1.w + t * (q2.w - q1.w),
                q1.x + t * (q2.x - q1.x),
                q1.y + t * (q2.y - q1.y),
                q1.z + t * (q2.z - q1.z)
            };
            return res.normalized();
        }

        const double omega = std::acos(cos_omega);
        const double sin_omega = std::sin(omega);
        const double scale1 = std::sin((1.0 - t) * omega) / sin_omega;
        const double scale2 = std::sin(t * omega) / sin_omega;

        return Quaternion{
            scale1 * q1.w + scale2 * q2.w,
            scale1 * q1.x + scale2 * q2.x,
            scale1 * q1.y + scale2 * q2.y,
            scale1 * q1.z + scale2 * q2.z
        };
    }
};

int main() {
    // Поворот від 0° до 90° навколо осі Z
    const Quaternion q_start{1.0, 0.0, 0.0, 0.0};
    const double angle = std::numbers::pi / 4.0;
    const Quaternion q_end{std::cos(angle), 0.0, 0.0, std::sin(angle)};

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Інтерполяція орієнтації C++:\n";

    for (int step = 0; step <= 4; ++step) {
        const double t = step * 0.25;
        const Quaternion q_interp = Quaternion::slerp(q_start, q_end, t);
        std::cout << "t = " << t << " -> (w: " << q_interp.w
                  << ", x: " << q_interp.x
                  << ", y: " << q_interp.y
                  << ", z: " << q_interp.z << ")\n";
    }
    return 0;
}
```
```python
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Quaternion:
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def dot(self, other: "Quaternion") -> float:
        return self.w * other.w + self.x * other.x + self.y * other.y + self.z * other.z

    def norm(self) -> float:
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalized(self) -> "Quaternion":
        mag = self.norm()
        if mag < 1e-12:
            return Quaternion(1.0, 0.0, 0.0, 0.0)
        return Quaternion(self.w / mag, self.x / mag, self.y / mag, self.z / mag)

    @staticmethod
    def slerp(q1: "Quaternion", q2: "Quaternion", t: float) -> "Quaternion":
        dot = q1.dot(q2)

        # Вибір найкоротшого шляху на 3-сфері S3
        if dot < 0.0:
            dot = -dot
            q2 = Quaternion(-q2.w, -q2.x, -q2.y, -q2.z)

        # Захист від похибок заокруглення floating point
        dot = max(-1.0, min(1.0, dot))

        # Захист від ділення на нуль при малих кутах
        if dot > 0.9995:
            res = Quaternion(
                q1.w + t * (q2.w - q1.w),
                q1.x + t * (q2.x - q1.x),
                q1.y + t * (q2.y - q1.y),
                q1.z + t * (q2.z - q1.z)
            )
            return res.normalized()

        omega = math.acos(dot)
        sin_omega = math.sin(omega)
        scale1 = math.sin((1.0 - t) * omega) / sin_omega
        scale2 = math.sin(t * omega) / sin_omega

        return Quaternion(
            scale1 * q1.w + scale2 * q2.w,
            scale1 * q1.x + scale2 * q2.x,
            scale1 * q1.y + scale2 * q2.y,
            scale1 * q1.z + scale2 * q2.z
        )

if __name__ == "__main__":
    q_start = Quaternion(1.0, 0.0, 0.0, 0.0)
    theta_half = math.pi / 4.0
    q_end = Quaternion(math.cos(theta_half), 0.0, 0.0, math.sin(theta_half))

    print("Інтерполяція орієнтацій Python:")
    for step in range(5):
        t_val = step * 0.25
        qt = Quaternion.slerp(q_start, q_end, t_val)
        print(f"t = {t_val:.2f} -> (w: {qt.w:.4f}, x: {qt.x:.4f}, y: {qt.y:.4f}, z: {qt.z:.4f})")
```
:::

### Типові пастки реалізації

1. **Ігнорування антиподального знаку (`dot < 0`).** Без перевірки знаку скалярного добутку інтерполяція між двома близькими фізичними станами `q₁ = (1, 0, 0, 0)` та `q₂ = (-0.999, 0, 0, 0.04)` здійснить оберт на 358° через усю сферу замість прямого повороту на 2°.
2. **Ділення на нуль при збігу орієнтацій.** Коли `q₁ = q₂`, кут `Ω = 0`, і `sin(Ω) = 0`. Поріг `dot > 0.9995` гарантує математичну стійкість та відсутність `NaN` у розрахунках.
3. **Вихід за межі діапазону `[-1, 1]` для функції `acos`.** Через похибки округлення скалярний добуток двох одиничних кватерніонів може стати `1.0000000000000002`. Без виклику `std::clamp` функція `acos` поверне `NaN`.
4. **Накопичення похибок округлення.** При багаторазовому застосуванні інтерполяції чи обчисленні кутової швидкості нормування `normalized()` повертає кватерніон точно на многовид одиничної сфери S³.
