# ⚙️ Алгоритм та реалізація рушія колірних перетворень і обчислення ΔE

Обчислювальний рушій колірних перетворень є основою будь-якої системи обробки графіки, растрового рендерингу та комп'ютерного зору. Його головне завдання — перетворити гамма-кореговані пікселі з апаратно-залежного простору `sRGB` у рівномірно-перцептивний простір `Oklab` та обчислити відносну зорову відмінність `ΔE_OK` без втрати обчислювальної продуктивності.

У цьому розділі розглядається повна архітектура алгоритму, його реалізація мовами C та C++, а також методи прискорення та оптимізації пам'яті для потокової обробки графічних масивів.

## 1. Архітектура та послідовність обчислювального конвеєра

Математичний конвеєр перетворення одного пікселя складається з чотирьох послідовних етапів. Кожен етап розв'язує окрему фізико-математичну задачу:

### Етап 1: Нормування та гамма-декомпандування (Лінеаризація)
Вхідний піксель зображення зазвичай подається у форматі 8-бітних цілих беззнакових чисел для кожного з трьох каналів `(R_8bit, G_8bit, B_8bit) ∈ [0 .. 255]`. Ці значення не пропорційні фізичній інтенсивності випромінювання через застосовану гамма-корекцію з показником `γ ≈ 2.2`.

На першому кроці кожне значення ділиться на `255.0` для переходу у діапазон `[0.0 .. 1.0]`, після чого виконується зворотне нелінійне електрооптичне перетворення (EOTF):

```
C_srgb = C_8bit / 255.0

C_linear = C_srgb / 12.92                        [якщо C_srgb ≤ 0.04045]
C_linear = ((C_srgb + 0.055) / 1.055)^2.4       [якщо C_srgb > 0.04045]
```

Ніжка формули при `C_srgb ≤ 0.04045` реалізує лінійну ділянку біля абсолютного чорного кольору. Вона запобігає появі нескінченної похідної у точці нуля при обчисленні відносних світлостей і зменшує шум у глибоких тінях.

### Етап 2: Проектування на тристимульний базис CIE XYZ 1931
Отриманий тривимірний вектор `(R_linear, G_linear, B_linear)` множиться на матрицю `M_sRGB_to_XYZ`. Ця матриця пов'язує первинні випромінювачі монітора sRGB із фотометричними координатами стандартного спостерігача CIE 1931 при опорному білому освітленні `D65` (`6504 K`):

```
[ X ]   [ 0.4124564  0.3575761  0.1804375 ]   [ R_linear ]
[ Y ] = [ 0.2126729  0.7151522  0.0721750 ] · [ G_linear ]
[ Z ]   [ 0.0193339  0.1191920  0.9503041 ]   [ B_linear ]
```

Результатом цього кроку є апаратно-незалежні координати `X`, `Y`, `Z`. Зверніть увагу, що друга рядок матриці обчислює координату `Y` з коефіцієнтами `(0.2126729, 0.7151522, 0.0721750)`. Ці коефіцієнти чітко відображають асиметрію зору: зелений колір забезпечує 71.5% сприйнятої фотометричної яскравості, червоний — 21.3%, а синій — лише 7.2%.

### Етап 3: Рецепторний перехід у простір Oklab
Простір Oklab моделює реакцію фоторецепторів сітківки. Вектор `(X, Y, Z)` спочатку переводиться у внутрішній простір довгохвильових, середньохвильових та короткохвильових колбочок `(L_cone, M_cone, S_cone)` за допомогою матриці `M₁`:

```
[ L_cone ]   [  0.8189330101  0.3618667424 -0.1288597137 ]   [ X ]
[ M_cone ] = [  0.0329845436  0.9293118715  0.0361456387 ] · [ Y ]
[ S_cone ]   [  0.0482003018  0.2643662691  0.6338517070 ]   [ Z ]
```

Після цього до кожного рецепторного сигналу застосовується кубічне стискання `l′ = ∛(L_cone)`, `m′ = ∛(M_cone)`, `s′ = ∛(S_cone)`. Ця нелінійність відображає стискання динамічного діапазону в біохімічному каскаді фототрансдукції.

Нарешті, нелінійні сигнали множаться на ортогональну матрицю `M₂`, утворюючи оппонентні координати `(L, a, b)`:

```
[ L ]   [  0.2104542553  0.7936177850 -0.0040720468 ]   [ l′ ]
[ a ] = [  1.9779984951 -2.4285922050  0.4505937099 ] · [ m′ ]
[ b ]   [  0.0259040371  0.7827717662 -0.8086758033 ] · [ s′ ]
```

### Етап 4: Обчислення метрики відмінності ΔE_OK
Оскільки простір Oklab є рівномірно-перцептивним, зорова відмінність `ΔE_OK` між двома колірними векторами `C₁ = (L₁, a₁, b₁)` та `C₂ = (L₂, a₂, b₂)` обчислюється як звичайна евклідова відстань у тривимірному просторі:

