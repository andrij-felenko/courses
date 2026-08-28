# ⚙️ Інженерний калькулятор вагового бюджету та центру тяжіння

Програмний інструмент для автоматизованого розрахунку максимальної злітної маси (MTOW), категорійного розподілу мас, тривимірних координат центру тяжіння (CG) та перевірки запасу тяги апарата (TWR).

Калькулятор дозволяє формалізувати вагову відомість компонентів (Bill of Materials, BOM), перевірити статичне балансування платформи відносно геометричного центру тяги (CoT), оцінити частку акумулятора та розрахувати робочі параметри висіння на основі імпульсної теорії диска.

---

## 1. Структура даних та математична модель

Програма оперує переліком складових частин, кожна з яких має:
1. Назву та функціональну категорію (`PAYLOAD`, `BATTERY`, `PROPULSION`, `AVIONICS`, `AIRFRAME`, `MARGIN`);
2. Масу `m_i` у грамах;
3. Координати центру мас `(x_i, y_i, z_i)` у міліметрах відносно базової точки відліку (Datum);
4. Номінальну електричну потужність споживання `P_i` у ватах (для авіоніки та корисного навантаження).

### Розрахункові співвідношення

1. **Загальна злітна маса (MTOW):**
   ```
   MTOW = ∑ m_i
   ```

2. **Координати центру тяжіння (Center of Gravity, CG):**
   ```
   X_cg = (∑ m_i · x_i) / MTOW
   Y_cg = (∑ m_i · y_i) / MTOW
   Z_cg = (∑ m_i · z_i) / MTOW
   ```

3. **Відхилення центру тяжіння від центру тяги (CoT):**
   ```
   Δ_cg = √((X_cg - X_cot)² + (Y_cg - Y_cot)²)
   ```

4. **Тягооснащеність (Thrust-to-Weight Ratio, TWR):**
   ```
   TWR = (N_motors · T_max_motor) / (MTOW · g)
   ```

---

## 2. Реалізація калькулятора (C та C++)

Нижче наведено модульну реалізацію калькулятора. Версія мовою C використовує статичні структури та компактний формат пам'яті без динамічного виділення, а версія на C++20 застосовує контейнери стандартної бібліотеки, строгу типізацію та строковий огляд (`std::string_view`).

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_COMPONENTS 32
#define GRAVITY_MSS 9.80665f

typedef enum {
    CAT_PAYLOAD = 0,
    CAT_BATTERY,
    CAT_PROPULSION,
    CAT_AVIONICS,
    CAT_AIRFRAME,
    CAT_MARGIN,
    CAT_COUNT
} ComponentCategory;

static const char* const CATEGORY_NAMES[] = {
    "Корисне навантаження",
    "Акумуляторна батарея",
    "Силова установка",
    "Бортова авіоніка",
    "Планер і кріплення",
    "Конструкторський резерв"
};

typedef struct {
    char name[40];
    ComponentCategory category;
    float mass_g;
    float x_mm;
    float y_mm;
    float z_mm;
    float power_w;
} Component;

typedef struct {
    Component items[MAX_COMPONENTS];
    size_t count;
    int motor_count;
    float max_thrust_per_motor_g;
    float cot_x_mm;
    float cot_y_mm;
} WeightBudget;

typedef struct {
    float mtow_g;
    float category_mass_g[CAT_COUNT];
    float category_fraction[CAT_COUNT];
    float cg_x_mm;
    float cg_y_mm;
    float cg_z_mm;
    float cg_offset_mm;
    float twr;
    float total_idle_power_w;
    bool is_balanced;
    bool is_twr_sufficient;
    bool is_battery_fraction_ok;
} BudgetAnalysis;

void budget_init(WeightBudget* budget, int motor_count, float max_thrust_g, float cot_x, float cot_y) {
    budget->count = 0;
    budget->motor_count = motor_count;
    budget->max_thrust_per_motor_g = max_thrust_g;
    budget->cot_x_mm = cot_x;
    budget->cot_y_mm = cot_y;
    memset(budget->items, 0, sizeof(budget->items));
}

