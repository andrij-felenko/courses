# ⚙️ Програма аналізу вимірювань TLM та вилучення параметрів контакту

У сучасній мікроелектроніці та промисловому виробництві напівпровідникових приладів створення надійних омічних контактів із низьким опором вимагає постійного метрологічного контролю кожної виготовленої кристалічної пластини. Основним і безальтернативним методом такої оцінки в індустрії є метод трансферної лінії (*Transfer Line Method*, TLM). 

Під час випробування експериментатор або автоматизований зондовий стенд (*Wafer Prober*) вимірює електричний опір між серією однакових прямокутних металевих площадок із різними відстанями між ними. Отримані експериментальні дані піддаються математичній обробці за допомогою лінійної регресії, що дає змогу відокремити власний опір об'єму напівпровідника від опору самого контакту.

Нижче подано практичний алгоритм та багатомовну реалізацію програми для автоматичної обробки експериментальних масивів вимірювань, перевірки фізичної коректності вимірів, оцінки погрешностей та вилучення чотирьох ключових параметрів: шарового опору напівпровідника `R_sh`, опору одного контакту `R_c`, довжини перенесення струму під контактом `L_T` та питомого опору контакту `rho_c`.

## 1. Метрологічні умови та чотириточкова схема вимірювання

Перед проведенням обчислень важливо врахувати фізичні особливості експериментальної установки. Звичайне двоточкове вимірювання опору притиснутими вимірювальними голками дає суттєву систематичну похибку, оскільки опір самого металевого зонда та контакту голка-металізація (типово `0.5 – 2.0 Ом`) додається до вимірюваного опору.

Щоб виключити опір щупів, вимірювання TLM виконують за **чотириточковою схемою Кельвіна** (*4-point Kelvin sensing*):
- Через одну пару зовнішніх голок від стабілізованого джерела струму подається тестовий мікрострум `I_test` (типово `100 мкА – 10 мА`).
- Через другу пару внутрішніх голок з високим вхідним опором (понад `10⁹ Ом`) вольтметром вимірюється спад напруги `V_meas`.
- Опір обчислюється як `R_T = V_meas / I_test`. Оскільки струм через вольтметричні голки практично не тече, опір зондів не вносить похибки у результат.

Також обов'язковим є перевірка на ізоляцію напівпровідникової мези (*mesa isolation*). Легований шар навколо контактних площадок має бути повністю витравлений до ізолювальної підкладки. Якщо стікання струму відбувається у бокових напрямках поза мезою, розраховане значення `rho_c` буде заниженим через спотворення геометричного фактора.

## 2. Алгоритм та математична модель обробки

Програма приймає на вхід геометричні розміри тестової контактної площадки — її ширину `W` та довжину `L` (у мікрометрах), а також два експериментальні масиви даних одинакової довжини:
1. Вектор зазорів між контактами `d = [d₁, d₂, ..., dₙ]` (у мікрометрах);
2. Вектор відповідних виміряних опорів `R_T = [R_T1, R_T2, ..., R_Tn]` (у Омах).

Для побудови лінійної залежності `R_T(d) = A · d + B` застосовується класичний метод найменших квадратів (МНК). Обчислюються чотири фундаментальні математичні суми по всіх `n` виміряних експериментальних точках:

```
sum_x = ∑ d_i,   sum_y = ∑ R_Ti,   sum_xx = ∑ (d_i)²,   sum_xy = ∑ (d_i · R_Ti)
```

Звідси коефіцієнти прямої лінійної регресії визначаються за виразами:

```
A = (n · sum_xy - sum_x · sum_y) / (n · sum_xx - (sum_x)²)       [нахил прямої]

B = (sum_y · sum_xx - sum_x · sum_xy) / (n · sum_xx - (sum_x)²)   [відсічка на Y]
```

З фізичних міркувань нахил прямої `A = R_sh / W` та вільний член `B = 2 · R_c` мусять бути строго додатними величинами. Якщо в результаті розрахунку нахил або відсічка виявляються від'ємними чи нульовими, це свідчить про наявність нелінійностей, пробій ізолювальної мези, або поганий зондовий контакт під час вимірювань.

