# ⚙️ Реалізація растеризатора відрізків і кіл

Алгоритм Брезенгема дає змогу будувати базові двовимірні графічні примітиви (відрізки, кола, еліпси) виключно з використанням цілочисельної арифметики. У цій практичній реалізації розглянуто універсальний генератор ліній для всіх 8 октантів площини, алгоритм генерації дуг кіл та алгоритм растеризації еліпсів. Код наведено двома мовами — ідіоматичною мовою C та сучасним C++17/C++20 з використанням концепції RAII, типів `std::vector` і `std::span`.

## 1. Архітектурні принципи розробки растеризатора

Під підготовці алгоритму растеризації для реальних графічних систем (від низькорівневих прошивок мікроконтролерів без операційної системи до сучасних двигунів векторної графіки) ключовим завданням є відокремлення обчислювальної логіки вибору точок від конкретної структури оперативної пам'яті фреймбуфера.

У традиційних спрощених реалізаціях функція малювання безпосередньо здійснює запис у двовимірний масив пікселів або звертається до відеопам'яті. Однак такий підхід прив'язує алгоритм до конкретної колірної моделі, розрішення екрана та формату зберігання даних. Для забезпечення максимальної гнучкості та нульових накладних витрат пам'яті (zero-allocation) растеризатор будується за паттерном зворотного виклику (callback mechanism). Алгоритм обчислює чергові цілочисельні координати пікселя `(x, y)` і передає їх у функцію-обробник, яка виконує безпосередній запис у піксельний буфер, перевірку меж екрана (clipping) або підрахунок довжини.

У системному програмуванні на C++ це реалізується за допомогою шаблонів, функціональних об'єктів `std::function` або концептів (concepts), що дає змогу компілятору виконувати агресивне підставляння (inlining) обробника пікселів прямо у внутрішній цикл растеризації, усуваючи накладні витрати на виклики функцій через покажчик.

## 2. Загальний алгоритм растеризації ліній для 8 октантів

Для довільних точок `(x₁, y₁)` та `(x₂, y₂)` відрізок може мати додатний або від'ємний нахил, а також кут нахилу більше 45° відносно осі `X`. Щоб обробляти всі 8 октантів без дублювання коду, обчислюються напрямки кроків `sx = sign(x₂ - x₁)` та `sy = sign(y₂ - y₁)`, а також абсолютні різниці `dx = |x₂ - x₁|` та `dy = |y₂ - y₁|`.

Якщо `dy > dx`, то пряма є крутою (steep line): кут нахилу перевищує 45 градусів відносно горизонталі. У цьому випадку координата `y` зростає швидше за `x`. Щоб зберегти єдину структуру циклу, значення `dx` та `dy` міняються місцями (`swap`), а на кожному кроці алгоритм змінює координату `y` з одиничним кроком `sy`, коригуючи `x` лише при перевищенні порогового значення похибки.

Розглянемо детальний алгоритм растеризації мовами C та C++:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    int32_t x;
    int32_t y;
} Point2D;

typedef void (*PixelCallbackC)(int32_t x, int32_t y, void* user_data);