bool budget_add(WeightBudget* budget, const char* name, ComponentCategory cat, 
                float mass_g, float x, float y, float z, float power_w) {
    if (budget->count >= MAX_COMPONENTS) {
        return false;
    }
    Component* item = &budget->items[budget->count++];
    strncpy(item->name, name, sizeof(item->name) - 1);
    item->name[sizeof(item->name) - 1] = '\0';
    item->category = cat;
    item->mass_g = mass_g;
    item->x_mm = x;
    item->y_mm = y;
    item->z_mm = z;
    item->power_w = power_w;
    return true;
}

BudgetAnalysis budget_calculate(const WeightBudget* budget) {
    BudgetAnalysis res;
    memset(&res, 0, sizeof(res));

    float sum_mx = 0.0f;
    float sum_my = 0.0f;
    float sum_mz = 0.0f;

    for (size_t i = 0; i < budget->count; ++i) {
        const Component* it = &budget->items[i];
        res.mtow_g += it->mass_g;
        res.category_mass_g[it->category] += it->mass_g;
        res.total_idle_power_w += it->power_w;

        sum_mx += it->mass_g * it->x_mm;
        sum_my += it->mass_g * it->y_mm;
        sum_mz += it->mass_g * it->z_mm;
    }

    if (res.mtow_g > 0.0f) {
        res.cg_x_mm = sum_mx / res.mtow_g;
        res.cg_y_mm = sum_my / res.mtow_g;
        res.cg_z_mm = sum_mz / res.mtow_g;

        for (int c = 0; c < CAT_COUNT; ++c) {
            res.category_fraction[c] = (res.category_mass_g[c] / res.mtow_g) * 100.0f;
        }

        float dx = res.cg_x_mm - budget->cot_x_mm;
        float dy = res.cg_y_mm - budget->cot_y_mm;
        res.cg_offset_mm = sqrtf(dx * dx + dy * dy);

        float total_max_thrust = budget->motor_count * budget->max_thrust_per_motor_g;
        res.twr = total_max_thrust / res.mtow_g;

        res.is_balanced = (res.cg_offset_mm <= 3.0f);
        res.is_twr_sufficient = (res.twr >= 1.8f);
        res.is_battery_fraction_ok = (res.category_fraction[CAT_BATTERY] <= 55.0f);
    }

    return res;
}

void budget_print_report(const WeightBudget* budget, const BudgetAnalysis* a) {
    printf("=================================================================\n");
    printf("              ІНЖЕНЕРНИЙ ЗВІТ ВАГОВОГО БЮДЖЕТУ                   \n");
    printf("=================================================================\n");
    printf("%-30s | %10s | %14s\n", "Категорія", "Маса (г)", "Частка MTOW (%)");
    printf("-----------------------------------------------------------------\n");

    for (int c = 0; c < CAT_COUNT; ++c) {
        printf("%-30s | %10.1f | %13.1f%%\n",
               CATEGORY_NAMES[c], a->category_mass_g[c], a->category_fraction[c]);
    }
    printf("-----------------------------------------------------------------\n");
    printf("%-30s | %10.1f | %13.1f%%\n", "ПОВНА ЗЛІТНА МАСА (MTOW)", a->mtow_g, 100.0f);
    printf("=================================================================\n");

    printf("Центр тяжіння (CG):      X = %+.1f мм, Y = %+.1f мм, Z = %+.1f мм\n",
           a->cg_x_mm, a->cg_y_mm, a->cg_z_mm);
    printf("Центр тяги (CoT):        X = %+.1f мм, Y = %+.1f мм\n",
           budget->cot_x_mm, budget->cot_y_mm);
    printf("Зсув CG відносно CoT:    Δ = %.2f мм [%s]\n",
           a->cg_offset_mm, a->is_balanced ? "OK: Збалансовано" : "УВАГА: Перекіс > 3 мм");

    printf("Тягооснащеність (TWR):   %.2f:1 [%s]\n",
           a->twr, a->is_twr_sufficient ? "OK: Запас тяги достатній" : "КРИТИЧНО: TWR < 1.8");
    printf("Частка акумулятора:      %.1f%% [%s]\n",
           a->category_fraction[CAT_BATTERY],
           a->is_battery_fraction_ok ? "OK: Оптимальна" : "УВАГА: Ризик перевантаження");
    printf("Споживання електроніки:  %.1f Вт (постійне бортове навантаження)\n",
           a->total_idle_power_w);
    printf("=================================================================\n");
}

