# ⚙️ Обчислення параметрів завантажувальної котушки та ККД антени

Ця вставка містить практичну інженерну програму мовами C та C++ для повного розрахунку необхідної індуктивності завантажувальної котушки, кількості витків за формулою Нагаока, опору випромінювання короткого штиря, втрат у котушці, ККД антени, її смуги пропускання, теплового розсіювання та пікової високовольтної напруги при заданій потужності передавача.

---

### Інженерна методологія та алгоритм розрахунку

Для розробки мобільної чи стаціонарної укороченої антени інженер має розв'язати систему взаємопов'язаних електродинамічних рівнянь. Наша програма виконує розрахунок у шість послідовних етапів:

1. **Обчислення власної ємності штиря `C_ant`:**  
   За формулою Шелкунова обчислюється ємність монополя висотою `h` та радіусом провідника `a` над ідеальною провідною землею:
   ```
   C_ant = (2π · ε₀ · h) / (ln(h / a) - 1)
   ```

2. **Визначення ємнісного реактивного опору `X_C` та індуктивності `L_coil`:**  
   На робочій частоті `f` знаходиться ємнісна реактивність `X_C = 1 / (2π · f · C_ant)`. З умови компенсації реактивностей `X_L = X_C` обчислюється необхідна індуктивність котушки:
   ```
   L_coil = X_C / (2π · f)
   ```

3. **Обчислення опору випромінювання та опору втрат:**  
   Опір випромінювання короткого монополя знаходиться за квадратичною формулою `R_рад = 160 · π² · (h / λ)²`. Опір ВЧ-втрат у котушці обчислюється за заданою добротністю `Q_coil`:
   ```
   R_котушки = X_L / Q_coil
   ```
   Підсумковий активний опір дорівнює сумі `R_повн = R_рад + R_землі + R_котушки`.

4. **Обчислення ККД, добротності та смуги пропускання:**  
   Визначаються корисний ККД випромінювання `η = (R_рад / R_повн) × 100%`, еквівалентна добротність антени `Q_ант = X_C / R_повн` та її ширина смуги пропускання по рівню КСХ = 2.0 (`BW = f / Q_ант`).

5. **Геометричний розрахунок витків котушки за формулою Нагаока:**  
   Для циліндричної одношарової котушки з діаметром каркаса `D` (см) та довжиною намотки `l` (см) необхідна кількість витків `N` становить:
   ```
   N = √[ L_coil (мкГн) · (45 · D + 100 · l) / (2.54 · D²) ]
   ```

6. **Розрахунок режимів високої напруги та теплового розсіювання:**  
   При заданій вхідній потужності `P` обчислюється ВЧ-струм `I = √(P / R_повн)`, пікова напруга на витках `V_peak = I · X_L · √2` та теплова потужність, яка розсіюється на котушці `P_тепло = I² · R_котушки`.

---

### Практична реалізація

