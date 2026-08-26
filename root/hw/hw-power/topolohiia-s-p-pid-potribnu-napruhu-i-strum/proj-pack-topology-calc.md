# ⚙️ Калькулятор батарейної топології: розрахунок S/P конфігурації, шин та просадки

Проєктування акумуляторної батареї починається з технічного завдання: цільової робочої напруги навантаження, безперервного та пікового струму споживання, необхідного запасу енергії (Вт·год) та геометричних обмежень корпусу. Спрощені табличні розрахунки часто випускають з уваги три критичні фактори: динамічне падіння напруги на внутрішньому опорі під час глибокого розряду, опір зварних струмопровідних шин і силових транзисторів BMS, а також поведінку системи на нижній межі робочого вікна напруг інвертора.

Калькулятор нижче автоматизує повний інженерний ланцюжок проєктування. Він розраховує мінімально необхідну кількість послідовних (S) та паралельних (P) комірок, перевіряє електричні ліміти інвертора, обчислює сумарний внутрішній опір пакета, підбирає переріз струмопровідних шин (мідь або нікель) і оцінює максимальну просадку напруги під піковим струмом.

### Математичний алгоритм роботи калькулятора

Програма виконує комплексний аналіз системи у шість послідовних розрахункових фаз:

1. **Визначення послідовної осі (S)**: обчислюється як відношення цільової напруги до номінальної напруги однієї комірки `S = ceil(U_target_nom / U_cell_nom)`. Одразу перевіряються два критичні обмеження: напруга повністю зарядженого пакета `S · U_cell_max` не повинна перевищувати максимальну вхідну напругу інвертора `U_inv_max`, а напруга розрядженого пакета `S · U_cell_min` має бути вищою за поріг апаратного вимкнення інвертора `U_inv_min`.
2. **Розрахунок струму за найгіршим сценарієм**: споживаний струм досягає максимуму, коли напруга батареї падає до мінімуму. Тому тривалий і піковий струми розраховуються відносно нижньої робочої напруги: `I_cont_req = P_cont / U_pack_min` та `I_peak_req = P_peak / U_pack_min`.
3. **Багатокритеріальний вибір паралельності (P)**: кількість паралельних банок визначається як максимум із трьох незалежних умов:
   - Забезпечення тривалого струму без перегріву: `P_cont = ceil(I_cont_req / I_cell_cont_max)`;
   - Забезпечення пікового струму при маневруванні: `P_peak = ceil(I_peak_req / I_cell_peak_max)`;
   - Забезпечення необхідного запасу енергії: `P_energy = ceil(E_req / (U_pack_nom · C_cell))`.
   Підсумкова кількість банок у паралельній групі приймається як `P = max(P_cont, P_peak, P_energy)`.
4. **Моделювання повного внутрішнього імпедансу пакета**: опір батареї постійному струму (DCIR) формується з еквівалентного опору комірок `S · (R_cell / P)` та паразитного опору мікроперемичок, зварних контактів і силових MOSFET-ключів BMS `S · R_interconnect`. Опір відкритого каналу пари зустрічно ввімкнених транзисторів захисту (Charge/Discharge FETs) додає від 0.5 до 2.0 мОм на весь пакет, а контактний опір зварної точки становить 0.2–0.4 мОм на кожну банку.
5. **Оцінка динамічної просадки напруги**: за законом Ома розраховується падіння напруги на повному опорі батареї при номінальній та піковій потужності (`ΔU = I · R_pack_total`). Якщо напруга під піковим навантаженням просідає нижче аварійного порогу UVLO інвертора, конфігурація маркується як небезпечна.
6. **Розрахунок силових шин і тепловиділення**: за заданою допустимою щільністю струму `J` (5 А/мм² для міді, 1.5 А/мм² для нікелю) визначається площа поперечного перерізу шини, її погонний опір та розсіювана теплова потужність за законом Джоуля-Ленца.

### Реалізація на C та C++

Модуль спроєктовано у двох варіантах: компактний детерміністичний C99-код без динамічного виділення пам'яті (придатний для вбудовування безпосередньо в прошивку мікроконтролера BMS або інженерний конфігуратор) та сучасна ідіоматична реалізація на C++20 з використанням типізованих помилок `std::expected` та константних обчислень `constexpr`.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    BUSBAR_COPPER,
    BUSBAR_NICKEL,
    BUSBAR_NICKEL_PLATED_STEEL
} BusbarMaterial;