```
ΔE_OK = √[ (L₁ - L₂)² + (a₁ - a₂)² + (b₁ - b₂)² ]
```

Значення `ΔE_OK ≈ 0.02` виражає межу нерозрізненності (1 JND). Якщо обчислена відстань менша за `0.02`, людина сприймає ці кольори як ідентичні.

## 2. Реалізація колірного рушія

:::tabs
```c
/* color_engine.c - Ідіоматична реалізація мовою C (C99) */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    unsigned char r;
    unsigned char g;
    unsigned char b;
} RGB8;

typedef struct {
    float r;
    float g;
    float b;
} RGBLinear;

typedef struct {
    float x;
    float y;
    float z;
} XYZ;

typedef struct {
    float l;
    float a;
    float b;
} Oklab;

typedef struct {
    float l;
    float c;
    float h; /* у градусах [0..360] */
} Oklch;

/* Лінеаризація одного каналу sRGB */
static float srgb_to_linear(unsigned char val) {
    float c = (float)val / 255.0f;
    if (c <= 0.04045f) {
        return c / 12.92f;
    }
    return powf((c + 0.055f) / 1.055f, 2.4f);
}

/* Перетворення sRGB (8-bit) у sRGB Linear */
RGBLinear rgb8_to_linear(RGB8 color) {
    RGBLinear lin;
    lin.r = srgb_to_linear(color.r);
    lin.g = srgb_to_linear(color.g);
    lin.b = srgb_to_linear(color.b);
    return lin;
}

/* Перетворення sRGB Linear у CIE XYZ (D65) */
XYZ linear_to_xyz(RGBLinear lin) {
    XYZ xyz;
    xyz.x = 0.4124564f * lin.r + 0.3575761f * lin.g + 0.1804375f * lin.b;
    xyz.y = 0.2126729f * lin.r + 0.7151522f * lin.g + 0.0721750f * lin.b;
    xyz.z = 0.0193339f * lin.r + 0.1191920f * lin.g + 0.9503041f * lin.b;
    return xyz;
}

/* Перетворення CIE XYZ у Oklab */
Oklab xyz_to_oklab(XYZ xyz) {
    /* Крок 1: Перехід у простір LMS */
    float l_c = 0.8189330101f * xyz.x + 0.3618667424f * xyz.y - 0.1288597137f * xyz.z;
    float m_c = 0.0329845436f * xyz.x + 0.9293118715f * xyz.y + 0.0361456387f * xyz.z;
    float s_c = 0.0482003018f * xyz.x + 0.2643662691f * xyz.y + 0.6338517070f * xyz.z;

    /* Крок 2: Нелінійність (кубічний корінь) */
    float l_p = cbrtf(l_c);
    float m_p = cbrtf(m_c);
    float s_p = cbrtf(s_c);

    /* Крок 3: Перехід у Oklab */
    Oklab lab;
    lab.l = 0.2104542553f * l_p + 0.7936177850f * m_p - 0.0040720468f * s_p;
    lab.a = 1.9779984951f * l_p - 2.4285922050f * m_p + 0.4505937099f * s_p;
    lab.b = 0.0259040371f * l_p + 0.7827717662f * m_p - 0.8086758033f * s_p;
    return lab;
}

/* Перетворення sRGB8 безпосередньо у Oklab */
Oklab rgb8_to_oklab(RGB8 color) {
    RGBLinear lin = rgb8_to_linear(color);
    XYZ xyz = linear_to_xyz(lin);
    return xyz_to_oklab(xyz);
}

/* Перетворення Oklab у полярні координати Oklch */
Oklch oklab_to_oklch(Oklab lab) {
    Oklch lch;
    lch.l = lab.l;
    lch.c = sqrtf(lab.a * lab.a + lab.b * lab.b);
    float h_rad = atan2f(lab.b, lab.a);
    float h_deg = h_rad * (180.0f / (float)M_PI);
    if (h_deg < 0.0f) {
        h_deg += 360.0f;
    }
    lch.h = h_deg;
    return lch;
}

/* Обчислення евклідової відмінності ΔE_OK */
float delta_e_ok(Oklab c1, Oklab c2) {
    float dl = c1.l - c2.l;
    float da = c1.a - c2.a;
    float db = c1.b - c2.b;
    return sqrtf(dl * dl + da * da + db * db);
}

int main(void) {
    RGB8 color1 = {255, 0, 0};   /* Червоний */
    RGB8 color2 = {200, 20, 10}; /* Темно-червоний */

    Oklab lab1 = rgb8_to_oklab(color1);
    Oklab lab2 = rgb8_to_oklab(color2);

    float de = delta_e_ok(lab1, lab2);
    printf("Oklab Color 1: L=%.4f, a=%.4f, b=%.4f\n", lab1.l, lab1.a, lab1.b);
    printf("Oklab Color 2: L=%.4f, a=%.4f, b=%.4f\n", lab2.l, lab2.a, lab2.b);
    printf("Delta E_OK = %.4f (Поріг сприйняття ~0.02)\n", de);

    return 0;
}
```
```cpp
// color_engine.cpp - Ідіоматична реалізація мовою C++ (C++20)
#include <iostream>
#include <cmath>
#include <numbers>
#include <array>
#include <span>

namespace color {

struct RGB8 {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};
};

struct RGBLinear {
    float r{0.0f};
    float g{0.0f};
    float b{0.0f};
};

struct XYZ {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Oklab {
    float l{0.0f};
    float a{0.0f};
    float b{0.0f};
};

struct Oklch {
    float l{0.0f};
    float c{0.0f};
    float h{0.0f}; // у градусах [0..360]
};

class ColorConverter {
public:
    [[nodiscard]] static constexpr float srgb_to_linear(uint8_t val) noexcept {
        const float c = static_cast<float>(val) / 255.0f;
        if (c <= 0.04045f) {
            return c / 12.92f;
        }
        return std::pow((c + 0.055f) / 1.055f, 2.4f);
    }

    [[nodiscard]] static RGBLinear to_linear(RGB8 color) noexcept {
        return RGBLinear{
            .r = srgb_to_linear(color.r),
            .g = srgb_to_linear(color.g),
            .b = srgb_to_linear(color.b)
        };
    }

    [[nodiscard]] static XYZ to_xyz(RGBLinear lin) noexcept {
        return XYZ{
            .x = 0.4124564f * lin.r + 0.3575761f * lin.g + 0.1804375f * lin.b,
            .y = 0.2126729f * lin.r + 0.7151522f * lin.g + 0.0721750f * lin.b,
            .z = 0.0193339f * lin.r + 0.1191920f * lin.g + 0.9503041f * lin.b
        };
    }

    [[nodiscard]] static Oklab xyz_to_oklab(XYZ xyz) noexcept {
        const float l_c = 0.8189330101f * xyz.x + 0.3618667424f * xyz.y - 0.1288597137f * xyz.z;
        const float m_c = 0.0329845436f * xyz.x + 0.9293118715f * xyz.y + 0.0361456387f * xyz.z;
        const float s_c = 0.0482003018f * xyz.x + 0.2643662691f * xyz.y + 0.6338517070f * xyz.z;

        const float l_p = std::cbrt(l_c);
        const float m_p = std::cbrt(m_c);
        const float s_p = std::cbrt(s_c);

        return Oklab{
            .l = 0.2104542553f * l_p + 0.7936177850f * m_p - 0.0040720468f * s_p,
            .a = 1.9779984951f * l_p - 2.4285922050f * m_p + 0.4505937099f * s_p,
            .b = 0.0259040371f * l_p + 0.7827717662f * m_p - 0.8086758033f * s_p
        };
    }

    [[nodiscard]] static Oklab to_oklab(RGB8 color) noexcept {
        return xyz_to_oklab(to_xyz(to_linear(color)));
    }

    [[nodiscard]] static Oklch to_oklch(Oklab lab) noexcept {
        float h_deg = std::atan2(lab.b, lab.a) * (180.0f / std::numbers::pi_v<float>);
        if (h_deg < 0.0f) {
            h_deg += 360.0f;
        }
        return Oklch{
            .l = lab.l,
            .c = std::hypot(lab.a, lab.b),
            .h = h_deg
        };
    }

    [[nodiscard]] static float delta_e_ok(Oklab c1, Oklab c2) noexcept {
        return std::hypot(c1.l - c2.l, c1.a - c2.a, c1.b - c2.b);
    }
};

} // namespace color

int main() {
    constexpr color::RGB8 color1{.r = 255, .g = 0, .b = 0};
    constexpr color::RGB8 color2{.r = 200, .g = 20, .b = 10};

    const auto lab1 = color::ColorConverter::to_oklab(color1);
    const auto lab2 = color::ColorConverter::to_oklab(color2);

    const float de = color::ColorConverter::delta_e_ok(lab1, lab2);
    
    std::cout << "Oklab Color 1: L=" << lab1.l << ", a=" << lab1.a << ", b=" << lab1.b << "\n";
    std::cout << "Oklab Color 2: L=" << lab2.l << ", a=" << lab2.a << ", b=" << lab2.b << "\n";
    std::cout << "Delta E_OK = " << de << "\n";

    return 0;
}
```
:::

