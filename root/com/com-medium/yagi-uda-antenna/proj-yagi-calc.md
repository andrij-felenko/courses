# ⚙️ Програма розрахунку геометричних параметрів антени Яґі-Уда

Проектування та практичне виготовлення антени Яґі-Уда вимагає точного математичного обчислення фізичних довжин усіх елементів (рефлектора, активного випромінювача та ряду директорів), а також відстаней між ними вздовж несучої траверси (буму). Найменша помилка у декілька міліметрів на частотах понад 400 МГц призводить до зміщення резонансної частоти, руйнування синфазності променя, різкого падіння коефіцієнта підсилення та зростання коефіцієнта стоячої хвилі (`КСХ`).

---

### Алгоритм та фізичні основи розрахунку

В основі програмного розрахунку лежать п'ять послідовних інженерно-фізичних кроків.

#### 1. Обчислення довжини хвилі у вільному просторі
Довжина електромагнітної хвилі `λ` (у метрах) розраховується через швидкість світла у вакуумі `c ≈ 299 792 458 м/с` та центральну робочу частоту `f_mhz` (у мегагерцах):

```
λ = c / f = 299.792458 / f_mhz
```

#### 2. Оцінка коефіцієнта укорочення (Velocity Factor, k_v)
Електромагнітна хвиля поширюється вздовж металевого провідника трохи повільніше, ніж у чистому вакуумі. Крім того, на кінцях провідника скінченного діаметра `d` виникає крайова ємність. Це викликає ефект електродинамічного подовження провідника, тому його реальна фізична довжина мусить бути меншою за теоретичну геометричну довжину.

Коефіцієнт укорочення `k_v` описується логарифмічною залежністю від відношення діаметра провідника `d` до довжини хвилі `λ`:

```
ratio = d / λ
k_v = 0.95 - 0.02 · log₁₀(ratio)
```

Для типових алюмінієвих або мідних трубок діаметром від 3 мм до 10 мм у діапазоні 100–900 МГц коефіцієнт `k_v` лежить у межах від **0.91 до 0.97**.

#### 3. Обчислення довжин та розстановок елементів
- **Рефлектор (Reflector):** Має індуктивний опір для забезпечення протифази ззаду. Його довжина становить `L_R = 0.485 · λ · k_v`, а відстань від активного диполя обирається в межах `S_R = 0.15...0.22 · λ`.
- **Активний диполь (Driven Dipole):** Розраховується на точний резонанс `L_D = 0.455 · λ · k_v`.
- **Директори (Directors):** Мають ємнісний опір. Перший директор `D1` роблять довжиною `L_D1 = 0.420 · λ · k_v`. Кожен наступний директор розраховується з поступовим конусним укороченням `L_Di = (0.420 - 0.008 · i) · λ · k_v`, що компенсує зміну фазової швидкості поверхневої хвилі вздовж траверси.

#### 4. Стратегія розстановки директорів (Uniform vs Progressive Spacing)
У найпростіших антенах Яґі-Уда відстані між директорами роблять однаковими (`S_D ≈ 0.15·λ...0.20·λ`). Однак у високоефективних антенах застосовують **прогресивне розширення кроку** (*progressive spacing*): відстані між першими директорами роблять вужчими (`0.15·λ`), а для дальніх директорів збільшують до `0.25·λ...0.28·λ`. Це запобігає передчасному розриву поверхневої хвилі та підвищує коефіцієнт підсилення на 1–1.5 дБ при тій самій кількості елементів.

#### 5. Налаштування та калібрування за допомогою векторного аналізатора кіл (VNA)
Після складання геометричної конструкції виконане вимірювання за допомогою векторного аналізатора кіл (VNA, наприклад NanoVNA) дозволяє остаточно підлаштувати параметри:
- Резонансна частота коригується підрізанням довжини активного диполя `L_D`.
- Мінімізація коефіцієнта стоячої хвилі (`КСХ < 1.15`) досягається підлаштуванням елементів Гамма-узгодження або U-коліна.
- Максимум відношення вперед/назад `F/B` підлаштовується зміною довжини рефлектора `L_R`.

---

### Порівняльний аналіз розмірів для популярних діапазонів

Для ілюстрації залежності геометричних розмірів антени Яґі-Уда від частоти, розглянемо чисельні параметри 5-елементної антени (1 рефлектор, 1 диполь, 3 директори) із 6-міліметрової алюмінієвої трубки для трьох типових систем радіозв'язку:

1. **Радіоаматорський діапазон 2 метри (145.00 МГц):**
   - Довжина хвилі `λ = 2.067 м` (206.7 см);
   - Довжина рефлектора `L_R = 952 мм`;
   - Довжина активного диполя `L_D = 893 мм`;
   - Загальна довжина буму = `1.12 м`.

2. **Діαпазон LPD / ISM (433.92 МГц):**
   - Довжина хвилі `λ = 0.691 м` (69.1 см);
   - Довжина рефлектора `L_R = 318 мм`;
   - Довжина активного диполя `L_D = 298 мм`;
   - Загальна довжина буму = `375 мм`.