void bresenham_draw_line_c(int32_t x1, int32_t y1, int32_t x2, int32_t y2, PixelCallbackC plot, void* user_data) {
    int32_t dx = abs(x2 - x1);
    int32_t dy = abs(y2 - y1);
    int32_t sx = (x1 < x2) ? 1 : -1;
    int32_t sy = (y1 < y2) ? 1 : -1;
    
    bool is_steep = dy > dx;
    if (is_steep) {
        int32_t tmp = dx;
        dx = dy;
        dy = tmp;
    }
    
    int32_t err = 2 * dy - dx;
    int32_t x = x1;
    int32_t y = y1;
    
    for (int32_t i = 0; i <= dx; i++) {
        plot(x, y, user_data);
        
        while (err >= 0) {
            if (is_steep) {
                x += sx;
            } else {
                y += sy;
            }
            err -= 2 * dx;
        }
        
        if (is_steep) {
            y += sy;
        } else {
            x += sx;
        }
        err += 2 * dy;
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <functional>
#include <algorithm>
#include <cstdint>

struct Point2D {
    int32_t x{0};
    int32_t y{0};
    
    constexpr bool operator==(const Point2D& other) const noexcept = default;
};

using PixelCallback = std::function<void(int32_t x, int32_t y)>;

class BresenhamRasterizer {
public:
    template <typename Callback>
    requires std::invocable<Callback, int32_t, int32_t>
    static void draw_line(Point2D p1, Point2D p2, Callback&& plot) {
        int32_t dx = std::abs(p2.x - p1.x);
        int32_t dy = std::abs(p2.y - p1.y);
        const int32_t sx = (p1.x < p2.x) ? 1 : -1;
        const int32_t sy = (p1.y < p2.y) ? 1 : -1;
        
        const bool is_steep = (dy > dx);
        if (is_steep) {
            std::swap(dx, dy);
        }
        
        int32_t err = 2 * dy - dx;
        int32_t x = p1.x;
        int32_t y = p1.y;
        
        for (int32_t i = 0; i <= dx; ++i) {
            plot(x, y);
            
            while (err >= 0) {
                if (is_steep) {
                    x += sx;
                } else {
                    y += sy;
                }
                err -= 2 * dx;
            }
            
            if (is_steep) {
                y += sy;
            } else {
                x += sx;
            }
            err += 2 * dy;
        }
    }
    
    [[nodiscard]] static std::vector<Point2D> rasterize_line(Point2D p1, Point2D p2) {
        std::vector<Point2D> pixels;
        pixels.reserve(static_cast<size_t>(std::max(std::abs(p2.x - p1.x), std::abs(p2.y - p1.y)) + 1));
        draw_line(p1, p2, [&pixels](int32_t x, int32_t y) {
            pixels.push_back({x, y});
        });
        return pixels;
    }
};
```
:::

## 3. Реалізація алгоритму растеризації кіл

Для побудови кола радіуса `R` з центром у точці `(cx, cy)` використовується 8-бічна дзеркальна симетрія. Оскільки коло є симетричним відносно обох осей координат та двох діагоналей під кутом 45°, алгоритм обчислює похибковий параметр та координати пікселів лише для одного октанта дуги (від кута 90° до 45°).

Допоміжна функція симетрії `plot_circle_octants` на кожному кроці генерує 8 симетричних точок навколо центра `(cx, cy)`:
- `(cx + x, cy + y)`
- `(cx - x, cy + y)`
- `(cx + x, cy - y)`
- `(cx - x, cy - y)`
- `(cx + y, cy + x)`
- `(cx - y, cy + x)`
- `(cx + y, cy - x)`
- `(cx - y, cy - x)`

Це зменшує кількість обчислень у 8 разів порівняно з повним обходом кола, забезпечуючи граничну продуктивність.

:::tabs
```c
void plot_circle_octants_c(int32_t cx, int32_t cy, int32_t x, int32_t y, PixelCallbackC plot, void* user_data) {
    plot(cx + x, cy + y, user_data);
    plot(cx - x, cy + y, user_data);
    plot(cx + x, cy - y, user_data);
    plot(cx - x, cy - y, user_data);
    plot(cx + y, cy + x, user_data);
    plot(cx - y, cy + x, user_data);
    plot(cx + y, cy - x, user_data);
    plot(cx - y, cy - x, user_data);
}

void bresenham_draw_circle_c(int32_t cx, int32_t cy, int32_t radius, PixelCallbackC plot, void* user_data) {
    int32_t x = 0;
    int32_t y = radius;
    int32_t d = 3 - 2 * radius;
    
    plot_circle_octants_c(cx, cy, x, y, plot, user_data);
    
    while (y >= x) {
        x++;
        if (d > 0) {
            y--;
            d = d + 4 * (x - y) + 10;
        } else {
            d = d + 4 * x + 6;
        }
        plot_circle_octants_c(cx, cy, x, y, plot, user_data);
    }
}
```
```cpp
class BresenhamCircle {
public:
    template <typename Callback>
    requires std::invocable<Callback, int32_t, int32_t>
    static void draw_circle(Point2D center, int32_t radius, Callback&& plot) {
        int32_t x = 0;
        int32_t y = radius;
        int32_t d = 3 - 2 * radius;
        
        auto plot_symmetric = [&](int32_t px, int32_t py) {
            plot(center.x + px, center.y + py);
            plot(center.x - px, center.y + py);
            plot(center.x + px, center.y - py);
            plot(center.x - px, center.y - py);
            plot(center.x + py, center.y + px);
            plot(center.x - py, center.y + px);
            plot(center.x + py, center.y - px);
            plot(center.x - py, center.y - px);
        };
        
        plot_symmetric(x, y);
        
        while (y >= x) {
            ++x;
            if (d > 0) {
                --y;
                d += 4 * (x - y) + 10;
            } else {
                d += 4 * x + 6;
            }
            plot_symmetric(x, y);
        }
    }
    
    [[nodiscard]] static std::vector<Point2D> rasterize_circle(Point2D center, int32_t radius) {
        std::vector<Point2D> pixels;
        draw_circle(center, radius, [&pixels](int32_t x, int32_t y) {
            pixels.push_back({x, y});
        });
        return pixels;
    }
};
```
:::

## 4. Алгоритм Брезенгема для еліпсів

Растеризація еліпса з канонічними піввісями `rx` та `ry` вимагає поділу дуги першого квадранта на дві області, оскільки кутовий коефіцієнт дотичної `|dy / dx|` змінюється від `0` до нескінченності. 

У першій області (де нахил менший за 45°) провідною віссю є `X`, а в другій області (де нахил більший за 45°) провідною віссю стає `Y`. Перехід між областями відбувається, коли умова `2 * ry² * x < 2 * rx² * y` стає хибною.

:::tabs
```c
void plot_ellipse_quadrants_c(int32_t cx, int32_t cy, int32_t x, int32_t y, PixelCallbackC plot, void* user_data) {
    plot(cx + x, cy + y, user_data);
    plot(cx - x, cy + y, user_data);
    plot(cx + x, cy - y, user_data);
    plot(cx - x, cy - y, user_data);
}

void bresenham_draw_ellipse_c(int32_t cx, int32_t cy, int32_t rx, int32_t ry, PixelCallbackC plot, void* user_data) {
    int64_t rx2 = (int64_t)rx * rx;
    int64_t ry2 = (int64_t)ry * ry;
    int64_t two_rx2 = 2 * rx2;
    int64_t two_ry2 = 2 * ry2;
    
    int32_t x = 0;
    int32_t y = ry;
    int64_t px = 0;
    int64_t py = two_rx2 * y;
    
    // Область 1
    int64_t d1 = ry2 - (rx2 * ry) + (rx2 / 4);
    plot_ellipse_quadrants_c(cx, cy, x, y, plot, user_data);
    
    while (px < py) {
        x++;
        px += two_ry2;
        if (d1 < 0) {
            d1 += ry2 + px;
        } else {
            y--;
            py -= two_rx2;
            d1 += ry2 + px - py;
        }
        plot_ellipse_quadrants_c(cx, cy, x, y, plot, user_data);
    }
    
    // Область 2
    int64_t d2 = ry2 * (x + 1) * (x + 1) + rx2 * (y - 1) * (y - 1) - rx2 * ry2;
    while (y > 0) {
        y--;
        py -= two_rx2;
        if (d2 > 0) {
            d2 += rx2 - py;
        } else {
            x++;
            px += two_ry2;
            d2 += rx2 - py + px;
        }
        plot_ellipse_quadrants_c(cx, cy, x, y, plot, user_data);
    }
}
```
```cpp
class BresenhamEllipse {
public:
    template <typename Callback>
    requires std::invocable<Callback, int32_t, int32_t>
    static void draw_ellipse(Point2D center, int32_t rx, int32_t ry, Callback&& plot) {
        const int64_t rx2 = static_cast<int64_t>(rx) * rx;
        const int64_t ry2 = static_cast<int64_t>(ry) * ry;
        const int64_t two_rx2 = 2 * rx2;
        const int64_t two_ry2 = 2 * ry2;
        
        int32_t x = 0;
        int32_t y = ry;
        int64_t px = 0;
        int64_t py = two_rx2 * y;
        
        auto plot_4way = [&](int32_t ex, int32_t ey) {
            plot(center.x + ex, center.y + ey);
            plot(center.x - ex, center.y + ey);
            plot(center.x + ex, center.y - ey);
            plot(center.x - ex, center.y - ey);
        };
        
        // Область 1
        int64_t d1 = ry2 - (rx2 * ry) + (rx2 / 4);
        plot_4way(x, y);
        
        while (px < py) {
            ++x;
            px += two_ry2;
            if (d1 < 0) {
                d1 += ry2 + px;
            } else {
                --y;
                py -= two_rx2;
                d1 += ry2 + px - py;
            }
            plot_4way(x, y);
        }
        
        // Область 2
        int64_t d2 = ry2 * (x + 1) * (x + 1) + rx2 * (y - 1) * (y - 1) - rx2 * ry2;
        while (y > 0) {
            --y;
            py -= two_rx2;
            if (d2 > 0) {
                d2 += rx2 - py;
            } else {
                ++x;
                px += two_ry2;
                d2 += rx2 - py + px;
            }
            plot_4way(x, y);
        }
    }
};
```
:::

## 5. Інтеграційний приклад та модуль тестування

Програма нижче демонструє роботу растеризатора Брезенгема для тестового відрізка від точки `(0, 0)` до `(7, 3)` та кола радіуса `R = 6` з центром у початку координат `(0, 0)`.

:::tabs
```c
static void print_pixel_c(int32_t x, int32_t y, void* user_data) {
    (void)user_data;
    printf("(%d, %d) ", x, y);
}

int main(void) {
    printf("Line (0,0) -> (7,3):\n");
    bresenham_draw_line_c(0, 0, 7, 3, print_pixel_c, NULL);
    printf("\n\nCircle R=6 at (0,0):\n");
    bresenham_draw_circle_c(0, 0, 6, print_pixel_c, NULL);
    printf("\n");
    return 0;
}
```
```cpp
int main() {
    std::cout << "Line (0,0) -> (7,3):\n";
    auto line_pixels = BresenhamRasterizer::rasterize_line({0, 0}, {7, 3});
    for (const auto& p : line_pixels) {
        std::cout << "(" << p.x << ", " << p.y << ") ";
    }
    
    std::cout << "\n\nCircle R=6 at (0,0):\n";
    auto circle_pixels = BresenhamCircle::rasterize_circle({0, 0}, 6);
    for (const auto& p : circle_pixels) {
        std::cout << "(" << p.x << ", " << p.y << ") ";
    }
    std::cout << "\n";
    return 0;
}
```
:::

## 6. Пастки реалізації, переповнення та крайові випадки

1. **Переповнення цілочисельних змінних (Integer Overflow):** 
   При розрахунку відрізків із великими координатами або кіл і еліпсів великих радіусів (наприклад, `rx, ry > 32767` на 16-бітових системних архітектурах) вирази `2 * rx²` або `rx² * ry²` викликають вихід за межі діапазону знакового 32-бітного числа `int32_t`. Для змінних похибки та квадратів напіввісей слід обов'язково використовувати 64-бітні цілочисельні типи `int64_t` або `uint64_t`, як показано у наведених прикладах коду.

2. **Інваріантність напрямку растеризації (Directional Invariance):** 
   Для графічних систем важливим є дотримання інваріантності: малювання відрізка від точки `A` до точки `B` має генерувати точно такий же набір пікселів, як і малювання від точки `B` до точки `A`. У несиметричних варіантах алгоритму при використанні нестрогої нерівності `err >= 0` зміна напрямку виклику може змінити вибір дискретного пікселя на 1 крок у спірних точках. Для забезпечення повної симетрії координати перед побудовою впорядковують так, щоб `x1` завжди був меншим за `x2` (або `y1 < y2` для крутих ліній).

3. **Обітення меж екрана (Clipping):** 
   При малюванні графічних примітивів, частина яких лежить поза межами видимого екрана або вікна (viewport), неконтрольований запис координати у фреймбуфер спричиняє пошкодження пам'яті (memory corruption) або аварійне завершення програми. Перевірку меж `0 <= x < width` та `0 <= y < height` необхідно виконувати безпосередньо у функції зворотного виклику `plot(x, y)` або застосовувати попередній алгоритм обітення Коена-Сазерленда чи Ліанга-Барські до виклику растеризатора Брезенгема.

4. **Субпіксельна точність (Subpixel Precision):** 
   У сучасних графічних двигунах векторні координати точок передаються не цілими числами, а числами з фіксованою крапкою (fixed-point arithmetic), наприклад, із 4 або 8 бітами дробової частини (1/16 або 1/256 пікселя). Алгоритм Брезенгема природно узагальнюється на випадок субпіксельної сітки: усі координати помножуються на масштабуючий коефіцієнт `2^N`, а початкова похибка обчислюється з урахуванням дробового зсуву початкової точки відносно цілого вузла ґратки.

5. **Оптимізація для кєш-пам'яті (Cache Locality):** 
   Попіксельний запис у фреймбуфер при малюванні крутих або діагональних ліній може викликати випадкові промахи кєш-пам'яті процесора (cache misses), оскільки сусідні за віссю Y пікселі віддалені в оперативній пам'яті на цілу довжину рядка екрана (`stride`). Для високопродуктивних графічних систем застосовують сканування за смугами (tile-based rendering) або групування вертикальних кроків.
