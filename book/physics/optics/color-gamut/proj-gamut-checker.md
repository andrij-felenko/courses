# ⚙️ Алгоритм перевірки та компресії колірного охоплення (Gamut Checker)

У графічних рушіях, процесорах обробки зображень (ISP), драйверах дисплеїв, камерах високої чіткості та системах кольороподілу для поліграфії постійно виникає практична задача: визначити, чи належить вхідний колір із заданими тристимулами `XYZ` або хроматичністю `(x, y)` колірному охопленню конкретного пристрою, і якщо ні — виконувати коректне стискання чи обмеження (Gamut Mapping).

Математична модель та алгоритми Gamut Checker поєднують векторну геометрію перевірки належності точки 2D-трикутнику хроматичностей, лінійні матричні перетворення між колірними просторами та стратегії компресії кольорів поза охопленням з оцінкою обчислювальної складності й продуктивності реалізації.

## 1. Архітектура та етапи алгоритму Gamut Checker

При зйомці чи рендерингу сцени джерела випромінювання (наприклад, насичений лазерний промінь, спалах неонової вивіски чи спектральне відображення вогню) можуть формувати хроматичності, які виходять далеко за межі трикутника sRGB або навіть DCI-P3. При спробі прямого виводу таких сигналів без попередньої обробки дисплей створює атефакти: зливаються дрібні деталі градієнтів, а кольори спотворюють свій природний відтінок.

Процес перевірки та адаптації вхідного кольору складається з п'яти послідовних кроків:

1. **Дегамація вхідних даних (Linearization)**: якщо вхідні RGB-координати отримано з стисненого файлу чи камери, до них застосовують зворотну нелінійну функцію декодування (EOTF). Усі колориметричні обчислення й матричні перетворення виконуються **виключно у лінійному просторі**.
2. **Перетворення тристимулів у лінійні координати первинних кольорів целевого пристрою**: за допомогою оберненої матриці системи `M⁻¹` обчислюємо `(R, G, B) = M⁻¹ · (X, Y, Z)ᵀ`.
3. **Перевірка досяжності в 3D (Range Boundaries Check)**: якщо всі три розраховані значення задовольняють нерівність `0.0 ≤ R ≤ 1.0`, `0.0 ≤ G ≤ 1.0`, `0.0 ≤ B ≤ 1.0`, колір є фізично досяжним для даного дисплея.
4. **Геометрична перевірка в 2D (Barycentric Point-in-Triangle Test)**: перевірка належності точки `(x, y)` трикутнику опорних хроматичностей `RGB` за допомогою векторного добутку (метод знаків орієнтованої площі).
5. **Адаптація та компресія кольорів поза охопленням (Gamut Mapping Strategy)**:
   - **Жорсткий кліпінг (Hard Clipping / Absolute Colorimetric)**: обрізання значень `R = max(0, min(1, R))`. Працює миттєво, але викликає кліпінг деталей у насичених областях та помітну зміну кольорового тону.
   - **Відносний колориметричний (Relative Colorimetric)**: масштабування з урахуванням точки білого пристрою без відтинання внутрішніх відтінків.
   - **Перцептивна компресія (Perceptual Desaturation)**: радіальне стискання точки на площині хроматичностей у напрямку до точкового білого джерела `D65` до перетину з найближчим межевим ребром трикутника.

## 2. Математика точкової перевірки в трикутнику та алгоритми перетину

Щоб визначити, чи лежить точка `P(x, y)` усередині трикутника з вершинами `R(x_r, y_r)`, `G(x_g, y_g)`, `B(x_b, y_b)`, використовують псевдоскалярний (векторний) добуток 2D-векторів на площині.

Для кожного з трьох напрямлених ребер трикутника `RG`, `GB`, `BR` обчислюють орієнтовану площу:

```
D(P, A, B) = (B_x - A_x) · (P_y - A_y) - (B_y - A_y) · (P_x - A_x)
```

