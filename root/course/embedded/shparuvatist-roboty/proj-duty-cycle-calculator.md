# Інженерний калькулятор профілю живлення та шпаруватості

Реальний активний цикл бездротового сенсорного вузла складається не з одного усередненого струму, а з ланцюжка дискретних підфаз із різними струмами та тривалостями: розгін кварцового генератора, стабілізація живлення сенсора, вимірювання АЦП, цифрова обробка на максимальній частоті ядра, спалах випромінювання передавача та очікування квитанції підтвердження. Наведений нижче програмний модуль моделює багатофазний профіль споживання, розраховує інтегральний середній струм, час життя від різних типів елементів живлення та знаходить точку насичення шпаруватості.

## Архітектура багатофазного живлення сенсорного вузла

Оптимізація енергоспоживання на рівні плати базується на ізоляції вузлів через незалежні домени живлення. У стані глибокого сну живиться лише блок реального часу RTC та схема виявлення пробудження. Усі інші споживачі (зовнішній SPI/I²C датчик, Flash-пам'ять, радіотрансивер) повністю знеструмлюються за допомогою керованих транзисторних ключів (Power Gating) або спеціалізованих інтегральних комутаторів (Load Switches, наприклад TPS22918 або SLG55593) із контрольованою швидкістю наростання напруги (Slew Rate Control).

Контроль швидкості наростання напруги є критичним: під час раптового відкриття звичайного P-канального польового транзистора розряджені блокувальні конденсатори на шині датчика викликають імпульсний струм заряду (Inrush Current) амплітудою до 0.5–1.5 А. Це призводить до миттєвого просідання напруги на виводах батареї та аварійного перезавантаження мікроконтролера за сигналом Brown-Out Reset (BOR).

У процесі виконання активного вікна пристрій проходить послідовні фази:

```
[ Старт HSE/PLL ] → [ Запуск датчика ] → [ Обчислення / AES ] → [ Радіо TX ] → [ Очікування RX ] → [ Вхід у сон ]
   1.5 мс @ 8 мА        3.0 мс @ 5 мА          1.2 мс @ 18 мА        22 мс @ 45 мА       6.0 мс @ 11 мА        0.3 мс @ 3 мА
```

Розгляньмо інженерні вимоги до кожної підфази:

1. **Фаза 1: Розгін системи тактування.** Після пробудження з глибокого сну мікроконтролер стартує від швидкого внутрішнього RC-генератора (MSI/HSI) за 5–10 мкс. Якщо для обчислень чи радіо потрібен точний зовнішній кварц (HSE), процесор вмикає генератор і переходить у режим сну з очікуванням переривання готовності генератора (HSERDY), уникаючи холостого обертання циклу `while(!HSERDY)`.
2. **Фаза 2: Інтерфейсний обмін із давачем.** Зчитування регістрів по шині I²C на частоті 100 кГц займає до 2 мс активного часу процесора. Переведення шини на режим Fast Mode Plus (1 МГц) або використання SPI на частоті 8–10 МГц у парі з DMA скорочує фазу опитування до 150–300 мкс.
3. **Фаза 3: Обробка та шифрування.** Використання апаратного прискорювача AES-128 замість програмної бібліотеки скорочує час формування криптографічного блоку з 1.5 мс до 15 мкс, знижуючи споживання енергії на цій ділянці у 100 разів.
4. **Фаза 4: Радіопередача (TX Burst).** Тривалість випромінювання визначається схемою модуляції та розміром пакета. У LoRaWAN перехід із коефіцієнта розширення спектра SF12 (час у повітрі ~1.2 с) на SF7 (час у повітрі ~45 мс) зменшує витрату заряду на одну передачу у 26 разів.
5. **Фаза 5: Прийом квитанції (RX Window).** Очікування відповіді базової станції вимагає точної синхронізації часу. Неточний RTC викликає необхідність завчасного відкриття приймача (розширення вікна прийому), що марно спалює струм прийому (8–15 мА).
6. **Фаза 6: Безпечний перехід у сон.** Перед виконанням інструкції сну всі виводи GPIO, під'єднані до знеструмлених мікросхем, переводяться у високий опір (Hi-Z) або стан логічного нуля, щоб виключити паразитне живлення через внутрішні захисні ESD-діоди.

Загальний активний заряд `Q_on` обчислюється як сума зарядів усіх технологічних підфаз:

```
Q_on = ∑_{i=1}^{N} (I_phase[i] · t_phase[i])      [сумарний активний заряд за один спалах]
```

Середній інтегральний струм розраховується з урахуванням струму спокою `I_sleep` та загального періоду `T`:

```
I_avg = ( Q_on + I_sleep · (T - ∑ t_phase[i]) ) / T
```

## Методика зняття параметрів профілю на лабораторному стенді

Для заповнення конфігураційної структури калькулятора реальними значеннями застосовують цифрові профайлери струму (наприклад, Nordic Power Profiler Kit II або Joulescope JS220):

- **Синхронізація через маркерні піни GPIO:** перед початком кожної підфази прошивка виставляє високий рівень на виділеній ніжці налагодження (наприклад, `GPIO_PIN_0` для старту АЦП, `GPIO_PIN_1` для радіо). Логічний аналізатор або цифровий канал профайлера фіксує точні часові межі кожної ділянки.
- **Усереднення шуму вимірювання:** тривалість та струм кожної фази усереднюються за вибіркою з не менше ніж 50–100 послідовних циклів передачі, щоб врахувати випадкові затримки синхронізації та коливання напруги.
- **Виявлення зависань інтерфейсів:** якщо шина I²C зависає через шум або апаратний збій підтяжок, стандартні блокуючі драйвери можуть тримати ядро в активному циклі очікування. Захисні тайм-аути на апаратному таймері обов'язково обмежують максимальний час перебування в будь-якій фазі.

## Врахування характеристик хімічних джерел живлення

Різні типи батарей по-різному реагують на імпульсне навантаження та тривалу експлуатацію:

| Тип хімії | Номінальна напруга | Саморозряд (%/рік) | Внутрішній опір R_int | Рекомендований запас (derating) |
|---|---|---|---|---|
| **Li-SOCl2 (AA / C)** | 3.6 В | 1.0 % | 10–30 Ом | 0.85 (15% запас) |
| **Li-MnO2 (CR2032)** | 3.0 В | 1.5 % | 15–40 Ом | 0.70 (30% запас) |
| **LiFePO4 (18650)** | 3.2 В | 2.0 % | 0.05–0.2 Ом | 0.85 (15% запас) |
| **Alkaline (AA / AAA)**| 1.5 В | 3.0 % | 0.2–1.5 Ом | 0.75 (25% запас) |

Калькулятор використовує коефіцієнт запасу `derating_factor`, що враховує нелінійність розрядної кривої, падіння ємності на морозі та саморозряд за роки роботи.

## Реалізація калькулятора на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PHASES 8

typedef struct {
    const char *name;      /* назва технологічної підфази */
    double current_ma;     /* струм споживання підфази, мА */
    double duration_ms;    /* тривалість підфази, мс */
} power_phase_t;

typedef struct {
    power_phase_t phases[MAX_PHASES];
    size_t phase_count;
    double sleep_current_ua;     /* струм сну всієї плати, мкА */
    double cycle_period_s;       /* повний період між циклами, с */
    double battery_capacity_mah; /* номінальна ємність батареї, мА·год */
    double derating_factor;      /* коефіцієнт корисної ємності (0.0..1.0) */
} power_profile_config_t;

typedef struct {
    double total_active_time_ms; /* сумарний час активного вікна t_on, мс */
    double total_active_charge_uc;/* сумарний активний заряд Q_on, мкКл (мкА·с) */
    double sleep_charge_uc;      /* заряд уві сні Q_off, мкКл */
    double avg_current_ua;       /* середній струм I_avg, мкА */
    double duty_cycle;           /* коефіцієнт шпаруватості D */
    double active_energy_share;  /* частка енергії активної фази, % */
    double sleep_energy_share;   /* частка енергії фази сну, % */
    double battery_lifetime_years;/* термін автономності, років */
    double saturation_period_s;  /* точка насичення T_90, с */
    bool valid;
} power_profile_report_t;

power_profile_report_t evaluate_power_profile(const power_profile_config_t *cfg) {
    power_profile_report_t rep = {0};
    if (!cfg || cfg->cycle_period_s <= 0.0 || cfg->phase_count == 0 || cfg->phase_count > MAX_PHASES) {
        return rep;
    }

    double t_on_ms = 0.0;
    double q_on_uc = 0.0;

    for (size_t i = 0; i < cfg->phase_count; ++i) {
        const power_phase_t *p = &cfg->phases[i];
        if (p->duration_ms < 0.0 || p->current_ma < 0.0) {
            return rep;
        }
        t_on_ms += p->duration_ms;
        /* заряд підфази в мкКл: мА * мс = мкКл (мкА * с) */
        q_on_uc += (p->current_ma * 1000.0) * (p->duration_ms / 1000.0);
    }

    double t_on_s = t_on_ms / 1000.0;
    if (t_on_s >= cfg->cycle_period_s) {
        return rep; /* активний час перевищує період циклу */
    }

    double t_off_s = cfg->cycle_period_s - t_on_s;
    double q_off_uc = cfg->sleep_current_ua * t_off_s;
    double q_total_uc = q_on_uc + q_off_uc;

    rep.total_active_time_ms = t_on_ms;
    rep.total_active_charge_uc = q_on_uc;
    rep.sleep_charge_uc = q_off_uc;
    rep.duty_cycle = t_on_s / cfg->cycle_period_s;
    rep.avg_current_ua = q_total_uc / cfg->cycle_period_s;
    rep.active_energy_share = (q_on_uc / q_total_uc) * 100.0;
    rep.sleep_energy_share = (q_off_uc / q_total_uc) * 100.0;

    if (rep.avg_current_ua > 0.0 && cfg->battery_capacity_mah > 0.0) {
        double eff_cap_uah = cfg->battery_capacity_mah * cfg->derating_factor * 1000.0;
        double hours = eff_cap_uah / rep.avg_current_ua;
        rep.battery_lifetime_years = hours / (24.0 * 365.25);
    }

    if (cfg->sleep_current_ua > 0.0) {
        /* T_90: період, за якого Q_off = 9 * Q_on */
        rep.saturation_period_s = (9.0 * q_on_uc) / cfg->sleep_current_ua;
    }

    rep.valid = true;
    return rep;
}

void print_profile_report(const power_profile_config_t *cfg, const power_profile_report_t *rep) {
    if (!rep || !rep->valid) {
        printf("Помилка: некоректні параметри профілю живлення!\n");
        return;
    }

    printf("================ ЗВІТ ЕНЕРГЕТИЧНОГО ПРОФІЛЮ ================\n");
    printf("Декомпозиція активного вікна (t_on = %.2f мс):\n", rep->total_active_time_ms);
    for (size_t i = 0; i < cfg->phase_count; ++i) {
        const power_phase_t *p = &cfg->phases[i];
        double q_phase = (p->current_ma * 1000.0) * (p->duration_ms / 1000.0);
        double share = (q_phase / rep->total_active_charge_uc) * 100.0;
        printf("  [%zu] %-20s | %6.2f мА | %6.2f мс | %7.1f мкКл (%5.1f%%)\n",
               i + 1, p->name, p->current_ma, p->duration_ms, q_phase, share);
    }
    printf("------------------------------------------------------------\n");
    printf("Шпаруватість D:             %.7f (%.5f%%)\n", rep->duty_cycle, rep->duty_cycle * 100.0);
    printf("Струм сну I_sleep:          %.2f мкА\n", cfg->sleep_current_ua);
    printf("Середній інтегральний струм: %.2f мкА\n", rep->avg_current_ua);
    printf("Розподіл енергії за цикл:   Активність: %.1f%% | Сон: %.1f%%\n",
           rep->active_energy_share, rep->sleep_energy_share);
    printf("Розрахункова автономність:  %.2f років\n", rep->battery_lifetime_years);
    printf("Точка насичення T_90:       %.0f с (%.1f хв)\n",
           rep->saturation_period_s, rep->saturation_period_s / 60.0);
    printf("============================================================\n");
}

int main(void) {
    power_profile_config_t lora_node = {
        .phases = {
            { .name = "Кварц + PLL старт",    .current_ma =  8.0, .duration_ms =  1.5 },
            { .name = "Живлення + АЦП давача",.current_ma =  5.0, .duration_ms =  3.0 },
            { .name = "Обробка + AES-128",    .current_ma = 18.0, .duration_ms =  1.2 },
            { .name = "Радіопередача LoRa TX",.current_ma = 45.0, .duration_ms = 22.0 },
            { .name = "Прийом квитанції RX",  .current_ma = 11.0, .duration_ms =  6.0 },
            { .name = "Перехід у глибокий сон",.current_ma=  3.0, .duration_ms =  0.3 }
        },
        .phase_count = 6,
        .sleep_current_ua = 2.8,       /* 2.8 мкА в глибокому сні */
        .cycle_period_s = 600.0,       /* 1 раз на 10 хвилин */
        .battery_capacity_mah = 2600.0,/* елемент Li-SOCl2 AA 2600 мА·год */
        .derating_factor = 0.85        /* 15% запас на саморозряд і температуру */
    };

    power_profile_report_t report = evaluate_power_profile(&lora_node);
    print_profile_report(&lora_node, &report);
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <numeric>
#include <expected>

namespace embedded::power {

using namespace std::chrono_literals;

struct PowerPhase {
    std::string name;
    double current_ma{0.0};
    std::chrono::duration<double, std::milli> duration{0.0ms};
};

struct BatterySpec {
    double nominal_capacity_mah{0.0};
    double derating_factor{0.85};
};

struct DeviceProfileConfig {
    std::vector<PowerPhase> phases;
    double sleep_current_ua{0.0};
    std::chrono::seconds cycle_period{0s};
    BatterySpec battery{};
};

struct ProfileEvaluationReport {
    std::chrono::duration<double, std::milli> total_active_time{0.0ms};
    double total_active_charge_uc{0.0};
    double sleep_charge_uc{0.0};
    double avg_current_ua{0.0};
    double duty_cycle{0.0};
    double active_energy_share_pct{0.0};
    double sleep_energy_share_pct{0.0};
    double battery_lifetime_years{0.0};
    std::chrono::seconds saturation_period{0s};
};

enum class ProfileError {
    EmptyPhases,
    InvalidDuration,
    ActiveExceedsPeriod,
    InvalidBattery
};

[[nodiscard]] constexpr auto evaluate_profile(const DeviceProfileConfig& cfg) noexcept
    -> std::expected<ProfileEvaluationReport, ProfileError>
{
    if (cfg.phases.empty()) {
        return std::unexpected(ProfileError::EmptyPhases);
    }
    if (cfg.cycle_period <= 0s) {
        return std::unexpected(ProfileError::InvalidDuration);
    }
    if (cfg.battery.nominal_capacity_mah <= 0.0 || cfg.battery.derating_factor <= 0.0) {
        return std::unexpected(ProfileError::InvalidBattery);
    }

    double total_active_ms = 0.0;
    double q_on_uc = 0.0;

    for (const auto& phase : cfg.phases) {
        if (phase.duration.count() < 0.0 || phase.current_ma < 0.0) {
            return std::unexpected(ProfileError::InvalidDuration);
        }
        total_active_ms += phase.duration.count();
        /* заряд підфази в мкКл: (мА * 1000 мкА/мА) * (мс / 1000 с/мс) = мкА * с */
        q_on_uc += phase.current_ma * phase.duration.count();
    }

    const double t_on_s = total_active_ms / 1000.0;
    const double period_s = std::chrono::duration<double>(cfg.cycle_period).count();

    if (t_on_s >= period_s) {
        return std::unexpected(ProfileError::ActiveExceedsPeriod);
    }

    const double t_off_s = period_s - t_on_s;
    const double q_off_uc = cfg.sleep_current_ua * t_off_s;
    const double q_total_uc = q_on_uc + q_off_uc;

    ProfileEvaluationReport rep{};
    rep.total_active_time = std::chrono::duration<double, std::milli>(total_active_ms);
    rep.total_active_charge_uc = q_on_uc;
    rep.sleep_charge_uc = q_off_uc;
    rep.duty_cycle = t_on_s / period_s;
    rep.avg_current_ua = q_total_uc / period_s;
    rep.active_energy_share_pct = (q_on_uc / q_total_uc) * 100.0;
    rep.sleep_energy_share_pct = (q_off_uc / q_total_uc) * 100.0;

    const double eff_capacity_uah = cfg.battery.nominal_capacity_mah * cfg.battery.derating_factor * 1000.0;
    const double lifetime_hours = eff_capacity_uah / rep.avg_current_ua;
    rep.battery_lifetime_years = lifetime_hours / (24.0 * 365.25);

    if (cfg.sleep_current_ua > 0.0) {
        const double sat_s = (9.0 * q_on_uc) / cfg.sleep_current_ua;
        rep.saturation_period = std::chrono::seconds(static_cast<long long>(sat_s));
    }

    return rep;
}

void print_report(const DeviceProfileConfig& cfg, const ProfileEvaluationReport& rep) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "================ ЗВІТ ЕНЕРГЕТИЧНОГО ПРОФІЛЮ ================\n";
    std::cout << "Декомпозиція активного вікна (t_on = " << rep.total_active_time.count() << " мс):\n";

    size_t idx = 1;
    for (const auto& phase : cfg.phases) {
        const double q_phase = phase.current_ma * phase.duration.count();
        const double share = (q_phase / rep.total_active_charge_uc) * 100.0;
        std::cout << "  [" << idx++ << "] " << std::left << std::setw(22) << phase.name
                  << " | " << std::right << std::setw(6) << phase.current_ma << " мА"
                  << " | " << std::setw(6) << phase.duration.count() << " мс"
                  << " | " << std::setw(7) << q_phase << " мкКл ("
                  << std::setw(5) << share << " %)\n";
    }
    std::cout << "------------------------------------------------------------\n";
    std::cout << "Шпаруватість D:             " << std::setprecision(7) << rep.duty_cycle
              << " (" << std::setprecision(5) << (rep.duty_cycle * 100.0) << " %)\n";
    std::cout << std::setprecision(2);
    std::cout << "Струм сну I_sleep:          " << cfg.sleep_current_ua << " мкА\n";
    std::cout << "Середній інтегральний струм: " << rep.avg_current_ua << " мкА\n";
    std::cout << "Розподіл енергії за цикл:   Активність: " << rep.active_energy_share_pct
              << " % | Сон: " << rep.sleep_energy_share_pct << " %\n";
    std::cout << "Розрахункова автономність:  " << rep.battery_lifetime_years << " років\n";
    std::cout << "Точка насичення T_90:       " << rep.saturation_period.count() << " с ("
              << (rep.saturation_period.count() / 60) << " хв)\n";
    std::cout << "============================================================\n";
}

} // namespace embedded::power

int main() {
    using namespace embedded::power;

    const DeviceProfileConfig lora_node{
        .phases = {
            { "Кварц + PLL старт",     8.0, 1.5ms },
            { "Живлення + АЦП давача", 5.0, 3.0ms },
            { "Обробка + AES-128",    18.0, 1.2ms },
            { "Радіопередача LoRa TX",45.0, 22.0ms },
            { "Прийом квитанції RX",  11.0, 6.0ms },
            { "Перехід у глибокий сон",3.0, 0.3ms }
        },
        .sleep_current_ua = 2.8,
        .cycle_period = 600s,
        .battery = {
            .nominal_capacity_mah = 2600.0,
            .derating_factor = 0.85
        }
    };

    const auto report = evaluate_profile(lora_node);
    if (!report) {
        std::cerr << "Помилка аналізу профілю енергоспоживання\n";
        return 1;
    }

    print_report(lora_node, *report);
    return 0;
}
```
:::

## Інтерпретація результатів профілювання

Звіт калькулятора дає розробнику конкретні інженерні вказівки:
1. **Аналіз часток заряду підфаз:** якщо спалах радіопередачі забирає понад 70% активного заряду, оптимізація швидкості обчислень мікроконтролера дасть мінімальний ефект. У цьому випадку слід зменшувати потужність передавача або переходити на швидші схеми модуляції (наприклад, SF7 замість SF12 у LoRa).
2. **Аналіз балансу активності та сну:** якщо частка сну `sleep_energy_share` становить понад 85–90%, подовження періоду циклу більше не принесе відчутної економії. Для подальшого зростання автономності необхідно знижувати струм сну `I_sleep` (заміна LDO, аудит підтяжок).
3. **Оцінка запасу ємності:** різниця між номінальною та ефективною ємністю показує ціну температурних коливань та саморозряду. Якщо розрахункова автономність перевищує 15 років, лімітуючим фактором стає не розряд від мікроконтролера, а фізична деградація ущільнювачів та хімічний розклад електроліту елемента живлення.