3. **Діапазон LoRa / IoT (868.00 МГц):**
   - Довжина хвилі `λ = 0.345 м` (34.5 см);
   - Довжина рефлектора `L_R = 159 мм`;
   - Довжина активного диполя `L_D = 149 мм`;
   - Загальна довжина буму = `187 мм`.

Зміна діапазону від 145 МГц до 868 МГц зменшує габарити антени у 6 разів, перетворюючи її з громіздкої вуличної конструкції на компактну модульниу антену.

---

### Практична програма розрахунку мовами C та C++

Нижче наведено кросплатформову реалізацію алгоритму розрахунку геометрії антени Яґі-Уда. 

Код подано у двох ідіоматичних вкладках:
1. **C (C99/C11):** Класичний системний код із динамічним виділенням пам'яті через `malloc`/`free`, строгим контролем покажчиків та форматованим виводом `printf`.
2. **C++ (C++20):** Сучасний об'єктно-орієнтований код із використанням безпечного контейнера `std::vector`, автоматичного управління пам'яттю (RAII), функцій `std::clamp` та струменів виводу `std::cout`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    char name[32];
    double position_m;
    double length_m;
} YagiElement;

typedef struct {
    double frequency_mhz;
    double wavelength_m;
    double boom_length_m;
    int total_elements;
    YagiElement *elements;
} YagiAntenna;

YagiAntenna* yagi_calculate(double freq_mhz, int num_directors, double element_dia_mm) {
    if (freq_mhz <= 0.0 || num_directors < 1) {
        return NULL;
    }

    YagiAntenna *ant = (YagiAntenna*)malloc(sizeof(YagiAntenna));
    if (!ant) return NULL;

    ant->frequency_mhz = freq_mhz;
    ant->wavelength_m = 299.792458 / freq_mhz; // λ в метрах

    // Оцінка коефіцієнта укорочення k_v залежно від відношення d/λ
    double ratio = (element_dia_mm / 1000.0) / ant->wavelength_m;
    double k_v = 0.95 - 0.02 * log10(ratio > 1e-4 ? ratio : 1e-4);
    if (k_v > 0.98) k_v = 0.98;
    if (k_v < 0.91) k_v = 0.91;

    ant->total_elements = 2 + num_directors; // 1 Рефлектор + 1 Активний + N Директорів
    ant->elements = (YagiElement*)malloc(sizeof(YagiElement) * ant->total_elements);
    if (!ant->elements) {
        free(ant);
        return NULL;
    }

    double lambda = ant->wavelength_m;
    double current_z = 0.0;

    // 1. Рефлектор
    snprintf(ant->elements[0].name, sizeof(ant->elements[0].name), "Рефлектор");
    ant->elements[0].position_m = current_z;
    ant->elements[0].length_m = 0.485 * lambda * k_v;

    // 2. Активний диполь (відстань від рефлектора ~ 0.18 λ)
    current_z += 0.18 * lambda;
    snprintf(ant->elements[1].name, sizeof(ant->elements[1].name), "Активний диполь");
    ant->elements[1].position_m = current_z;
    ant->elements[1].length_m = 0.455 * lambda * k_v;

    // 3. Директори
    double dir_spacing = 0.15 * lambda;
    for (int i = 0; i < num_directors; i++) {
        current_z += dir_spacing;
        snprintf(ant->elements[2 + i].name, sizeof(ant->elements[2 + i].name), "Директор %d", i + 1);
        ant->elements[2 + i].position_m = current_z;

        // Коротшають за конусною залежністю
        double factor = 0.420 - 0.008 * i;
        if (factor < 0.370) factor = 0.370;
        ant->elements[2 + i].length_m = factor * lambda * k_v;

        // Пропорційне розширення відстані для далеких директорів
        dir_spacing = (0.15 + 0.01 * (i + 1)) * lambda;
        if (dir_spacing > 0.28 * lambda) dir_spacing = 0.28 * lambda;
    }

    ant->boom_length_m = current_z;
    return ant;
}

void yagi_free(YagiAntenna *ant) {
    if (ant) {
        if (ant->elements) free(ant->elements);
        free(ant);
    }
}