## 3. Особливості обробки крайових випадків та граничних умов

При практичній обробці зображень рушій повинен коректно обробляти крайові випадки, пов'язані з обмеженням математичної точності та виходом кольору за межі гамуту.

### 1. Випадки нульової хроматичності (Ахроматична вісь)
Коли колір є чисто сірим, білим чи чорним (`R = G = B`), його декартові координати `a` та `b` у просторі Oklab стають рівними нулю (`a = 0, b = 0`). 
При перетворенні у полярну систему Oklch функція `atan2(0, 0)` є математично неозначеною. Обчислювальний рушій повинен явно перевіряти поріг хроматичності `if (c < 1e-6f)` і примусово встановлювати кут тону `h = 0.0f`, щоб уникнути появи значень `NaN` або невизначеної поведінки плаваючої крапки.

### 2. Кліпінг позагамутових кольорів (Gamut Mapping)
При оберненому перетворенні з Oklab чи Oklch у простір sRGB частина обчислених координат `R_linear`, `G_linear`, `B_linear` може вийти за межі допустимого діапазону `[0.0 .. 1.0]` (стати від'ємною або перевищити одиницю). Це означає, що згенерований у перцептивному просторі колір є занадто насиченим і не може бути відтворений звичайним sRGB-монітором.

Найпростіший метод відсікання (Clamping) полягає у затисканні значень `clamp(val, 0.0f, 1.0f)`. Проте примусове затискання окремих каналів викривляє колірний тон об'єкта. Професійні колірні рушії виконують алгоритм відсікання в Oklch: вони зберігають перцептивну світлоту `L` та кут тону `h` незмінними, бінарним пошуком зменшуючи лише хроматичність `C` доти, доки обчислений вектор sRGB не вкладеться у куб `[0.0 .. 1.0]`.

## 4. Аналіз часової складності та SIMD-векторизація

Перетворення кожного пікселя вимагає виконання трьох викликів степеня `powf()` та трьох викликів кубічного кореня `cbrtf()`. На стандартному CPU обчислення кубічного кореня виконується за допомогою послідовних ітерацій метода Ньютона — Рафсона або апаратних плаваючих інструкцій, що вимагає від 15 до 45 процесорних тактів на піксель.

Для потокової обробки 4K-відеосигналу (`3840 × 2160 = 8 294 400 пікселів`) при 60 кадрах на секунду рушій повинен обробляти понад 497 мільйонів пікселів на секунду.

Для забезпечення такої швидконості застосовують дві головні техніки оптимізації:

### 1. Таблична апроксимація лінеаризації (sRGB LUT)
Оскільки вхідні значення sRGB є 8-бітними цілими числами у діапазоні `[0 .. 255]`, замість повторного обчислення дробової степені `powf(c, 2.4)` створюють сталеве масив-таблицю лукапу з 256 елементів типу `float`:

:::tabs
```c
/* C (C99): Дінамічна ініціалізація LUT при старті програми */
static float srgb_lut[256];
void init_srgb_lut(void) {
    for (int i = 0; i < 256; ++i) {
        float c = (float)i / 255.0f;
        srgb_lut[i] = (c <= 0.04045f) ? (c / 12.92f) : powf((c + 0.055f) / 1.055f, 2.4f);
    }
}
```
```cpp
// C++ (C++20): Компіляція таблиці LUT на етапі компіляції через consteval / constexpr
#include <array>
#include <cmath>

namespace color {

[[nodiscard]] consteval std::array<float, 256> make_srgb_lut() noexcept {
    std::array<float, 256> lut{};
    for (size_t i = 0; i < 256; ++i) {
        const float c = static_cast<float>(i) / 255.0f;
        if (c <= 0.04045f) {
            lut[i] = c / 12.92f;
        } else {
            // C++20 constexpr math підтримка
            lut[i] = std::pow((c + 0.055f) / 1.055f, 2.4f);
        }
    }
    return lut;
}

inline constexpr auto srgb_lut = make_srgb_lut();

} // namespace color
```
:::

Використання `srgb_lut[pixel_val]` зменшує час лінеаризації до одного звернення у cache пам'яті (1–2 такти CPU).

### 2. Векторизація SIMD (AVX2 / ARM NEON)
Замість упаковки даних у масив структур (AoS — Array of Structures), зображення зберігають у форматі структур масивів (SoA — Structure of Arrays), де масиви `R`, `G`, `B` лежать у пам'яті окремими неперервними блоками.

Це дозволяє використовувати інструкції AVX2 (на процесорах x86) або NEON (на ARM), за один процесорний такт виконуючи паралельне матричне множення `M₁` та `M₂` одразу для 8 пікселів з плаваючою крапкою (256-бітні вектори `__m256`). Для обчислення кубічного кореня `cbrt` у SIMD-регістрах застосовують швидку векторизовану апроксимацію на основі алгоритму поліномів Чебишова з однією ітерацією Ньютона — Рафсона.