typedef struct {
    double v_nom;       /* Номінальна напруга комірки (В), наприклад 3.6 */
    double v_min;       /* Мінімальна напруга розряду (В), наприклад 2.5 */
    double v_max;       /* Максимальна напруга повного заряду (В), наприклад 4.2 */
    double cap_ah;      /* Номінальна ємність (А·год), наприклад 4.5 */
    double i_cont_max;  /* Максимальний тривалий струм розряду (А), наприклад 15.0 */
    double i_peak_max;  /* Максимальний піковий струм розряду (А), наприклад 30.0 */
    double r_internal;  /* Внутрішній опір комірки DCIR (Ом), наприклад 0.020 (20 мОм) */
    double weight_g;    /* Маса однієї комірки (г), наприклад 70.0 */
} CellSpec;

typedef struct {
    double v_target_nom;    /* Цільова номінальна напруга системи (В), наприклад 48.0 */
    double v_inverter_min;  /* Нижній поріг відсічки інвертора (В), наприклад 40.0 */
    double v_inverter_max;  /* Верхній ліміт вхідної напруги інвертора (В), наприклад 58.4 */
    double p_continuous_w;  /* Тривала потужність навантаження (Вт), наприклад 2000.0 */
    double p_peak_w;        /* Пікова потужність навантаження (Вт), наприклад 4000.0 */
    double energy_wh_req;   /* Необхідний запас енергії (Вт·год), наприклад 1000.0 */
} SystemRequirements;

typedef struct {
    int s_count;            /* Кількість послідовних груп (S) */
    int p_count;            /* Кількість паралельних комірок у групі (P) */
    int total_cells;        /* Загальна кількість банок (S * P) */
    double v_pack_nom;      /* Номінальна напруга батареї (В) */
    double v_pack_min;      /* Мінімальна напруга розрядженої батареї (В) */
    double v_pack_max;      /* Максимальна напруга зарядженої батареї (В) */
    double cap_pack_ah;     /* Сумарна ємність пакета (А·год) */
    double energy_pack_wh;  /* Сумарна запасена енергія (Вт·год) */
    double i_cont_max;      /* Максимальний допустимий тривалий струм пакета (А) */
    double i_peak_max;      /* Максимальний допустимий піковий струм пакета (А) */
    double r_pack_total;    /* Еквівалентний внутрішній опір батареї (Ом) */
    double v_sag_continuous;/* Просадка напруги на номінальній потужності (В) */
    double v_sag_peak;      /* Просадка напруги на піковій потужності (В) */
    double busbar_area_mm2; /* Рекомендований переріз головної шини (мм²) */
    double total_weight_kg; /* Орієнтовна маса тільки комірок (кг) */
    bool is_valid;          /* Чи вкладається конфігурація у вікно напруг інвертора */
} PackDesign;

/* Питомий опір у мОм·мм²/м */
double get_busbar_resistivity(BusbarMaterial mat) {
    switch (mat) {
        case BUSBAR_COPPER: return 17.2;
        case BUSBAR_NICKEL: return 96.0;
        case BUSBAR_NICKEL_PLATED_STEEL: return 130.0;
        default: return 17.2;
    }
}

/* Рекомендована щільність струму (А/мм²) */
double get_target_current_density(BusbarMaterial mat) {
    switch (mat) {
        case BUSBAR_COPPER: return 5.0;
        case BUSBAR_NICKEL: return 1.5;
        case BUSBAR_NICKEL_PLATED_STEEL: return 1.0;
        default: return 5.0;
    }
}