int main(void) {
    double freq = 433.92; // МГц (LPD/ISM діапазон)
    int directors = 4;
    double dia_mm = 6.0;   // 6 мм алюмінієва трубка

    YagiAntenna *ant = yagi_calculate(freq, directors, dia_mm);
    if (!ant) {
        fprintf(stderr, "Помилка обчислення параметрів антени\n");
        return 1;
    }

    printf("=========================================================\n");
    printf("  РОЗРАХУНОК АНТЕНИ ЯҐІ-УДА ДЛЯ ЧАСТОТИ %.2f МГц\n", ant->frequency_mhz);
    printf("  Довжина хвилі λ = %.4f м (%.1f см)\n", ant->wavelength_m, ant->wavelength_m * 100.0);
    printf("  Загальна довжина траверси (буму) = %.3f м\n", ant->boom_length_m);
    printf("=========================================================\n");
    printf("%-18s | %-16s | %-16s\n", "Елемент", "Позиція на бумі (мм)", "Довжина L (мм)");
    printf("---------------------------------------------------------\n");

    for (int i = 0; i < ant->total_elements; i++) {
        printf("%-18s | %18.1f | %14.1f\n",
               ant->elements[i].name,
               ant->elements[i].position_m * 1000.0,
               ant->elements[i].length_m * 1000.0);
    }
    printf("=========================================================\n");

    yagi_free(ant);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct YagiElement {
    std::string name;
    double position_m;
    double length_m;
};

class YagiCalculator {
public:
    struct Configuration {
        double frequency_mhz;
        int num_directors;
        double element_diameter_mm;
    };

    struct Result {
        double frequency_mhz;
        double wavelength_m;
        double boom_length_m;
        std::vector<YagiElement> elements;
    };

    static Result calculate(const Configuration& config) {
        Result res{};
        res.frequency_mhz = config.frequency_mhz;
        res.wavelength_m = 299.792458 / config.frequency_mhz;

        const double ratio = (config.element_diameter_mm / 1000.0) / res.wavelength_m;
        double k_v = 0.95 - 0.02 * std::log10(ratio > 1e-4 ? ratio : 1e-4);
        k_v = std::clamp(k_v, 0.91, 0.98);

        const double lambda = res.wavelength_m;
        double current_z = 0.0;

        // 1. Рефлектор
        res.elements.push_back({"Рефлектор", current_z, 0.485 * lambda * k_v});

        // 2. Активний диполь
        current_z += 0.18 * lambda;
        res.elements.push_back({"Активний диполь", current_z, 0.455 * lambda * k_v});

        // 3. Директори
        double dir_spacing = 0.15 * lambda;
        for (int i = 0; i < config.num_directors; ++i) {
            current_z += dir_spacing;
            double factor = std::max(0.370, 0.420 - 0.008 * i);
            res.elements.push_back({
                "Директор " + std::to_string(i + 1),
                current_z,
                factor * lambda * k_v
            });
            dir_spacing = std::min(0.28 * lambda, (0.15 + 0.01 * (i + 1)) * lambda);
        }

        res.boom_length_m = current_z;
        return res;
    }
};

int main() {
    YagiCalculator::Configuration config{
        .frequency_mhz = 433.92,
        .num_directors = 4,
        .element_diameter_mm = 6.0
    };

    auto res = YagiCalculator::calculate(config);

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "=========================================================\n";
    std::cout << "  РОЗРАХУНОК АНТЕНИ ЯҐІ-УДА ДЛЯ ЧАСТОТИ " << res.frequency_mhz << " МГц\n";
    std::cout << "  Довжина хвилі λ = " << (res.wavelength_m * 100.0) << " см\n";
    std::cout << "  Довжина траверси = " << (res.boom_length_m * 1000.0) << " мм\n";
    std::cout << "=========================================================\n";
    std::cout << std::left << std::setw(18) << "Елемент" << " | "
              << std::right << std::setw(18) << "Позиція (мм)" << " | "
              << std::setw(14) << "Довжина L (мм)" << "\n";
    std::cout << "---------------------------------------------------------\n";

    for (const auto& elem : res.elements) {
        std::cout << std::left << std::setw(18) << elem.name << " | "
                  << std::right << std::setw(18) << (elem.position_m * 1000.0) << " | "
                  << std::setw(14) << (elem.length_m * 1000.0) << "\n";
    }
    std::cout << "=========================================================\n";

    return 0;
}
```
:::

---

### Компенсація металевого буму (Boom Correction Factor)

При практичному збиранні антени металеві стрижні можуть проходити наскрізь через металеву квадратну або круглясту несучу трубу (бум). Наявність суцільного металевого буму створює додатковий локальний масив металу навколо центральної частини диполів, що електрично подовжує елементи.

Щоб зберегти розраховану резонансну частоту, фізичну довжину кожного елемента `L`, який проходить наскрізь через суцільний металевий бум діаметром `D_boom`, необхідно додатково збільшити на величину поправки `ΔL`:

```
ΔL = D_boom · (0.5...0.8)
```

- Якщо елемент проходити наскрізь через металевий бум без ізоляції: `ΔL ≈ 0.65 · D_boom`.
- Якщо елемент встановлюється поверх металевого буму на ізоляційній стійці: `ΔL ≈ 0.15 · D_boom`.
- Якщо бум виготовлено з діелектричного матеріалу (склопластик, дерево, PVC): поправка дорівнює нулю (`ΔL = 0`).

---

### Інструкція з компіляції та запуску

Компіляція програми виконується стандартними інструментами командного рядка:

```bash
# Компіляція C-версії (GCC / Clang):
gcc -O2 -std=c11 proj-yagi-calc.c -o yagi_calc_c -lm

# Компіляція C++ версії (GCC / Clang):
g++ -O2 -std=c++20 proj-yagi-calc.cpp -o yagi_calc_cpp

# Запуск:
./yagi_calc_c
```