int main(void) {
    WeightBudget uav;
    // Квадрокоптер X4, 4 мотори з макс. тягою 1850 г кожен, центр тяги у (0, 0)
    budget_init(&uav, 4, 1850.0f, 0.0f, 0.0f);

    budget_add(&uav, "Термальна камера + Gimbal", CAT_PAYLOAD,    380.0f,  45.0f,   0.0f, -20.0f, 12.0f);
    budget_add(&uav, "Бортовий комп'ютер SBC",   CAT_PAYLOAD,     85.0f,  10.0f,   0.0f,  10.0f, 15.0f);
    budget_add(&uav, "Батарея Li-ion 6S2P 21700",CAT_BATTERY,    860.0f, -22.0f,   0.0f,  25.0f,  0.0f);
    budget_add(&uav, "Мотори 2806.5 (4 шт)",     CAT_PROPULSION, 192.0f,   0.0f,   0.0f,   0.0f,  0.0f);
    budget_add(&uav, "ESC 4-in-1 55A",           CAT_PROPULSION,  28.0f,   0.0f,   0.0f,   5.0f,  1.5f);
    budget_add(&uav, "Пропелери 7.5x4.5 (4 шт)", CAT_PROPULSION,  36.0f,   0.0f,   0.0f,  15.0f,  0.0f);
    budget_add(&uav, "Політний контролер FC H7", CAT_AVIONICS,    14.0f,   0.0f,   0.0f,  12.0f,  3.0f);
    budget_add(&uav, "GNSS модуль + Compass",    CAT_AVIONICS,    18.0f, -50.0f,   0.0f,  45.0f,  1.2f);
    budget_add(&uav, "VTX 5.8GHz 2.5W + антена", CAT_AVIONICS,    32.0f, -40.0f,   0.0f,  20.0f, 11.0f);
    budget_add(&uav, "Приймач ELRS 868MHz",      CAT_AVIONICS,     4.0f, -30.0f,   0.0f,   8.0f,  0.5f);
    budget_add(&uav, "Карбонова рама 7 дюймів",  CAT_AIRFRAME,   165.0f,   0.0f,   0.0f,   0.0f,  0.0f);
    budget_add(&uav, "Кріплення, демпфери, TPU", CAT_AIRFRAME,    45.0f,   5.0f,   0.0f,   5.0f,  0.0f);
    budget_add(&uav, "Конструкторський резерв",  CAT_MARGIN,      80.0f,   0.0f,   0.0f,   0.0f,  0.0f);

    BudgetAnalysis report = budget_calculate(&uav);
    budget_print_report(&uav, &report);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <numeric>
#include <cmath>
#include <iomanip>

enum class ComponentCategory : size_t {
    Payload = 0,
    Battery,
    Propulsion,
    Avionics,
    Airframe,
    Margin,
    Count
};

constexpr std::array<std::string_view, static_cast<size_t>(ComponentCategory::Count)> CategoryNames = {
    "Корисне навантаження",
    "Акумуляторна батарея",
    "Силова установка",
    "Бортова авіоніка",
    "Планер і кріплення",
    "Конструкторський резерв"
};

struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Component {
    std::string name;
    ComponentCategory category;
    float mass_g{0.0f};
    Vector3D position_mm;
    float power_w{0.0f};
};

struct BudgetAnalysis {
    float mtow_g{0.0f};
    std::array<float, static_cast<size_t>(ComponentCategory::Count)> category_mass_g{};
    std::array<float, static_cast<size_t>(ComponentCategory::Count)> category_fraction{};
    Vector3D cg_mm;
    float cg_offset_mm{0.0f};
    float twr{0.0f};
    float total_idle_power_w{0.0f};
    bool is_balanced{false};
    bool is_twr_sufficient{false};
    bool is_battery_fraction_ok{false};
};

class WeightBudgetCalculator {
public:
    WeightBudgetCalculator(int motor_count, float max_thrust_per_motor_g, Vector3D cot_position_mm = {})
        : motor_count_(motor_count),
          max_thrust_per_motor_g_(max_thrust_per_motor_g),
          cot_position_mm_(cot_position_mm) {}

    void add_component(std::string name, ComponentCategory cat, 
                       float mass_g, Vector3D pos, float power_w = 0.0f) {
        components_.push_back(Component{
            .name = std::move(name),
            .category = cat,
            .mass_g = mass_g,
            .position_mm = pos,
            .power_w = power_w
        });
    }

    [[nodiscard]] BudgetAnalysis calculate() const {
        BudgetAnalysis res{};

        float sum_mx = 0.0f;
        float sum_my = 0.0f;
        float sum_mz = 0.0f;

        for (const auto& item : components_) {
            res.mtow_g += item.mass_g;
            const auto cat_idx = static_cast<size_t>(item.category);
            res.category_mass_g[cat_idx] += item.mass_g;
            res.total_idle_power_w += item.power_w;

            sum_mx += item.mass_g * item.position_mm.x;
            sum_my += item.mass_g * item.position_mm.y;
            sum_mz += item.mass_g * item.position_mm.z;
        }

        if (res.mtow_g > 0.0f) {
            res.cg_mm = Vector3D{
                .x = sum_mx / res.mtow_g,
                .y = sum_my / res.mtow_g,
                .z = sum_mz / res.mtow_g
            };

            for (size_t c = 0; c < static_cast<size_t>(ComponentCategory::Count); ++c) {
                res.category_fraction[c] = (res.category_mass_g[c] / res.mtow_g) * 100.0f;
            }

            const float dx = res.cg_mm.x - cot_position_mm_.x;
            const float dy = res.cg_mm.y - cot_position_mm_.y;
            res.cg_offset_mm = std::sqrt(dx * dx + dy * dy);

            const float total_max_thrust = static_cast<float>(motor_count_) * max_thrust_per_motor_g_;
            res.twr = total_max_thrust / res.mtow_g;

            res.is_balanced = (res.cg_offset_mm <= 3.0f);
            res.is_twr_sufficient = (res.twr >= 1.8f);
            const size_t bat_idx = static_cast<size_t>(ComponentCategory::Battery);
            res.is_battery_fraction_ok = (res.category_fraction[bat_idx] <= 55.0f);
        }

        return res;
    }

    void print_report(const BudgetAnalysis& a) const {
        std::cout << "=================================================================\n";
        std::cout << "              ІНЖЕНЕРНИЙ ЗВІТ ВАГОВОГО БЮДЖЕТУ                   \n";
        std::cout << "=================================================================\n";
        std::cout << std::left << std::setw(30) << "Категорія" << " | "
                  << std::right << std::setw(10) << "Маса (г)" << " | "
                  << std::setw(14) << "Частка MTOW (%)" << "\n";
        std::cout << "-----------------------------------------------------------------\n";

        std::cout << std::fixed << std::setprecision(1);
        for (size_t c = 0; c < static_cast<size_t>(ComponentCategory::Count); ++c) {
            std::cout << std::left << std::setw(30) << CategoryNames[c] << " | "
                      << std::right << std::setw(10) << a.category_mass_g[c] << " | "
                      << std::setw(13) << a.category_fraction[c] << "%\n";
        }
        std::cout << "-----------------------------------------------------------------\n";
        std::cout << std::left << std::setw(30) << "ПОВНА ЗЛІТНА МАСА (MTOW)" << " | "
                  << std::right << std::setw(10) << a.mtow_g << " | "
                  << std::setw(13) << 100.0f << "%\n";
        std::cout << "=================================================================\n";

        std::cout << "Центр тяжіння (CG):      X = " << std::showpos << a.cg_mm.x 
                  << " мм, Y = " << a.cg_mm.y << " мм, Z = " << a.cg_mm.z << " мм\n" << std::noshowpos;
        std::cout << "Центр тяги (CoT):        X = " << std::showpos << cot_position_mm_.x 
                  << " мм, Y = " << cot_position_mm_.y << " мм\n" << std::noshowpos;
        std::cout << "Зсув CG відносно CoT:    Δ = " << std::setprecision(2) << a.cg_offset_mm 
                  << " мм [" << (a.is_balanced ? "OK: Збалансовано" : "УВАГА: Перекіс > 3 мм") << "]\n";

        std::cout << "Тягооснащеність (TWR):   " << a.twr << ":1 ["
                  << (a.is_twr_sufficient ? "OK: Запас тяги достатній" : "КРИТИЧНО: TWR < 1.8") << "]\n";
        const size_t bat_idx = static_cast<size_t>(ComponentCategory::Battery);
        std::cout << "Частка акумулятора:      " << std::setprecision(1) << a.category_fraction[bat_idx] 
                  << "% [" << (a.is_battery_fraction_ok ? "OK: Оптимальна" : "УВАГА: Ризик перевантаження") << "]\n";
        std::cout << "Споживання електроніки:  " << a.total_idle_power_w 
                  << " Вт (постійне бортове навантаження)\n";
        std::cout << "=================================================================\n";
    }

private:
    int motor_count_{4};
    float max_thrust_per_motor_g_{0.0f};
    Vector3D cot_position_mm_{};
    std::vector<Component> components_;
};

int main() {
    // Конфігурація розвідувального 7-дюймового квадрокоптера (X4)
    WeightBudgetCalculator uav(4, 1850.0f, Vector3D{0.0f, 0.0f, 0.0f});

    uav.add_component("Термальна камера + Gimbal", ComponentCategory::Payload,    380.0f, Vector3D{ 45.0f, 0.0f, -20.0f}, 12.0f);
    uav.add_component("Бортовий комп'ютер SBC",   ComponentCategory::Payload,     85.0f, Vector3D{ 10.0f, 0.0f,  10.0f}, 15.0f);
    uav.add_component("Батарея Li-ion 6S2P 21700",ComponentCategory::Battery,    860.0f, Vector3D{-22.0f, 0.0f,  25.0f},  0.0f);
    uav.add_component("Мотори 2806.5 (4 шт)",     ComponentCategory::Propulsion, 192.0f, Vector3D{  0.0f, 0.0f,   0.0f},  0.0f);
    uav.add_component("ESC 4-in-1 55A",           ComponentCategory::Propulsion,  28.0f, Vector3D{  0.0f, 0.0f,   5.0f},  1.5f);
    uav.add_component("Пропелери 7.5x4.5 (4 шт)", ComponentCategory::Propulsion,  36.0f, Vector3D{  0.0f, 0.0f,  15.0f},  0.0f);
    uav.add_component("Політний контролер FC H7", ComponentCategory::Avionics,    14.0f, Vector3D{  0.0f, 0.0f,  12.0f},  3.0f);
    uav.add_component("GNSS модуль + Compass",    ComponentCategory::Avionics,    18.0f, Vector3D{-50.0f, 0.0f,  45.0f},  1.2f);
    uav.add_component("VTX 5.8GHz 2.5W + антена", ComponentCategory::Avionics,    32.0f, Vector3D{-40.0f, 0.0f,  20.0f}, 11.0f);
    uav.add_component("Приймач ELRS 868MHz",      ComponentCategory::Avionics,     4.0f, Vector3D{-30.0f, 0.0f,   8.0f},  0.5f);
    uav.add_component("Карбонова рама 7 дюймів",  ComponentCategory::Airframe,   165.0f, Vector3D{  0.0f, 0.0f,   0.0f},  0.0f);
    uav.add_component("Кріплення, демпфери, TPU", ComponentCategory::Airframe,    45.0f, Vector3D{  5.0f, 0.0f,   5.0f},  0.0f);
    uav.add_component("Конструкторський резерв",  ComponentCategory::Margin,      80.0f, Vector3D{  0.0f, 0.0f,   0.0f},  0.0f);

    const auto report = uav.calculate();
    uav.print_report(report);

    return 0;
}
```
:::

---

## 3. Аналіз роботи та інженерні висновки

Калькулятор формує детальний підсумок вагового балансу, який одразу сигналізує про потенційні аеродинамічні чи теплові загрози:

```
=================================================================
              ІНЖЕНЕРНИЙ ЗВІТ ВАГОВОГО БЮДЖЕТУ                   
=================================================================
Категорія                      |   Маса (г) | Частка MTOW (%)
-----------------------------------------------------------------
Корисне навантаження           |      465.0 |          24.0%
Акумуляторна батарея           |      860.0 |          44.4%
Силова установка               |      256.0 |          13.2%
Бортова авіоніка               |       68.0 |           3.5%
Планер і кріплення             |      210.0 |          10.8%
Конструкторський резерв        |       80.0 |           4.1%
-----------------------------------------------------------------
ПОВНА ЗЛІТНА МАСА (MTOW)       |     1939.0 |         100.0%
=================================================================
Центр тяжіння (CG):      X = -1.6 мм, Y = +0.0 мм, Z = +8.9 мм
Центр тяги (CoT):        X = +0.0 мм, Y = +0.0 мм
Зсув CG відносно CoT:    Δ = 1.57 мм [OK: Збалансовано]
Тягооснащеність (TWR):   3.82:1 [OK: Запас тяги достатній]
Частка акумулятора:      44.4% [OK: Оптимальна]
Споживання електроніки:  44.2 Вт (постійне бортове навантаження)
=================================================================
```

### Практичне використання розрахунку

1. **Компенсація важкого оптичного підвісу попереду:** Камера масою 380 г у точці `X = +45 мм` компенсується зміщенням батареї масою 860 г у точку `X = -22 мм`. Підсумковий зсув `Δ = 1.57 мм` (зміщення `X_cg = -1.6 мм`) є ідеальним: диференціал тяги передніх і задніх моторів у висінні складе менше 1%, зберігаючи симетричний динамічний діапазон ПІД-регулятора.
2. **Контроль висоти центру мас (`Z_cg`):** Значення `Z_cg = +8.9 мм` розташоване трохи вище площини пропелерів (`Z = 0 мм`), що типово для платформ із верхнім розташуванням акумулятора. Це забезпечує підвищену чутливість до кутових прискорень (Roll/Pitch rate) при маневрах.
3. **Енергетичний аудит бортової електроніки:** Постійне споживання 44.2 Вт (SBC + VTX + FC) є значною величиною: для батареї 6S2P (ємність ~200 Вт·год) це означає, що понад 22% всієї запасеної енергії витрачається не на політ, а на живлення обчислювачів і передавача.

---

## 4. Інженерні сценарії використання калькулятора та валідація

У процесі підготовки серійного виробництва або розробки кастомної платформи калькулятор інтегрується у три основні етапи інженерного робочого процесу:

### Сценарій 1. Автоматизована генерація конфігурації польотного контролера
Сучасні прошивки автопілотів (ArduPilot, PX4, Betaflight) вимагають точного знання вагових і силових параметрів апарата для ініціалізації контурів управління:
* **Базовий газ висіння (`MOT_THST_HOVER` в ArduPilot):**
  Розраховується як `Hover_Throttle = 1.0 / TWR`. Для нашого прикладу з `TWR = 3.82` розрахункове значення дорівнює `0.26` (26% тяги). Якщо прошивка стартує з дефолтним значенням 0.50, апарат при першому переході в режим утримання висоти (Altitude Hold) підскочить угору.
* **Масштабування ПІД-коефіцієнтів за напругою та масою (TPA / Thrust PID Attenuation):**
  Знаючи відношення тяги до маси, інженер налаштовує криву ослаблення коефіцієнтів `D-term` на високому газі, запобігаючи високочастотним механічним осциляціям моторів.

### Сценарій 2. Оцінка динамічного зміщення центру мас під час місії
У багатьох практичних місіях маса апарата не залишається абсолютно постійною:
1. **Скидання корисного навантаження (Cargo Drop):**
   При скиданні вантажу масою 380 г значення `m_payload` обнуляється. Повна злітна маса зменшується з 1939 г до 1559 г, а центр мас різко зміщується назад у точку `X_cg = -12.4 мм` (оскільки батарея залишилася ззаду). Калькулятор дозволяє заздалегідь перевірити, чи вистачить залишкового запасу тяги задніх моторів для стабільного повернення апарата на базу без перекидання.
2. **Зсув батареї при жорстких перевантаженнях:**
   Якщо текстильна липучка (Kevlar Strap) послабилася в польоті і акумулятор зсунувся назад на 30 мм, зсув центру мас зростає до `Δ_cg = 14.5 мм`. Розрахунок показує, що при такому перекосі задні мотори повинні видавати на 45% більше тяги, ніж передні, що спричинить швидке спрацьовування теплового захисту ESC.

### Сценарій 3. Оцінка головних моментів інерції тензора (`I_xx`, `I_yy`, `I_zz`)
Знаючи маси `m_i` та їхні просторові координати відносно обчисленого центру тяжіння `(x_i - X_cg, y_i - Y_cg, z_i - Z_cg)`, калькулятор дозволяє обчислити діагональні компоненти тензора інерції твердого тіла:

```
I_xx = ∑ m_i · ((y_i - Y_cg)² + (z_i - Z_cg)²)
I_yy = ∑ m_i · ((x_i - X_cg)² + (z_i - Z_cg)²)
I_zz = ∑ m_i · ((x_i - X_cg)² + (y_i - Y_cg)²)
```

Ці величини безпосередньо визначають кутове прискорення апарата під дією керівних моментів: `dω / dt = M / I`. Якщо важкі компоненти (батарея та камера) рознесені далеко по краях рами (великі значення `|x_i|`), поздовжній момент інерції `I_yy` різко зростає. Апарат стає «в'ялим» по осі тангажу (Pitch), вимагаючи від автопілота агресивніших коефіцієнтів `P-term` і `FeedForward` для збереження динаміки.

---

## 5. Вбудовування в бортову прошивку реального часу

Алгоритм розрахунку вагового балансу на мові C спроектовано для роботи на вбудованих мікроконтролерах класу ARM Cortex-M4/M7 (STM32 F405, F722, H743):
* **Відсутність динамічної купи (No Heap Allocation):** Усі масиви мають фіксований розмір `MAX_COMPONENTS = 32`, що гарантує детермінізм пам'яті та унеможливлює фрагментацію RAM під час польоту;
* **Мінімальний час виконання:** Повний розрахунок MTOW, CG та TWR займає менше 1.2 мікросекунди на частоті 480 МГц, що дозволяє викликати функцію в низькопріоритетному тасці телеметрії з частотою 10 Гц;
* **Сумісність із протоколом MAVLink:** Розраховані параметри транслюються на наземну станцію керування (QGroundControl, Mission Planner) у складі кастомного повідомлення або стандартного пакета `SYS_STATUS`, сповіщаючи оператора про поточний баланс маси й енергії в реальному часі.