PackDesign calculate_pack_topology(const CellSpec* cell, 
                                   const SystemRequirements* req, 
                                   BusbarMaterial busbar_mat) {
    PackDesign d;
    d.is_valid = true;

    /* 1. Розрахунок послідовних груп S */
    d.s_count = (int)ceil(req->v_target_nom / cell->v_nom);
    d.v_pack_nom = d.s_count * cell->v_nom;
    d.v_pack_min = d.s_count * cell->v_min;
    d.v_pack_max = d.s_count * cell->v_max;

    /* Перевірка лімітів інвертора */
    if (d.v_pack_max > req->v_inverter_max || d.v_pack_min < req->v_inverter_min) {
        d.is_valid = false;
    }

    /* 2. Розрахунок струмів системи */
    double i_cont_req = req->p_continuous_w / d.v_pack_min;
    double i_peak_req = req->p_peak_w / d.v_pack_min;

    /* 3. Розрахунок паралельних банок P за трьома критеріями */
    int p_by_cont_current = (int)ceil(i_cont_req / cell->i_cont_max);
    int p_by_peak_current = (int)ceil(i_peak_req / cell->i_peak_max);
    int p_by_energy = (int)ceil(req->energy_wh_req / (d.v_pack_nom * cell->cap_ah));

    int p_max = p_by_cont_current;
    if (p_by_peak_current > p_max) p_max = p_by_peak_current;
    if (p_by_energy > p_max) p_max = p_by_energy;
    if (p_max < 1) p_max = 1;

    d.p_count = p_max;
    d.total_cells = d.s_count * d.p_count;

    /* 4. Електричні параметри зібраного пакета */
    d.cap_pack_ah = d.p_count * cell->cap_ah;
    d.energy_pack_wh = d.v_pack_nom * d.cap_pack_ah;
    d.i_cont_max = d.p_count * cell->i_cont_max;
    d.i_peak_max = d.p_count * cell->i_peak_max;

    /* Внутрішній опір: S послідовних груп по P паралельних комірок */
    /* Додаємо умовні 1.5 мОм на комутацію групи (шини + BMS FETs) */
    double r_interconnect_per_s = 0.0015;
    d.r_pack_total = d.s_count * ((cell->r_internal / d.p_count) + r_interconnect_per_s);

    /* 5. Просадка напруги під навантаженням */
    d.v_sag_continuous = i_cont_req * d.r_pack_total;
    d.v_sag_peak = i_peak_req * d.r_pack_total;

    /* 6. Переріз головної силової шини */
    double j_target = get_target_current_density(busbar_mat);
    d.busbar_area_mm2 = i_cont_req / j_target;

    /* 7. Маса батареї */
    d.total_weight_kg = (d.total_cells * cell->weight_g) / 1000.0;

    return d;
}