Точка `P` лежить усередині або на межі трикутника тоді й лише тоді, коли всі три величини `D(P, R, G)`, `D(P, G, B)` та `D(P, B, R)` мають однаковий знак (усі `≥ 0` або всі `≤ 0`). Наявність знаків із протилежною орієнтацією свідчить про те, що точка лежить ззовні трикутника.

Для алгоритму перцептивної компресії виконують ітераційний бінарний пошук (Binary Search) на відрізку між точкою `P(x, y)` та точкою білого `W(x_w, y_w)` або обчислюють точний алгебраїчний перетин променя `WP` з відрізком ребра трикутника.

## 3. Робочі програмні реалізації (Python, C, C++)

Нижче подано повні реалізації алгоритму перевірки та компресії трьома мовами програмування.

### 3.1. Структура коду та інтерфейс

Кожна реалізація містить:
- Структуру або клас `Vector3` для збереження векторів `XYZ` та `RGB`.
- Матрицю перетворення `M_INV_SRGB` розміром 3×3 для точної конвертації з XYZ у лінійні координати sRGB.
- Метод `is_in_gamut` для перевірки належності кольору досяжному діапазону `[0, 1]`.
- Метод `clip_to_gamut` для захищеного відтинання виходів за межі.

:::tabs
```py
# Python: реалізація Gamut Checker та компресії кольору

class Vector3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

class GamutChecker:
    # Обернена матриця sRGB D65
    M_INV_SRGB = [
        [ 3.2404542, -1.5371385, -0.4985314],
        [-0.9692660,  1.8760108,  0.0415560],
        [ 0.0556434, -0.2040259,  1.0572252]
    ]

    def __init__(self, r_xy=(0.64, 0.33), g_xy=(0.30, 0.60), b_xy=(0.15, 0.06), w_xy=(0.3127, 0.3290)):
        self.r = r_xy
        self.g = g_xy
        self.b = b_xy
        self.w = w_xy

    @staticmethod
    def xyz_to_srgb(xyz: Vector3) -> Vector3:
        """Перетворення XYZ у лінійні sRGB."""
        m = GamutChecker.M_INV_SRGB
        r = m[0][0]*xyz.x + m[0][1]*xyz.y + m[0][2]*xyz.z
        g = m[1][0]*xyz.x + m[1][1]*xyz.y + m[1][2]*xyz.z
        b = m[2][0]*xyz.x + m[2][1]*xyz.y + m[2][2]*xyz.z
        return Vector3(r, g, b)

    def is_in_gamut(self, xyz: Vector3) -> bool:
        """Перевірка, чи належить колір sRGB охопленню."""
        rgb = self.xyz_to_srgb(xyz)
        eps = 1e-6
        return (-eps <= rgb.x <= 1.0 + eps and
                -eps <= rgb.y <= 1.0 + eps and
                -eps <= rgb.z <= 1.0 + eps)

    def clip_to_gamut(self, xyz: Vector3) -> Vector3:
        """Жорсткий кліпінг лінійних RGB значений."""
        rgb = self.xyz_to_srgb(xyz)
        clamped_r = max(0.0, min(1.0, rgb.x))
        clamped_g = max(0.0, min(1.0, rgb.y))
        clamped_b = max(0.0, min(1.0, rgb.z))
        return Vector3(clamped_r, clamped_g, clamped_b)

    def compress_desaturate(self, xy: tuple[float, float], steps: int = 50) -> tuple[float, float]:
        """Перцептивний зсув до білої точки D65 до потрапляння всередину трикутника."""
        px, py = xy
        wx, wy = self.w
        
        def cross_product(p1, p2, p3):
            return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

        def in_triangle(pt):
            d1 = cross_product(pt, self.r, self.g)
            d2 = cross_product(pt, self.g, self.b)
            d3 = cross_product(pt, self.b, self.r)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            return not (has_neg and has_pos)

        if in_triangle((px, py)):
            return (px, py)

        low, high = 0.0, 1.0
        best_x, best_y = wx, wy
        for _ in range(steps):
            t = (low + high) / 2.0
            cur_x = px * (1.0 - t) + wx * t
            cur_y = py * (1.0 - t) + wy * t
            if in_triangle((cur_x, cur_y)):
                best_x, best_y = cur_x, cur_y
                high = t
            else:
                low = t

        return (best_x, best_y)

if __name__ == "__main__":
    checker = GamutChecker()
    laser_xyz = Vector3(0.14, 0.03, 0.85)
    print("Належить sRGB:", checker.is_in_gamut(laser_xyz))
    clipped = checker.clip_to_gamut(laser_xyz)
    print(f"Clipped RGB: ({clipped.x:.3f}, {clipped.y:.3f}, {clipped.z:.3f})")
```
```c
/* C99: Перевірка та кліпінг колірного охоплення sRGB */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

typedef struct {
    double x;
    double y;
} Point2D;

static const double M_INV_SRGB[3][3] = {
    { 3.2404542, -1.5371385, -0.4985314},
    {-0.9692660,  1.8760108,  0.0415560},
    { 0.0556434, -0.2040259,  1.0572252}
};

Vector3 xyz_to_srgb(Vector3 xyz) {
    Vector3 rgb;
    rgb.x = M_INV_SRGB[0][0]*xyz.x + M_INV_SRGB[0][1]*xyz.y + M_INV_SRGB[0][2]*xyz.z;
    rgb.y = M_INV_SRGB[1][0]*xyz.x + M_INV_SRGB[1][1]*xyz.y + M_INV_SRGB[1][2]*xyz.z;
    rgb.z = M_INV_SRGB[2][0]*xyz.x + M_INV_SRGB[2][1]*xyz.y + M_INV_SRGB[2][2]*xyz.z;
    return rgb;
}

bool is_in_srgb_gamut(Vector3 xyz) {
    Vector3 rgb = xyz_to_srgb(xyz);
    const double eps = 1e-6;
    return (rgb.x >= -eps && rgb.x <= 1.0 + eps &&
            rgb.y >= -eps && rgb.y <= 1.0 + eps &&
            rgb.z >= -eps && rgb.z <= 1.0 + eps);
}

Vector3 clip_srgb_gamut(Vector3 xyz) {
    Vector3 rgb = xyz_to_srgb(xyz);
    Vector3 out;
    out.x = (rgb.x < 0.0) ? 0.0 : ((rgb.x > 1.0) ? 1.0 : rgb.x);
    out.y = (rgb.y < 0.0) ? 0.0 : ((rgb.y > 1.0) ? 1.0 : rgb.y);
    out.z = (rgb.z < 0.0) ? 0.0 : ((rgb.z > 1.0) ? 1.0 : rgb.z);
    return out;
}

int main(void) {
    Vector3 test_xyz = {0.14, 0.03, 0.85};
    bool valid = is_in_srgb_gamut(test_xyz);
    printf("Is in sRGB gamut: %s\n", valid ? "YES" : "NO");

    Vector3 clipped = clip_srgb_gamut(test_xyz);
    printf("Clipped RGB: [%.4f, %.4f, %.4f]\n", clipped.x, clipped.y, clipped.z);
    return 0;
}
```
```cpp
// C++20: Ідіоматичний Gamut Checker з використанням std::array, RAII та std::clamp
#include <iostream>
#include <array>
#include <algorithm>
#include <cmath>

namespace color {

struct Tristimulus {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct Chromaticity {
    double x{0.0};
    double y{0.0};
};

class ColorGamut {
public:
    using Matrix3x3 = std::array<std::array<double, 3>, 3>;

    static constexpr Matrix3x3 sRGB_Inverse_Matrix = {{
        {{ 3.2404542, -1.5371385, -0.4985314}},
        {{-0.9692660,  1.8760108,  0.0415560}},
        {{ 0.0556434, -0.2040259,  1.0572252}}
    }};

    explicit constexpr ColorGamut(
        Chromaticity r = {0.64, 0.33},
        Chromaticity g = {0.30, 0.60},
        Chromaticity b = {0.15, 0.06},
        Chromaticity w = {0.3127, 0.3290})
        : primary_r_(r), primary_g_(g), primary_b_(b), white_point_(w) {}

    [[nodiscard]] static constexpr Tristimulus to_linear_rgb(const Tristimulus& xyz) noexcept {
        const auto& m = sRGB_Inverse_Matrix;
        return Tristimulus{
            m[0][0]*xyz.x + m[0][1]*xyz.y + m[0][2]*xyz.z,
            m[1][0]*xyz.x + m[1][1]*xyz.y + m[1][2]*xyz.z,
            m[2][0]*xyz.x + m[2][1]*xyz.y + m[2][2]*xyz.z
        };
    }

    [[nodiscard]] static constexpr bool contains(const Tristimulus& xyz, double tolerance = 1e-6) noexcept {
        const auto rgb = to_linear_rgb(xyz);
        return (rgb.x >= -tolerance && rgb.x <= 1.0 + tolerance) &&
               (rgb.y >= -tolerance && rgb.y <= 1.0 + tolerance) &&
               (rgb.z >= -tolerance && rgb.z <= 1.0 + tolerance);
    }

    [[nodiscard]] static constexpr Tristimulus clip(const Tristimulus& xyz) noexcept {
        const auto rgb = to_linear_rgb(xyz);
        return Tristimulus{
            std::clamp(rgb.x, 0.0, 1.0),
            std::clamp(rgb.y, 0.0, 1.0),
            std::clamp(rgb.z, 0.0, 1.0)
        };
    }

private:
    Chromaticity primary_r_;
    Chromaticity primary_g_;
    Chromaticity primary_b_;
    Chromaticity white_point_;
};

} // namespace color

int main() {
    constexpr color::Tristimulus laser_light{0.14, 0.03, 0.85};
    constexpr bool in_gamut = color::ColorGamut::contains(laser_light);
    
    std::cout << "Contains in sRGB gamut: " << (in_gamut ? "true" : "false") << '\n';

    constexpr auto clipped = color::ColorGamut::clip(laser_light);
    std::cout << "Clipped Linear RGB: [" 
              << clipped.x << ", " 
              << clipped.y << ", " 
              << clipped.z << "]\n";
    return 0;
}
```
:::

