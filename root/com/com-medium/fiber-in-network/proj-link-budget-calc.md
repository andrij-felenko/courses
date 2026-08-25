# ⚙️ Проект: Калькулятор оптичного бюджету та аналізатор запасу лінії PON

Цей практичний проект присвячено розробці універсального модульного ядра для автоматизованого розрахунку оптичного бюджету потужності лінії (*Optical Link Power Budget*), оцінки неефективностей пасивного розщеплення в мережах PON (GPON, XGS-PON, NG-PON2) та визначення системного запасу лінії (*System Link Margin*) мовами C та C++.

---

### Архітектурний опис та постановка задачі

Під час проектування волоконно-оптичних ліній зв'язку (ВОЛЗ) та автоматизованої паспортизації магістралей інженери щоденно вирішують задачу підтвердження фізичної спроможності оптичного тракту. Ручний розрахунок у таблицях Excel часто призводить до помилок через ігнорування втрат вставки на зварках, неефективностей PLC-сплітерів або температурних відхилень лазерів.

Сворюваний модуль вирішує три ключові задачі:
1. **Точний облік зважених втрат тракту:** Розрахунок погонного загасання волокна з урахуванням довжини й довжини хвилі (1310, 1490, 1550 чи 1577 нм), втрат на технологічних зварювальних стиках, кросових роз'ємах та логарифмічних втрат розгалуження на пасивних сплітерах 1:N.
2. **Перевірка динамічного діапазону:** Автоматичне зіставлення розрахованого рівня оптичної потужності на приймачі `P_RX` із межами чутливості `P_sens` та оптичного перевантаження `P_overload` конкретного класу приймача (наприклад, GPON Class B+, Class C+ чи XGS-PON N1/N2).
3. **Класифікація надійності лінії:** Визначення залишку оптичного запасу `Margin` [дБ] із видачею розширеного статусу:
   - `LINK_STATUS_OK`: Лінія повністю працездатна, інженерний запас перевищує норму (≥ 3.0 дБ).
   - `LINK_STATUS_LOW_MARGIN`: Сигнал доходить до фотодіода, але запас лінії впав нижче нормативного (0.0…3.0 дБ). Існує високий ризик втрати зв'язку при підвищенні температури чи старінні лазера.
   - `LINK_STATUS_UNREACHABLE`: Загасання траси перевищило поріг чутливості приймача (`P_RX < P_sens`). Зв'язок відсутній.
   - `LINK_STATUS_OVERLOADED`: Оптична потужність на приймачі вища за поріг оптичного насичення фотодіода (`P_RX > P_overload`). Існує ризик засліплення діода та сплеску бітових помилок.

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      СТРУКТУРА ОПТИЧНОГО ТРАКТУ                        │
 │                                                                        │
 │   [Передавач P_TX] ──► (Роз'єм A_conn) ──► (Зварки N_spl)             │
 │                               │                                        │
 │                               ▼                                        │
 │                  (Кабель L км * α дБ/км)                               │
 │                               │                                        │
 │                               ▼                                        │
 │                  (Сплітер 1:N -> A_split)                              │
 │                               │                                        │
 │                               ▼                                        │
 │   [Приймач P_RX]  ◄── (Роз'єм A_conn) ──► [Оптичний бюджет P_sens]      │
 └────────────────────────────────────────────────────────────────────────┘
```

---

### Деталізований математичний та алгоритмічний аналіз

Для забезпечення найвищої швидкості обчислень в автотестах GIS-систем (обробка десятків тисяч абонентських трас на секунду) та сумісності з мікроконтролерами оптичних рефлектометрів (OTDR), розрахунковий алгоритм будується на прямих логарифмічних перетвореннях без виділення динамічної пам'яті.

1. **Розрахунок втрат сплітера:**
   Втрати розгалужувача `A_splitter` обчислюються за фундаментальною логарифмічною формулою:
   ```text
   A_splitter = 10 · log₁₀( Ratio ) + A_excess
   ```
   Де `Ratio` — коефіцієнт розщеплення (1, 2, 4, 8, 16, 32, 64 або 128), а `A_excess` — фабричні втрати вставки PLC-матриці (зазвичай від 0.5 дБ для 1:2 до 2.5 дБ для 1:64).

2. **Обчислення сумарного загасання траси:**
   Загальне загасання складається з чотирьох незалежних доданків:
   ```text
   A_total = (L · α) + (N_spl · A_spl) + (N_conn · A_conn) + A_splitter
   ```
   Кожен доданок розраховується з урахуванням специфіки технологічного монтажу. Наприклад, для волокна на довжині хвилі 1490 нм коефіцієнт `α = 0.35 дБ/км`, а на довжині хвилі 1577 нм (XGS-PON) — `α = 0.22 дБ/км`.

3. **Оцінка оптичної потужності на приймачі:**
   ```text
   P_RX = P_TX − A_total
   ```
   У разі отримання негативного або нереалістичного значення потужності програма перевіряє коректність вхідних параметрів передавача `P_TX`.

4. **Обчислення запасу та класифікація:**
   ```text
   Margin = P_RX − P_sens
   ```
   Якщо отриманий результат `Margin` менший за нуль, це свідчить про те, що лінія непрацездатна за поточного рівня зварних втрат або коефіцієнта розщеплення.

---

### Інтеграція з мережевими утилітами та системи паспортизації

Модуль розрахунку оптичного бюджету розроблений для легкої інтеграції в автоматизовані системи управління мережею (NMS — *Network Management System*), геоінформаційні карти (GIS) та автономні вимірювальні прилади (OTDR/OPM).

Під час підключення нового абонента менеджер мережі або технік на виклику вводить у гео-систему довжину кабельної лінії та адресу сплітерної шафи. Програма автоматично викликає ядро розрахунку бюджету і дає відповідь: чи можливе підключення на даній нитці, чи потрібне переварювання кросових роз'ємів, чи необхідно перевести порт OLT у вищий оптичний клас (наприклад, з GPON Class B+ на Class C+).

---

### Повна реалізація: C та C++

Поданий код реалізовано у двох ідіоматичних стилях: C (чисті структури, статичні функції, відсутність залежностей) та C++ (класи, шаблони рішень `std::expected`, типування `std::string_view`, нові можливості форматування C++20/C++23).

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Статуси оптичної лінії
typedef enum {
    LINK_STATUS_OK = 0,          // Запас лінії в межах норми (>= 3.0 дБ)
    LINK_STATUS_LOW_MARGIN,      // Сигнал доходить, але запас критичний (0 .. 3.0 дБ)
    LINK_STATUS_UNREACHABLE,     // Сигнал загашений нижче чутливості приймача
    LINK_STATUS_OVERLOADED       // Перевантаження приймача (ризик пошкодження діода)
} link_status_t;

// Параметри оптичного трансивера
typedef struct {
    float tx_power_dbm;          // Вихідна потужність передавача (дБм)
    float rx_sensitivity_dbm;    // Поріг чутливості приймача (дБм)
    float rx_overload_dbm;       // Рівень оптичного насичення (дБм)
} transceiver_spec_t;

// Параметри пасивної траси
typedef struct {
    float length_km;             // Довжина оптичного кабелю (км)
    float attenuation_per_km;    // Загасання волокна на робочій хвилі (дБ/км)
    int splice_count;            // Кількість зварних з'єднань
    float splice_loss_db;        // Втрати на одну зварку (дБ)
    int connector_count;         // Кількість з'єднувальних роз'ємів
    float connector_loss_db;     // Втрати на один роз'єм (дБ)
    int splitter_ratio;          // Коефіцієнт розщеплення сплітера (1, 2, 4, 8, 16, 32, 64)
    float splitter_excess_db;    // Додаткові втрати вставки сплітера (дБ)
    float system_margin_target;  // Нормативний інженерний запас (дБ, зазвичай 3.0)
} fiber_path_t;

// Результат розрахунку оптичного бюджету
typedef struct {
    float total_attenuation_db;  // Сумарне загасання тракту (дБ)
    float rx_power_dbm;          // Розрахункова потужність на приймачі (дБм)
    float margin_db;             // Фактичний залишковий запас (дБ)
    link_status_t status;        // Підсумковий статус лінії
} link_budget_result_t;

// Розрахунок втрат пасивного оптичного розгалужувача 1:N
static float calculate_splitter_loss(int ratio, float excess_loss_db) {
    if (ratio <= 1) return 0.0f;
    // Формула: 10 * log10(ratio) + excess_loss
    return 10.0f * log10f((float)ratio) + excess_loss_db;
}

// Головна функція розрахунку оптичного бюджету
link_budget_result_t calculate_link_budget(const transceiver_spec_t *tx_rx,
                                           const fiber_path_t *path) {
    link_budget_result_t result = {0};

    // 1. Загасання оптичного волокна
    float fiber_loss = path->length_km * path->attenuation_per_km;

    // 2. Втрати на зварювальних та рознімних з'єднаннях
    float splices_loss = (float)path->splice_count * path->splice_loss_db;
    float connectors_loss = (float)path->connector_count * path->connector_loss_db;

    // 3. Втрати на пасивному сплітері
    float splitter_loss = calculate_splitter_loss(path->splitter_ratio, path->splitter_excess_db);

    // 4. Сумарне загасання тракту
    result.total_attenuation_db = fiber_loss + splices_loss + connectors_loss + splitter_loss;

    // 5. Розрахункова потужність на фотодіоді приймача
    result.rx_power_dbm = tx_rx->tx_power_dbm - result.total_attenuation_db;

    // 6. Розрахунок запасу відносно чутливості
    result.margin_db = result.rx_power_dbm - tx_rx->rx_sensitivity_dbm;

    // 7. Оцінка стану лінії
    if (result.rx_power_dbm > tx_rx->rx_overload_dbm) {
        result.status = LINK_STATUS_OVERLOADED;
    } else if (result.rx_power_dbm < tx_rx->rx_sensitivity_dbm) {
        result.status = LINK_STATUS_UNREACHABLE;
    } else if (result.margin_db < path->system_margin_target) {
        result.status = LINK_STATUS_LOW_MARGIN;
    } else {
        result.status = LINK_STATUS_OK;
    }

    return result;
}

int main(void) {
    // Специфікація модуля GPON Class B+
    transceiver_spec_t gpon_b_plus = {
        .tx_power_dbm = 2.5f,          // +2.5 дБм (передавач OLT)
        .rx_sensitivity_dbm = -27.0f,  // -27.0 дБм (чутливість ONU)
        .rx_overload_dbm = -8.0f       // -8.0 дБм (перевантаження ONU)
    };

    // Параметри випробувальної траси GPON 12 км зі сплітером 1:32
    fiber_path_t path_12km = {
        .length_km = 12.0f,
        .attenuation_per_km = 0.35f,   // 1490 нм
        .splice_count = 5,
        .splice_loss_db = 0.04f,
        .connector_count = 4,
        .connector_loss_db = 0.25f,
        .splitter_ratio = 32,          // 1:32
        .splitter_excess_db = 1.8f,
        .system_margin_target = 3.0f
    };

    link_budget_result_t res = calculate_link_budget(&gpon_b_plus, &path_12km);

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ОПТИЧНОГО БЮДЖЕТУ ===\n");
    printf("Сумарне загасання тракту:  %.2f дБ\n", res.total_attenuation_db);
    printf("Потужність на приймачі:    %.2f дБм\n", res.rx_power_dbm);
    printf("Залишковий запас лінії:    %.2f дБ (норма >= %.1f дБ)\n",
           res.margin_db, path_12km.system_margin_target);

    switch (res.status) {
        case LINK_STATUS_OK:
            printf("СТАТУС: [ОК] Лінія надійна, запас достатній.\n");
            break;
        case LINK_STATUS_LOW_MARGIN:
            printf("СТАТУС: [УВАГА] Сигнал є, але запас нижчий за 3 дБ!\n");
            break;
        case LINK_STATUS_UNREACHABLE:
            printf("СТАТУС: [ПОМИЛКА] Зв'язок відсутній (загасання завелике).\n");
            break;
        case LINK_STATUS_OVERLOADED:
            printf("СТАТУС: [КРИТИЧНО] Засліплення приймача (потрібен атенюатор).\n");
            break;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <string_view>
#include <expected>
#include <format>
#include <vector>

namespace photonics {

enum class LinkStatus {
    Ok,             // Лінія працює, запас достатній (>= Target Margin)
    LowMargin,      // Зв'язок є, але інженерний запас нижче норми
    Unreachable,    // Згасання перевищує поріг чутливості
    Overloaded      // Потужність вища за поріг насичення (overload)
};

struct TransceiverSpec {
    float tx_power_dbm{0.0f};
    float rx_sensitivity_dbm{-28.0f};
    float rx_overload_dbm{-8.0f};
};

struct FiberPath {
    float length_km{0.0f};
    float attenuation_per_km{0.35f};
    int splice_count{0};
    float splice_loss_db{0.05f};
    int connector_count{0};
    float connector_loss_db{0.3f};
    int splitter_ratio{1};
    float splitter_excess_db{1.5f};
    float system_margin_target{3.0f};
};

struct LinkBudgetResult {
    float total_attenuation_db{0.0f};
    float rx_power_dbm{0.0f};
    float margin_db{0.0f};
    LinkStatus status{LinkStatus::Ok};

    [[nodiscard]] constexpr std::string_view status_to_string() const noexcept {
        switch (status) {
            case LinkStatus::Ok:          return "OK: Лінія надійна";
            case LinkStatus::LowMargin:   return "WARNING: Запас нижче нормативу";
            case LinkStatus::Unreachable: return "ERROR: Сигнал загас повністю";
            case LinkStatus::Overloaded:  return "CRITICAL: Перевантаження приймача";
        }
        return "Unknown";
    }
};

class LinkBudgetCalculator {
public:
    [[nodiscard]] static float calculate_splitter_loss(int ratio, float excess_loss_db) noexcept {
        if (ratio <= 1) return 0.0f;
        return 10.0f * std::log10(static_cast<float>(ratio)) + excess_loss_db;
    }

    [[nodiscard]] static std::expected<LinkBudgetResult, std::string_view>
    analyze_link(const TransceiverSpec& tx_rx, const FiberPath& path) noexcept {
        if (path.length_km < 0.0f || path.attenuation_per_km < 0.0f) {
            return std::unexpected("Некоректна довжина або загасання волокна");
        }

        LinkBudgetResult result{};

        const float fiber_loss = path.length_km * path.attenuation_per_km;
        const float splices_loss = static_cast<float>(path.splice_count) * path.splice_loss_db;
        const float connectors_loss = static_cast<float>(path.connector_count) * path.connector_loss_db;
        const float splitter_loss = calculate_splitter_loss(path.splitter_ratio, path.splitter_excess_db);

        result.total_attenuation_db = fiber_loss + splices_loss + connectors_loss + splitter_loss;
        result.rx_power_dbm = tx_rx.tx_power_dbm - result.total_attenuation_db;
        result.margin_db = result.rx_power_dbm - tx_rx.rx_sensitivity_dbm;

        if (result.rx_power_dbm > tx_rx.rx_overload_dbm) {
            result.status = LinkStatus::Overloaded;
        } else if (result.rx_power_dbm < tx_rx.rx_sensitivity_dbm) {
            result.status = LinkStatus::Unreachable;
        } else if (result.margin_db < path.system_margin_target) {
            result.status = LinkStatus::LowMargin;
        } else {
            result.status = LinkStatus::Ok;
        }

        return result;
    }
};

} // namespace photonics

int main() {
    using namespace photonics;

    const TransceiverSpec xgs_pon_class_n1{
        .tx_power_dbm = 4.0f,          // +4.0 дБм (XGS-PON OLT 1577 нм)
        .rx_sensitivity_dbm = -28.0f,  // -28.0 дБм (XGS-PON ONU)
        .rx_overload_dbm = -7.0f
    };

    const FiberPath metro_path{
        .length_km = 18.5f,
        .attenuation_per_km = 0.22f,   // 1577 нм у C/L діапазоні
        .splice_count = 8,
        .splice_loss_db = 0.03f,
        .connector_count = 6,
        .connector_loss_db = 0.20f,
        .splitter_ratio = 64,          // 1:64 сплітер
        .splitter_excess_db = 2.1f,
        .system_margin_target = 3.0f
    };

    auto analysis = LinkBudgetCalculator::analyze_link(xgs_pon_class_n1, metro_path);

    if (analysis) {
        const auto& res = analysis.value();
        std::cout << std::format("=== РЕЗУЛЬТАТ XGS-PON (1:64, 18.5 км) ===\n");
        std::cout << std::format("Загасання тракту:  {:.2f} дБ\n", res.total_attenuation_db);
        std::cout << std::format("Потужність на ONU: {:.2f} дБм\n", res.rx_power_dbm);
        std::cout << std::format("Запас лінії:       {:.2f} дБ\n", res.margin_db);
        std::cout << std::format("Статус:            {}\n", res.status_to_string());
    } else {
        std::cerr << "Помилка аналізу: " << analysis.error() << '\n';
    }

    return 0;
}
```
:::

---

### Практичні висновки, крайові випадки та виправлення помилок

1. **Крайовий випадок засліплення (Overload):** На коротких випробувальних патчкордах (1–5 метрів) потужний лазер OLT (+5 дБм) потрапляє на роз'єм ONU без загасання. Якщо отриманий рівень перевищує `P_overload` (-8 дБм), фотодіод засліплюється й генерація бітових помилок зростає до 100%. Виправлення: додавання оптичного атенюатора (*optical attenuator*) на 10–15 дБ.
2. **Температурний дрейф лазера:** Із підвищенням температури вихідна потужність передавача падає на 0.5–1.5 дБ, а довжина хвилі зміщується на 0.1 нм/°C. Інженерний запас `M = 3.0 дБ` перекриває температурний деградаційний дефіцит.
3. **Нехтування неефективністю вставки сплітерів:** Початківці вважають, що розгалужувач 1:32 додає лише теоретичні `10 · log10(32) = 15.05 дБ`. На практиці планарна матриця PLC має втрати вставки `A_excess ≈ 2.0 дБ`, що дає сумарно **17.1 дБ**. Ігнорування цих 2 дБ призводить до провалу інженерного запасу лінії на реальному об'єкті.
4. **Плутанина між роз'ємами UPC та APC:** Застосування синього коннектора UPC замість зеленого APC на вхідному кросі PON підвищує зворотне відбиття ORL з `-60 дБ` до `-45 дБ`, що дестабілізує лазер OLT та викликає постійний перезапуск авторизації абонентів у мережі.