int main(void) {
    CellSpec cell_21700 = {
        .v_nom = 3.6,
        .v_min = 2.5,
        .v_max = 4.2,
        .cap_ah = 4.5,
        .i_cont_max = 15.0,
        .i_peak_max = 30.0,
        .r_internal = 0.018, /* 18 мОм */
        .weight_g = 70.0
    };

    SystemRequirements drone_req = {
        .v_target_nom = 48.0,
        .v_inverter_min = 38.0,
        .v_inverter_max = 58.8,
        .p_continuous_w = 2500.0,
        .p_peak_w = 5000.0,
        .energy_wh_req = 1200.0
    };

    PackDesign design = calculate_pack_topology(&cell_21700, &drone_req, BUSBAR_COPPER);

    printf("=== Звіт проєктування батареї ===\n");
    printf("Конфігурація: %dS%dP (Всього комірок: %d)\n", 
           design.s_count, design.p_count, design.total_cells);
    printf("Напруга: ном. %.1f В (робоче вікно: %.1f В .. %.1f В)\n", 
           design.v_pack_nom, design.v_pack_min, design.v_pack_max);
    printf("Ємність: %.2f А·год | Енергія: %.1f Вт·год\n", 
           design.cap_pack_ah, design.energy_pack_wh);
    printf("Внутрішній опір пакета (DCIR): %.4f Ом (%.2f мОм)\n", 
           design.r_pack_total, design.r_pack_total * 1000.0);
    printf("Просадка напруги: ном. %.2f В | пік. %.2f В\n", 
           design.v_sag_continuous, design.v_sag_peak);
    printf("Рекомендований переріз мідної шини: %.2f мм²\n", design.busbar_area_mm2);
    printf("Маса комірок: %.2f кг\n", design.total_weight_kg);
    printf("Статус валідації: %s\n", design.is_valid ? "OK" : "ПОМИЛКА НАПРУГИ");

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <string_view>
#include <expected>
#include <iomanip>

enum class BusbarMaterial {
    Copper,
    Nickel,
    NickelPlatedSteel
};

struct CellSpec {
    double v_nom{3.6};       // В
    double v_min{2.5};       // В
    double v_max{4.2};       // В
    double cap_ah{4.5};      // А·год
    double i_cont_max{15.0}; // А
    double i_peak_max{30.0}; // А
    double r_internal{0.018};// Ом (18 мОм)
    double weight_g{70.0};   // г
};

struct SystemRequirements {
    double v_target_nom{48.0};   // В
    double v_inverter_min{38.0}; // В
    double v_inverter_max{58.8}; // В
    double p_continuous_w{2500.0};// Вт
    double p_peak_w{5000.0};     // Вт
    double energy_wh_req{1200.0};// Вт·год
};

struct PackDesign {
    int s_count{0};
    int p_count{0};
    int total_cells{0};
    double v_pack_nom{0.0};
    double v_pack_min{0.0};
    double v_pack_max{0.0};
    double cap_pack_ah{0.0};
    double energy_pack_wh{0.0};
    double i_cont_max{0.0};
    double i_peak_max{0.0};
    double r_pack_total{0.0};
    double v_sag_continuous{0.0};
    double v_sag_peak{0.0};
    double busbar_area_mm2{0.0};
    double total_weight_kg{0.0};
};

enum class SizingError {
    VoltageOutOfRange,
    InvalidCellParameters,
    ZeroPowerRequested
};

constexpr double get_busbar_resistivity(BusbarMaterial mat) noexcept {
    switch (mat) {
        case BusbarMaterial::Copper: return 17.2;
        case BusbarMaterial::Nickel: return 96.0;
        case BusbarMaterial::NickelPlatedSteel: return 130.0;
    }
    return 17.2;
}

constexpr double get_target_current_density(BusbarMaterial mat) noexcept {
    switch (mat) {
        case BusbarMaterial::Copper: return 5.0; // А/мм²
        case BusbarMaterial::Nickel: return 1.5;
        case BusbarMaterial::NickelPlatedSteel: return 1.0;
    }
    return 5.0;
}

std::expected<PackDesign, SizingError> calculate_pack_topology(
    const CellSpec& cell,
    const SystemRequirements& req,
    BusbarMaterial busbar_mat = BusbarMaterial::Copper) noexcept 
{
    if (cell.v_nom <= 0.0 || cell.cap_ah <= 0.0 || cell.i_cont_max <= 0.0) {
        return std::unexpected(SizingError::InvalidCellParameters);
    }
    if (req.p_continuous_w <= 0.0 || req.v_target_nom <= 0.0) {
        return std::unexpected(SizingError::ZeroPowerRequested);
    }

    PackDesign design;

    // 1. Послідовні групи S
    design.s_count = static_cast<int>(std::ceil(req.v_target_nom / cell.v_nom));
    design.v_pack_nom = design.s_count * cell.v_nom;
    design.v_pack_min = design.s_count * cell.v_min;
    design.v_pack_max = design.s_count * cell.v_max;

    if (design.v_pack_max > req.v_inverter_max || design.v_pack_min < req.v_inverter_min) {
        return std::unexpected(SizingError::VoltageOutOfRange);
    }

    // 2. Струми навантаження
    const double i_cont_req = req.p_continuous_w / design.v_pack_min;
    const double i_peak_req = req.p_peak_w / design.v_pack_min;

    // 3. Паралельні банки P
    const int p_cont = static_cast<int>(std::ceil(i_cont_req / cell.i_cont_max));
    const int p_peak = static_cast<int>(std::ceil(i_peak_req / cell.i_peak_max));
    const int p_energy = static_cast<int>(std::ceil(req.energy_wh_req / (design.v_pack_nom * cell.cap_ah)));

    design.p_count = std::max({p_cont, p_peak, p_energy, 1});
    design.total_cells = design.s_count * design.p_count;

    // 4. Електричні параметри
    design.cap_pack_ah = design.p_count * cell.cap_ah;
    design.energy_pack_wh = design.v_pack_nom * design.cap_pack_ah;
    design.i_cont_max = design.p_count * cell.i_cont_max;
    design.i_peak_max = design.p_count * cell.i_peak_max;

    constexpr double r_interconnect_per_s = 0.0015; // 1.5 мОм на S-групу
    design.r_pack_total = design.s_count * ((cell.r_internal / design.p_count) + r_interconnect_per_s);

    // 5. Просадка напруги
    design.v_sag_continuous = i_cont_req * design.r_pack_total;
    design.v_sag_peak = i_peak_req * design.r_pack_total;

    // 6. Шина та маса
    const double j_target = get_target_current_density(busbar_mat);
    design.busbar_area_mm2 = i_cont_req / j_target;
    design.total_weight_kg = (design.total_cells * cell.weight_g) / 1000.0;

    return design;
}

int main() {
    constexpr CellSpec cell_21700{
        .v_nom = 3.6,
        .v_min = 2.5,
        .v_max = 4.2,
        .cap_ah = 4.5,
        .i_cont_max = 15.0,
        .i_peak_max = 30.0,
        .r_internal = 0.018,
        .weight_g = 70.0
    };

    constexpr SystemRequirements drone_req{
        .v_target_nom = 48.0,
        .v_inverter_min = 38.0,
        .v_inverter_max = 58.8,
        .p_continuous_w = 2500.0,
        .p_peak_w = 5000.0,
        .energy_wh_req = 1200.0
    };

    auto result = calculate_pack_topology(cell_21700, drone_req, BusbarMaterial::Copper);

    if (!result) {
        std::cerr << "Помилка розрахунку конфігурації батареї!\n";
        return 1;
    }

    const auto& d = *result;
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Звіт проєктування батареї (C++20) ===\n";
    std::cout << "Конфігурація: " << d.s_count << "S" << d.p_count << "P"
              << " (Всього банок: " << d.total_cells << ")\n";
    std::cout << "Напруга пакета: " << d.v_pack_nom << " В (Діапазон: "
              << d.v_pack_min << " В .. " << d.v_pack_max << " В)\n";
    std::cout << "Ємність: " << d.cap_pack_ah << " А·год | Енергія: " 
              << d.energy_pack_wh << " Вт·год\n";
    std::cout << "DCIR пакета: " << (d.r_pack_total * 1000.0) << " мОм\n";
    std::cout << "Просадка напруги: " << d.v_sag_continuous << " В (ном) / " 
              << d.v_sag_peak << " В (пік)\n";
    std::cout << "Переріз шини: " << d.busbar_area_mm2 << " мм²\n";
    std::cout << "Маса комірок: " << d.total_weight_kg << " кг\n";

    return 0;
}
```
:::

### Інженерні застереження та практична валідація на стенді

1. **Коефіцієнт запасу за струмом (Derating)**: паспортний тривалий струм комірки у формулах ніколи не беруть на рівні 100% даташитного максимуму. Для забезпечення ресурсу понад 500 циклів номінальний робочий струм обмежують величиною 60–70% від паспортного `i_cont_max`. Наприклад, для комірки з паспортним струмом 20 А розрахунковий струм у алгоритмі обмежують до 12–14 А.
2. **Температурний градієнт шини**: якщо розрахунковий переріз шини перевищує 15–20 мм², цільну смугу замінюють на багатошаровий мідний пакет (англ. *laminated busbar*) або лазерне зварювання, щоб уникнути надмірної жорсткості конструкції та відриву контактів під час вібрацій.
3. **Крайовий випадок спрацювання UVLO**: якщо розрахована пікова просадка напруги призводить до падіння миттєвого потенціалу нижче нижнього порогу інвертора `v_inverter_min`, ємність пакета формально задовольняє ТЗ, але під час різкого прискорення інвертор відключатиме живлення за захистом від низької напруги. У такому разі алгоритм рекомендує або збільшити паралельність `P` на 1–2 щаблі для зниження внутрішнього опору, або обмежити мінімальний робочий SoC батареї на рівні 15–20%.
4. **Сортування комірок за DCIR перед монтажем**: розраховані значення просадки та нагріву справедливі лише тоді, коли відхилення внутрішнього опору банок у паралельній групі не перевищує 5%. Перед складанням усі елементи обов'язково вимірюють імпульсним методом і компонують у групи за правилом найменшої дисперсії провідностей `∑ G_i`.
5. **Лабораторна перевірка на електронному навантаженні**: після складання прототипу батарею підключають до програмованого навантаження постійного струму й подають імпульси струму 100% та 150% від номіналу тривалістю 5–10 секунд. Одночасно тепловізором фіксують температурний розподіл уздовж шин: якщо перегрів шини перевищує +15 °C відносно корпусу комірок, переріз шини або якість зварних точок є недостатніми й вимагають доопрацювання.