:::tabs
```c
/* loading_coil_calc.c - Розрахунок завантажувальної котушки мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double freq_mhz;        /* Робоча частота в МГц */
    double height_m;        /* Висота штиря в метрах */
    double wire_radius_mm;  /* Радіус провідника в мм */
    double ground_loss_ohm; /* Опір втрат у землі/кузові (Ом) */
    double coil_q;          /* Власна добротність котушки (Q) */
    double power_watts;     /* Вхідна потужність передавача (Вт) */
    double coil_diam_cm;    /* Діаметр каркаса котушки (см) */
    double coil_len_cm;     /* Довжина намотки котушки (см) */
} AntennaInputs;

typedef struct {
    double wavelength_m;    /* Довжина хвилі (м) */
    double c_ant_pf;        /* Власна ємність штиря (пФ) */
    double x_c_ohm;         /* Ємнісна реактивність (Ом) */
    double l_coil_uh;       /* Необхідна індуктивність (мкГн) */
    double r_rad_ohm;       /* Опір випромінювання (Ом) */
    double r_coil_ohm;      /* Опір втрат котушки (Ом) */
    double r_total_ohm;     /* Повний опір системи (Ом) */
    double efficiency_pct;  /* ККД випромінювання (%) */
    double q_ant;           /* Добротність антени */
    double bandwidth_khz;   /* Смуга пропускання -3dB (кГц) */
    double v_peak_volts;    /* Пікова напруга на котушці (В) */
    double p_heat_watts;    /* Теплова потужність на котушці (Вт) */
    int turns_count;        /* Кількість витків за Нагаока */
} AntennaResults;

int calculate_loading_coil(const AntennaInputs* in, AntennaResults* out) {
    if (!in || !out) {
        return -1;
    }
    if (in->freq_mhz <= 0.0 || in->height_m <= 0.0 || in->wire_radius_mm <= 0.0 || in->coil_q <= 0.0) {
        return -2;
    }

    const double c_speed = 299792458.0;  /* Швидкість світла в м/с */
    const double eps0 = 8.854187817e-12; /* Електрична стала Ф/м */

    double freq_hz = in->freq_mhz * 1.0e6;
    double omega = 2.0 * M_PI * freq_hz;
    out->wavelength_m = c_speed / freq_hz;

    /* 1. Ємність штиря C_ant за Шелкуновим */
    double wire_radius_m = in->wire_radius_mm / 1000.0;
    double ln_ratio = log(in->height_m / wire_radius_m) - 1.0;
    if (ln_ratio <= 0.2) {
        return -3; /* Геометричне виродження штиря */
    }

    double c_farads = (2.0 * M_PI * eps0 * in->height_m) / ln_ratio;
    out->c_ant_pf = c_farads * 1.0e12;

    /* 2. Ємнісна реактивність та необхідна індуктивність */
    out->x_c_ohm = 1.0 / (omega * c_farads);
    out->l_coil_uh = (out->x_c_ohm / omega) * 1.0e6;

    /* 3. Опори випромінювання та втрат */
    double h_lambda_ratio = in->height_m / out->wavelength_m;
    out->r_rad_ohm = 160.0 * M_PI * M_PI * h_lambda_ratio * h_lambda_ratio;
    out->r_coil_ohm = out->x_c_ohm / in->coil_q;
    out->r_total_ohm = out->r_rad_ohm + in->ground_loss_ohm + out->r_coil_ohm;

    /* 4. ККД, Q-фактор та смуга */
    out->efficiency_pct = (out->r_rad_ohm / out->r_total_ohm) * 100.0;
    out->q_ant = out->x_c_ohm / out->r_total_ohm;
    out->bandwidth_khz = (in->freq_mhz * 1000.0) / out->q_ant;

    /* 5. Висока напруга та теплові втрати */
    double i_ant_rms = sqrt(in->power_watts / out->r_total_ohm);
    double v_rms = i_ant_rms * out->x_c_ohm;
    out->v_peak_volts = v_rms * sqrt(2.0);
    out->p_heat_watts = i_ant_rms * i_ant_rms * out->r_coil_ohm;

    /* 6. Формула Нагаока для обчислення витків */
    double d = in->coil_diam_cm;
    double l = in->coil_len_cm;
    if (d > 0.0 && l > 0.0) {
        double n_squared = (out->l_coil_uh * (45.0 * d + 100.0 * l)) / (2.54 * d * d);
        out->turns_count = (int)ceil(sqrt(n_squared));
    } else {
        out->turns_count = 0;
    }

    return 0;
}

void print_antenna_report(const AntennaInputs* in, const AntennaResults* res) {
    printf("========================================================\n");
    printf("   РЕЗУЛЬТАТИ РОЗРАХУНКУ ЗАВАНТАЖУВАЛЬНОЇ КОТУШКИ (C)   \n");
    printf("========================================================\n");
    printf("Вхідні параметри:\n");
    printf("  Частота: %.2f МГц (λ = %.2f м)\n", in->freq_mhz, res->wavelength_m);
    printf("  Висота штиря h: %.2f м (%.2f%% λ)\n", in->height_m, (in->height_m / res->wavelength_m) * 100.0);
    printf("  Радіус провідника: %.1f мм\n", in->wire_radius_mm);
    printf("  Потужність передавача: %.0f Вт\n", in->power_watts);
    printf("--------------------------------------------------------\n");
    printf("Параметри котушки та імпедансу:\n");
    printf("  Ємність штиря C_ant: %.2f пФ\n", res->c_ant_pf);
    printf("  Реактивний опір X_C: -j%.1f Ом\n", res->x_c_ohm);
    printf("  Необхідна індуктивність L_coil: %.2f мкГн\n", res->l_coil_uh);
    printf("  Каркас D=%.1f см, довжина l=%.1f см  ⇒  %d витків\n", 
           in->coil_diam_cm, in->coil_len_cm, res->turns_count);
    printf("--------------------------------------------------------\n");
    printf("Баланс опорів та ККД:\n");
    printf("  Опір випромінювання R_рад: %.2f Ом\n", res->r_rad_ohm);
    printf("  Опір втрат котушки R_котушки: %.2f Ом\n", res->r_coil_ohm);
    printf("  Опір заземлення/кузова R_землі: %.2f Ом\n", in->ground_loss_ohm);
    printf("  Повний опір R_повн: %.2f Ом\n", res->r_total_ohm);
    printf("  ККД випромінювання η: %.2f %%\n", res->efficiency_pct);
    printf("--------------------------------------------------------\n");
    printf("Характеристики смуги та режими напруги:\n");
    printf("  Добротність антени Q: %.1f\n", res->q_ant);
    printf("  Смуга пропускання BW (-3dB): %.1f кГц\n", res->bandwidth_khz);
    printf("  Теплові втрати на котушці: %.1f Вт\n", res->p_heat_watts);
    printf("  Пікова ВЧ-напруга V_peak: %.0f В (%.2f кВ)\n", 
           res->v_peak_volts, res->v_peak_volts / 1000.0);
    printf("========================================================\n");
}

int main(void) {
    AntennaInputs in = {
        .freq_mhz = 7.10,
        .height_m = 1.80,
        .wire_radius_mm = 2.0,
        .ground_loss_ohm = 4.0,
        .coil_q = 200.0,
        .power_watts = 100.0,
        .coil_diam_cm = 5.0,
        .coil_len_cm = 8.0
    };
    AntennaResults res;

    if (calculate_loading_coil(&in, &res) == 0) {
        print_antenna_report(&in, &res);
    } else {
        fprintf(stderr, "Помилка: некоректні вхідні параметри антени!\n");
        return 1;
    }
    return 0;
}
```
```cpp
// loading_coil_calc.cpp - Обчислення завантажувальної котушки мовою C++
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <expected>
#include <string>

struct AntennaInputs {
    double freq_mhz{7.10};
    double height_m{1.80};
    double wire_radius_mm{2.0};
    double ground_loss_ohm{4.0};
    double coil_q{200.0};
    double power_watts{100.0};
    double coil_diam_cm{5.0};
    double coil_len_cm{8.0};
};

struct AntennaResults {
    double wavelength_m;
    double c_ant_pf;
    double x_c_ohm;
    double l_coil_uh;
    double r_rad_ohm;
    double r_coil_ohm;
    double r_total_ohm;
    double efficiency_pct;
    double q_ant;
    double bandwidth_khz;
    double v_peak_volts;
    double p_heat_watts;
    int turns_count;
};

enum class CalcError {
    InvalidParameters,
    GeometryDegeneracy
};

class LoadingCoilCalculator {
public:
    [[nodiscard]] static std::expected<AntennaResults, CalcError> calculate(const AntennaInputs& in) noexcept {
        if (in.freq_mhz <= 0.0 || in.height_m <= 0.0 || in.wire_radius_mm <= 0.0 || in.coil_q <= 0.0) {
            return std::unexpected(CalcError::InvalidParameters);
        }

        constexpr double c_speed = 299792458.0;
        constexpr double eps0 = 8.854187817e-12;
        constexpr double pi = std::numbers::pi;

        const double freq_hz = in.freq_mhz * 1.0e6;
        const double omega = 2.0 * pi * freq_hz;
        const double wavelength = c_speed / freq_hz;

        const double wire_radius_m = in.wire_radius_mm / 1000.0;
        const double ln_ratio = std::log(in.height_m / wire_radius_m) - 1.0;
        if (ln_ratio <= 0.2) {
            return std::unexpected(CalcError::GeometryDegeneracy);
        }

        const double c_farads = (2.0 * pi * eps0 * in.height_m) / ln_ratio;
        const double c_ant_pf = c_farads * 1.0e12;
        const double x_c = 1.0 / (omega * c_farads);
        const double l_coil_uh = (x_c / omega) * 1.0e6;

        const double h_lambda = in.height_m / wavelength;
        const double r_rad = 160.0 * pi * pi * h_lambda * h_lambda;
        const double r_coil = x_c / in.coil_q;
        const double r_total = r_rad + in.ground_loss_ohm + r_coil;

        const double eff_pct = (r_rad / r_total) * 100.0;
        const double q_ant = x_c / r_total;
        const double bw_khz = (in.freq_mhz * 1000.0) / q_ant;

        const double i_ant_rms = std::sqrt(in.power_watts / r_total);
        const double v_rms = i_ant_rms * x_c;
        const double v_peak = v_rms * std::numbers::sqrt2;
        const double p_heat = i_ant_rms * i_ant_rms * r_coil;

        int turns = 0;
        if (in.coil_diam_cm > 0.0 && in.coil_len_cm > 0.0) {
            const double d = in.coil_diam_cm;
            const double l = in.coil_len_cm;
            const double n_sq = (l_coil_uh * (45.0 * d + 100.0 * l)) / (2.54 * d * d);
            turns = static_cast<int>(std::ceil(std::sqrt(n_sq)));
        }

        return AntennaResults{
            .wavelength_m = wavelength,
            .c_ant_pf = c_ant_pf,
            .x_c_ohm = x_c,
            .l_coil_uh = l_coil_uh,
            .r_rad_ohm = r_rad,
            .r_coil_ohm = r_coil,
            .r_total_ohm = r_total,
            .efficiency_pct = eff_pct,
            .q_ant = q_ant,
            .bandwidth_khz = bw_khz,
            .v_peak_volts = v_peak,
            .p_heat_watts = p_heat,
            .turns_count = turns
        };
    }
};

void print_cpp_report(const AntennaInputs& in, const AntennaResults& res) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "========================================================\n";
    std::cout << "  РЕЗУЛЬТАТИ РОЗРАХУНКУ ЗАВАНТАЖУВАЛЬНОЇ КОТУШКИ (C++)  \n";
    std::cout << "========================================================\n";
    std::cout << "Вхідні параметри:\n";
    std::cout << "  Частота: " << in.freq_mhz << " МГц (λ = " << res.wavelength_m << " м)\n";
    std::cout << "  Висота штиря h: " << in.height_m << " м (" 
              << (in.height_m / res.wavelength_m) * 100.0 << "% λ)\n";
    std::cout << "  Радіус провідника: " << in.wire_radius_mm << " мм\n";
    std::cout << "  Потужність передавача: " << std::setprecision(0) << in.power_watts << " Вт\n";
    std::cout << std::setprecision(2);
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Параметри котушки та імпедансу:\n";
    std::cout << "  Ємність штиря C_ant: " << res.c_ant_pf << " пФ\n";
    std::cout << "  Реактивний опір X_C: -j" << res.x_c_ohm << " Ом\n";
    std::cout << "  Необхідна індуктивність L_coil: " << res.l_coil_uh << " мкГн\n";
    std::cout << "  Каркас D=" << in.coil_diam_cm << " см, довжина l=" << in.coil_len_cm 
              << " см  ⇒  " << res.turns_count << " витків\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Баланс опорів та ККД:\n";
    std::cout << "  Опір випромінювання R_рад: " << res.r_rad_ohm << " Ом\n";
    printf("  Опір втрат котушки R_котушки: %.2f Ом\n", res.r_coil_ohm);
    std::cout << "  Опір заземлення/кузова R_землі: " << in.ground_loss_ohm << " Ом\n";
    std::cout << "  Повний опір R_повн: " << res.r_total_ohm << " Ом\n";
    std::cout << "  ККД випромінювання η: " << res.efficiency_pct << " %\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Характеристики смуги та режими напруги:\n";
    std::cout << "  Добротність антени Q: " << std::setprecision(1) << res.q_ant << "\n";
    std::cout << "  Смуга пропускання BW (-3dB): " << res.bandwidth_khz << " кГц\n";
    std::cout << "  Теплові втрати на котушці: " << res.p_heat_watts << " Вт\n";
    std::cout << "  Пікова ВЧ-напруга V_peak: " << std::setprecision(0) << res.v_peak_volts 
              << " В (" << std::setprecision(2) << res.v_peak_volts / 1000.0 << " кВ)\n";
    std::cout << "========================================================\n";
}

int main() {
    AntennaInputs inputs{
        .freq_mhz = 7.10,
        .height_m = 1.80,
        .wire_radius_mm = 2.0,
        .ground_loss_ohm = 4.0,
        .coil_q = 200.0,
        .power_watts = 100.0,
        .coil_diam_cm = 5.0,
        .coil_len_cm = 8.0
    };

    auto result = LoadingCoilCalculator::calculate(inputs);

    if (result) {
        print_cpp_report(inputs, *result);
    } else {
        std::cerr << "Помилка: некоректні вхідні параметри для розрахунку!\n";
        return 1;
    }

    return 0;
}
```
:::