Після знаходження додатних коефіцієнтів `A` та `B` програма розраховує фізичні параметри омічного контакту:

```
R_sh = A · W                             [шаровий опір напівпровідника, Ом/кв]

R_c = B / 2                              [опір одного контакту, Ом]

L_T = B / (2 · A)                        [довжина перенесення струму, см]

rho_c = R_c · W · L_T = B² · W / (4 · A) [питомий опір контакту, Ом·см²]
```

Для додаткового контролю якості вимірювань обчислюється коефіцієнт детермінації `R²`, який показує відсоток дисперсії, пояснений лінійною моделлю:

```
y_mean = (1 / n) · ∑ R_Ti                [середнє значення виміряного опору]

ss_tot = ∑ (R_Ti - y_mean)²             [загальна сума квадратів відхилень]

ss_res = ∑ (R_Ti - (A · d_i + B))²        [залишкова сума квадратів відхилень]

R² = 1 - (ss_res / ss_tot)               [коефіцієнт детермінації]
```

Значення `R² > 0.99` вважається підтвердженням високої точності вимірювального експерименту. Якщо `R² < 0.95`, це вказує на наявність системних похибок (наприклад, локального розігріву струмом чи деформації контактних площадок).

## 3. Аналіз ефекту скупчення струму та межі застосовності

Після розрахунку довжини перенесення `L_T` програма виконує фізичну перевірку геометрії контакту:
- Якщо геометрична довжина контакту `L ≥ 2 · L_T`, контакт вважається **довгим**. Формула `rho_c = R_c · W · L_T` є строго справедливою.
- Якщо `L < 2 · L_T`, контакт є **коротким**. Струм використовує всю площу контакту, і точне значення `rho_c` обчислюється з урахуванням поправки на гіперболічний котангенс:

```
rho_c_exact = R_c · W · L_T · tanh(L / L_T)
```

Ця поправка автоматично розраховується алгоритмом для забезпечення високої точності при аналізі субмікронних контактних площадок сучасних транзисторів.

## 4. Покроковий чисельний приклад обробки даних

Для ілюстрації роботи алгоритму розглянемо конкретний практичний приклад обробки даних вимірювання омічних контактів металізації `Ti/Al/Ni/Au` до шарового $n-GaN$.

**Вхідні геометричні параметри:**
- Ширина контактної площадки: `W = 100.0 мкм = 0.010 см`;
- Довжина контактної площадки: `L = 20.0 мкм = 0.002 см`.

**Експериментальна таблиця вимірюваних зазорів та опорів:**
```
--------------------------------------------------------------
Номер виміру i | Зазор d_i (мкм) | Виміряний опір R_Ti (Ом)
--------------------------------------------------------------
      1        |      5.0        |          12.4
      2        |     10.0        |          18.2
      3        |     15.0        |          24.1
      4        |     20.0        |          30.0
      5        |     25.0        |          35.9
--------------------------------------------------------------
```

**Крок 1. Переведення зазорів у сантиметри:**
`d = [0.0005, 0.0010, 0.0015, 0.0020, 0.0025] см`.

**Крок 2. Обчислення сум МНК (`n = 5`):**
- `sum_x = 0.0075 см`;
- `sum_y = 120.6 Ом`;
- `sum_xx = 0.00001375 см²`;
- `sum_xy = 0.21045 Ом·см`.

**Крок 3. Обчислення коефіцієнтів регресії:**
- Знаменник: `denom = 5 · (0.00001375) - (0.0075)² = 0.00006875 - 0.00005625 = 0.0000125 см²`.
- Нахил `A`: `A = (5 · 0.21045 - 0.0075 · 120.6) / 0.0000125 = (1.05225 - 0.9045) / 0.0000125 = 11820.0 Ом/см`.
- Відсічка `B`: `B = (120.6 · 0.00001375 - 0.0075 · 0.21045) / 0.0000125 = (0.00165825 - 0.001578375) / 0.0000125 = 6.39 Ом`.