## 4. Оптимізація продуктивності та розширений аналіз пасток

У системах рендерингу реального часу (ігрові рушії, відеопроцесори 4K/8K, фрагментні шейдери) обчислення матричного множення для кожного пікселя окремо є занадто ресурсоємним.

Для прискорення застосовують такі інженерні підходи:

1. **Векторизація SIMD (AVX2 / ARM NEON)**: обробка чотирьох або восьми пікселів одночасно у форматі `float32x4` за один інструкційний крок.
2. **Тривимірні текстури та 3D LUT (Look-Up Tables)**: координати `XYZ` або `RGB` масштабують у сітку 3D-текстури розміром `33×33×33` або `65×65×65` вузлів. Значення вибірки обчислюють апаратним інтерполятором GPU за допомогою трилінійної фільтрації.
3. **Обробка крайових випадків біля нуля (`Y → 0`)**: у ділянці глибоких тіней ділення на мале значення `y` може спричиняти ділення на нуль та появу `NaN` / `Inf`. Для запобігання цього в шейдерах вводять пороговий затиск `y = max(y, 1e-5)`.
4. **Профілі ICC (International Color Consortium)**: у професійних системах перетворення спирається на теги `rXYZ`, `gXYZ`, `bXYZ` та таблиці `A2B0`/`B2A0`, збережені в ICC-файлі конкретного залікового пристрою.

При реалізації систем обробки відеопотоків важливо враховувати розрядність (8 біт vs 10 біт vs 12 біт). У 8-бітних каналах навіть невеликі похибки кліпінгу створюють видимий бандинг (східчасті градієнти), тому стискання колірного охоплення рекомендовано виконувати у 16-бітному форматі з плаваючою комою перед кінцевим квантуванням.

В оптичних спектрометрах та системах технічного зору додатково перевіряють похибку освітленості сцен. Якщо освітлювальний прилад має нелінійний спектр (наприклад, дешева люмінесцентна лампа), то перетворення кольорів через стандартну матрицю sRGB створює неусувні відхилення колірного тону, які неможливо поправити жодним кліпінгом без адаптації точки білого.