---

### Порівняльний аналіз реалізацій мовами C та C++

Обидва варіанти коду реалізують ідентичні формули електродинаміки, але демонструють фундаментально різні підходи до архітектури програмного забезпечення.

1. **Обробка помилок та безпека типів:**
   - **У реалізації на C** обробка помилок виконується через повернення цілочисельних кодів статусу (`0` — успіх, від'ємні значення — помилка) та передачу вказівників на структури `const AntennaInputs*` і `AntennaResults*`. Це класичний системний стиль C, що вимагає явних перевірок `if (!in || !out)` в кожній функції.
   - **У реалізації на C++23** використовується сучасний тип `std::expected<AntennaResults, CalcError>`. Функція повертає або валідний результат, або структуровану помилку з переліку `CalcError`, виключаючи використання винятків (*exceptions*) та сирих вказівників. Позначка `[[nodiscard]]` гарантує, що розробник не зможе мовчки проігнорувати повернутий результат.

2. **Математична точність та стандарти:**
   - У C++ застосовуються строго типізовані математичні константи стандарту C++20 із заголовочного файлу `<numbers>`: `std::numbers::pi` та `std::numbers::sqrt2`. У C-версії застосовано макрос `M_PI` з макрозахистом `#ifndef M_PI`.
   - Застосування `constexpr` у C++ гарантує, що константи швидкості світла `c_speed` та електричної сталої `eps0` обчислюються під час компіляції без жодних витрат ресурсів у рантаймі.

---

### Інженерний аналіз результатів розрахунку

Запуск обчислювального модуля для автомобільної антени довжиною 1.8 м на частоті 7.1 МГц дає важливі висновки для практичного проєктування:

- **Індуктивність 29.11 мкГн та 22 витки:**  
  Намотування 22 витків дроту діаметром 1.5–2 мм на 5-сантиметровому фторопластовому каркасі формує котушку довжиною 8 см, яка точно компенсує ємність штиря 17.26 пФ.
- **Драматичний дисбаланс опорів (R_рад = 2.86 Ом проти R_втрат = 10.49 Ом):**  
  Опір випромінювання становить всього **21.4%** від загального опору системи. Зі ста ватів вхідної потужності лише **21.4 Вт** випромінюються в простір як корисна радіохвиля.
- **Тепловий режим 48.6 Вт:**  
  Майже половина всієї потужності передавача (**48.6 Вт**) перетворюється на тепло безпосередньо у котушці. При виборі тонкого дроту каркас швидко перегріється та розплавиться.
- **Високовольтний бар'єр 5.03 кВ:**  
  Пікова ВЧ-напруга понад 5 кіловольт вимагає проміжку між витками котушки не менше 2–3 мм для запобігання дуговому пробою в сиру погоду.

---

### Пастки та інженерні нюанси при реалізації

1. **Власна ємність витків котушки**:  
   При великій кількості витків паразитна ємність між витками створює паралельний резонанс. Якщо частота паралельного резонансу котушки наблизиться до робочої частоти `f₀`, котушка почне діяти як загороджувальний фільтр із величезними втратами. Відстань між витками (крок намотки `s`) повинна становити не менше `1.5 – 2` діаметрів дроту.

2. **Скін-ефект та ефект близькості (Proximity effect)**:  
   Високочастотний струм протікає лише у тонкому поверхневому шарі провідника (глибина скін-шару для міді на 7 МГц становить всього `24 мкм`). Використання багатожильного ізольованого дроту (ліцендрату) або посрібленої мідної трубки суттєво піднімає добротність `Q_coil` з `100` до `350–400`, зменшуючи втрати нагріву майже вдвічі.