**Крок 4. Розрахунок підсумкових параметрів контакту:**
- Шаровий опір: `R_sh = A · W = 11820.0 · 0.010 = 118.20 Ом/кв`.
- Опір одного контакту: `R_c = B / 2 = 6.39 / 2 = 3.195 Ом`.
- Довжина перенесення струму: `L_T = B / (2 · A) = 6.39 / (2 · 11820.0) = 0.0002703 см = 2.703 мкм`.
- Перевірка критерію довгого контакту: `L / L_T = 20.0 / 2.703 = 7.40 ≥ 2` (контакт є довгим).
- Питомий опір контакту: `rho_c = R_c · W · L_T = 3.195 · 0.010 · 0.0002703 = 8.636e-6 Ом·см²`.
- Коефіцієнт детермінації: `R² = 0.9999` (відмінний лінійний зв'язок).

## 5. Багатомовна реалізація програми

:::tabs
```py
import math
from typing import List, Dict, Optional

class TLMAnalyzer:
    """Клас аналізу даних вимірювань TLM та екстраполяції параметрів контакту."""
    
    def __init__(self, contact_width_um: float, contact_length_um: float):
        """
        :param contact_width_um: Ширина контактної площадки W у мікрометрах.
        :param contact_length_um: Довжина контактної площадки L у мікрометрах.
        """
        if contact_width_um <= 0 or contact_length_um <= 0:
            raise ValueError("Геометричні розміри контактів повинні бути додатними.")
        self.w_cm = contact_width_um * 1e-4   # Переведення мкм -> см
        self.l_cm = contact_length_um * 1e-4   # Переведення мкм -> см

    def analyze(self, spacings_um: List[float], resistances_ohm: List[float]) -> Optional[Dict[str, float]]:
        """
        Обробляє масиви відстаней d [мкм] та опорів R_T [Ом].
        :return: Словник з розрахованими параметрами або None у разі помилки.
        """
        n = len(spacings_um)
        if n < 2 or n != len(resistances_ohm):
            return None

        # Переведення зазорів d з мкм у см
        d_cm = [d * 1e-4 for d in spacings_um]

        # Обчислення сум МНК для лінійного рівняння Y = A*X + B
        sum_x = sum(d_cm)
        sum_y = sum(resistances_ohm)
        sum_xx = sum(x * x for x in d_cm)
        sum_xy = sum(x * y for x, y in zip(d_cm, resistances_ohm))

        denom = n * sum_xx - sum_x * sum_x
        if abs(denom) < 1e-15:
            return None

        slope = (n * sum_xy - sum_x * sum_y) / denom      # A = R_sh / W
        intercept = (sum_y * sum_xx - sum_x * sum_xy) / denom # B = 2 * R_c

        # Фізична валідація: нахил та відсічка повинні бути строго додатними
        if slope <= 0.0 or intercept <= 0.0:
            return None

        r_sh = slope * self.w_cm                            # Ом/кв
        r_c = intercept / 2.0                              # Ом
        l_t_cm = intercept / (2.0 * slope)                 # см
        
        # Перевірка на короткий/довгий контакт та обчислення точного rho_c
        ratio = self.l_cm / l_t_cm
        if ratio < 2.0:
            rho_c = r_c * self.w_cm * l_t_cm * math.tanh(ratio)
        else:
            rho_c = r_c * self.w_cm * l_t_cm               # Ом·см²

        # Обчислення коефіцієнта детермінації R^2
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in resistances_ohm)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(d_cm, resistances_ohm))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return {
            "r_sh_ohm_sq": r_sh,
            "r_c_ohm": r_c,
            "l_t_um": l_t_cm * 1e4,
            "rho_c_ohm_cm2": rho_c,
            "r2_score": r2,
            "l_ratio": ratio
        }

if __name__ == "__main__":
    analyzer = TLMAnalyzer(contact_width_um=100.0, contact_length_um=20.0)
    # Набір даних: зазори d = [5, 10, 15, 20, 25] мкм, виміряні R_T [Ом]
    d_data = [5.0, 10.0, 15.0, 20.0, 25.0]
    r_data = [12.4, 18.2, 24.1, 30.0, 35.9]

    res = analyzer.analyze(d_data, r_data)
    if res:
        print(f"R_sh    = {res['r_sh_ohm_sq']:.2f} Ohm/sq")
        print(f"R_c     = {res['r_c_ohm']:.3f} Ohm")
        print(f"L_T     = {res['l_t_um']:.3f} um")
        print(f"rho_c   = {res['rho_c_ohm_cm2']:.3e} Ohm*cm^2")
        print(f"R^2     = {res['r2_score']:.4f}")
        print(f"L / L_T = {res['l_ratio']:.2f}")
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура збереження результатів аналізу TLM */
typedef struct {
    double r_sh_ohm_sq;   /* Шаровий опір напівпровідника [Ом/кв] */
    double r_c_ohm;        /* Опір одного контакту [Ом] */
    double l_t_um;         /* Довжина перенесення струму [мкм] */
    double rho_c_ohm_cm2;  /* Питомий опір контакту [Ом·см²] */
    double r2_score;       /* Якість лінійного наближення R^2 */
    double l_ratio;        /* Співвідношення L / L_T */
} tlm_result_t;

/**
 * Розраховує параметри TLM методом найменших квадратів.
 * @param d_um Масив відстаней між контактами [мкм]
 * @param r_ohm Масив виміряних опорів [Ом]
 * @param count Кількість експериментальних точок
 * @param w_um Ширина контакту W [мкм]
 * @param l_um Довжина контакту L [мкм]
 * @param out_res Вказівник на структуру для запису результату
 * @return true при успішному обчисленні, false при фізичній чи математичній помилці
 */
bool tlm_analyze(const double* d_um, const double* r_ohm, size_t count,
                 double w_um, double l_um, tlm_result_t* out_res) {
    if (!d_um || !r_ohm || !out_res || count < 2 || w_um <= 0.0 || l_um <= 0.0) {
        return false;
    }

    double w_cm = w_um * 1e-4;
    double l_cm = l_um * 1e-4;
    double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;

    for (size_t i = 0; i < count; ++i) {
        double x = d_um[i] * 1e-4; /* Переведення мкм у см */
        double y = r_ohm[i];
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }

    double denom = (double)count * sum_xx - sum_x * sum_x;
    if (fabs(denom) < 1e-15) {
        return false;
    }

    double slope = ((double)count * sum_xy - sum_x * sum_y) / denom;
    double intercept = (sum_y * sum_xx - sum_x * sum_xy) / denom;

    /* Фізична перевірка коректності знаків */
    if (slope <= 0.0 || intercept <= 0.0) {
        return false;
    }

    out_res->r_sh_ohm_sq = slope * w_cm;
    out_res->r_c_ohm = intercept / 2.0;
    double l_t_cm = intercept / (2.0 * slope);
    out_res->l_t_um = l_t_cm * 1e4;
    out_res->l_ratio = l_cm / l_t_cm;

    if (out_res->l_ratio < 2.0) {
        out_res->rho_c_ohm_cm2 = out_res->r_c_ohm * w_cm * l_t_cm * tanh(out_res->l_ratio);
    } else {
        out_res->rho_c_ohm_cm2 = out_res->r_c_ohm * w_cm * l_t_cm;
    }

    /* Розрахунок R^2 */
    double y_mean = sum_y / (double)count;
    double ss_tot = 0.0, ss_res = 0.0;
    for (size_t i = 0; i < count; ++i) {
        double x = d_um[i] * 1e-4;
        double y = r_ohm[i];
        double y_pred = slope * x + intercept;
        ss_tot += (y - y_mean) * (y - y_mean);
        ss_res += (y - y_pred) * (y - y_pred);
    }

    out_res->r2_score = (ss_tot > 0.0) ? (1.0 - ss_res / ss_tot) : 0.0;
    return true;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <optional>
#include <numeric>
#include <cmath>
#include <iomanip>

struct TlmResult {
    double r_sh_ohm_sq;   // Шаровий опір [Ом/кв]
    double r_c_ohm;        // Опір одного контакту [Ом]
    double l_t_um;         // Довжина перенесення [мкм]
    double rho_c_ohm_cm2;  // Питомий опір контакту [Ом·см²]
    double r2_score;       // Коефіцієнт детермінації R^2
    double l_ratio;        // Співвідношення L / L_T
};

class TlmAnalyzer {
public:
    constexpr TlmAnalyzer(double width_um, double length_um) noexcept
        : w_cm_(width_um * 1e-4), l_cm_(length_um * 1e-4) {}

    [[nodiscard]] std::optional<TlmResult> analyze(
        std::span<const double> spacings_um,
        std::span<const double> resistances_ohm) const {

        if (spacings_um.size() != resistances_ohm.size() || spacings_um.size() < 2) {
            return std::nullopt;
        }

        const auto n = static_cast<double>(spacings_um.size());
        double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;

        for (size_t i = 0; i < spacings_um.size(); ++i) {
            const double x = spacings_um[i] * 1e-4; // мкм -> см
            const double y = resistances_ohm[i];
            sum_x += x;
            sum_y += y;
            sum_xx += x * x;
            sum_xy += x * y;
        }

        const double denom = n * sum_xx - sum_x * sum_x;
        if (std::abs(denom) < 1e-15) {
            return std::nullopt;
        }

        const double slope = (n * sum_xy - sum_x * sum_y) / denom;
        const double intercept = (sum_y * sum_xx - sum_x * sum_xy) / denom;

        if (slope <= 0.0 || intercept <= 0.0) {
            return std::nullopt;
        }

        TlmResult res{};
        res.r_sh_ohm_sq = slope * w_cm_;
        res.r_c_ohm = intercept / 2.0;
        const double l_t_cm = intercept / (2.0 * slope);
        res.l_t_um = l_t_cm * 1e4;
        res.l_ratio = l_cm_ / l_t_cm;

        if (res.l_ratio < 2.0) {
            res.rho_c_ohm_cm2 = res.r_c_ohm * w_cm_ * l_t_cm * std::tanh(res.l_ratio);
        } else {
            res.rho_c_ohm_cm2 = res.r_c_ohm * w_cm_ * l_t_cm;
        }

        const double y_mean = sum_y / n;
        double ss_tot = 0.0, ss_res = 0.0;
        for (size_t i = 0; i < spacings_um.size(); ++i) {
            const double x = spacings_um[i] * 1e-4;
            const double y = resistances_ohm[i];
            const double y_pred = slope * x + intercept;
            ss_tot += (y - y_mean) * (y - y_mean);
            ss_res += (y - y_pred) * (y - y_pred);
        }

        res.r2_score = (ss_tot > 0.0) ? (1.0 - ss_res / ss_tot) : 0.0;
        return res;
    }

private:
    double w_cm_;
    double l_cm_;
};

int main() {
    TlmAnalyzer analyzer(100.0, 20.0);
    std::vector<double> d_um{5.0, 10.0, 15.0, 20.0, 25.0};
    std::vector<double> r_ohm{12.4, 18.2, 24.1, 30.0, 35.9};

    if (const auto res = analyzer.analyze(d_um, r_ohm)) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "R_sh    = " << res->r_sh_ohm_sq << " Ohm/sq\n";
        std::cout << "R_c     = " << std::setprecision(3) << res->r_c_ohm << " Ohm\n";
        std::cout << "L_T     = " << res->l_t_um << " um\n";
        std::cout << "rho_c   = " << std::scientific << res->rho_c_ohm_cm2 << " Ohm*cm^2\n";
        std::cout << "R^2     = " << std::fixed << std::setprecision(4) << res->r2_score << "\n";
        std::cout << "L / L_T = " << res->l_ratio << "\n";
    }
    return 0;
}
```
:::

## 6. Особливості реалізації різними мовами

- **Python-реалізація:** Використовує динамічний тип повернення через `Optional[Dict]` та стандартні засоби розпакування даних. Зручна для обробки лабораторних скриптів та швидкого аналізу у Jupyter Notebook під час наукових досліджень.
- **C-реалізація:** Забезпечує максимально виключний обчислювальний швидкісний опір для вбудованих автоматизованих вимірювальних систем стендів (ATE) без виділення пам'яті в купі (*zero-allocation*). Результати передаються через вказівник на структуру `tlm_result_t`.
- **C++-реалізація:** Застосовує сучасний стандарт C++20 із семантикою неволодіючих зрізів `std::span<const double>`, концептами незмінності, та безпечною обробкою помилок через `std::optional<TlmResult>` замість сирих вказівників чи системних кодів помилок.
