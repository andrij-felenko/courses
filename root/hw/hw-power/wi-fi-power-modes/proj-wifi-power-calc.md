# ⚙️ Калькулятор енергоспоживання та автономності Wi-Fi вузла

Оцінка терміну служби батареї для автономного пристрою з бездротовим інтерфейсом Wi-Fi вимагає ретельного врахування не лише стаціонарних струмів у режимах передачі та сну, а й тонких перехідних процесів: тривалості стабілізації опорного кварцового генератора, дрейфу годинника реального часу (RTC) під час очікування маякових інтервалів DTIM, накладних витрат на відновлення криптографічного контексту та випадкових затримок доступу до радіоефіру через колізії CSMA/CA.

Спрощені методики розрахунку, які множать струм передавача на тривалість корисного пакета, дають похибку в 10–50 разів, оскільки повністю ігнорують енергію, що витрачається на сканування каналів, обмін службовими кадрами асоціації, очікування відповідей DHCP-сервера та роботу вихідних кіл радіотракту під час синхронізації фазового автопідстроювання частоти (PLL).

Нижче наведено програмну імітаційну модель, яка реалізує дискретний підсумок витраченого електричного заряду `Q = ∑ I_k · t_k` для чотирьох фундаментальних архітектурних стратегій живлення Wi-Fi вузла:

1. **Cold Boot (Повний холодний запуск)** — після кожного періоду сну мікроконтролер скидається до початкового стану. Виконується повна ініціалізація радіотракту, сканування всіх 13 каналів діапазону 2.4 ГГц, відправка запитів автентифікації та асоціації, 4-етапне криптографічне рукостискання WPA2/WPA3 для генерації парних сесійних ключів (PTK), 4-етапна оренда IP-адреси за протоколом DHCP (Discover, Offer, Request, ACK) та перевірка адреси через ARP.
2. **Fast Reconnect (Швидке відновлення сесії)** — мікроконтролер прокидається з режиму Deep-Sleep зі збереженням критичних мережевих параметрів у захищеній пам'яті низькоспоживаючого домену (RTC Fast/Slow Memory). Пропускається сканування каналів (приймач одразу налаштовується на збережений канал AP), використовується кеш ідентифікаторів безпеки PMKSA (що скорочує рукостискання до швидкої реасоціації), а замість DHCP застосовується збережена статична IP-конфігурація або перевірений кеш оренди.
3. **Light-Sleep DTIM-3 (Безперервне підтримання з'єднання)** — радіотракт і обчислювальні ядра переводяться в режим тактового блокування, проте оперативна пам'ять (SRAM) залишається під напругою ретенції. Вузол періодично прокидається за таймером RTC для прийому кожного 3-го DTIM-маяка, відстежуючи бітову карту індикації трафіку (TIM), і миттєво повертається до сну, якщо даних для нього немає.
4. **Wi-Fi 6 TWT (Target Wake Time)** — пристрій узгоджує з точкою доступу індивідуальний розклад сеансів зв'язку. Вузол повністю звільняється від необхідності приймати проміжні маякові кадри й занурюється в найглибший стан сну на довільний час (від часток секунди до місяців), виходячи в ефір строго в призначене вікно обслуговування (Service Period).

## Програмна реалізація моделі

Програма розраховує повний заряд циклу в мікрокулонах (мкКл), середній струм споживання в мікроамперах (мкА), а також прогнозований час автономної роботи в добах та роках з урахуванням хімічного саморозряду джерела струму.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>

typedef struct {
    double v_bat;               /* Напруга батареї, В */
    double cap_mah;             /* Паспортна ємність, мА·год */
    double self_discharge_pct;  /* Річний саморозряд, % */
    double k_use;               /* Коефіцієнт корисної ємності */
} BatterySpec;

typedef struct {
    double i_deep_sleep_ua;     /* Струм Deep-Sleep, мкА */
    double i_light_sleep_ma;    /* Струм Light-Sleep, мА */
    double i_cpu_active_ma;     /* Струм CPU Modem-Sleep, мА */
    double i_rx_ma;             /* Струм прийому RX, мА */
    double i_tx_ma;             /* Струм передачі TX (+18 dBm), мА */
    double t_xtal_settle_ms;    /* Час стабілізації PLL кварцу, мс */
    double rtc_drift_ppm;       /* Температурний дрейф RTC кварцу, ppm */
} TransceiverSpec;

typedef struct {
    double q_cycle_uc;          /* Заряд на один цикл, мкКл (мА·мс) */
    double i_avg_ua;            /* Середній струм споживання, мкА */
    double life_days;           /* Час автономної роботи, діб */
    double life_years;          /* Час автономної роботи, років */
} SimResult;

SimResult sim_cold_boot(const BatterySpec *bat, const TransceiverSpec *trx, double interval_s) {
    /* Фази: Boot (40мс/20мА), Scan 13ch (200мс/75мА), Assoc+WPA (120мс/95мА), DHCP (1200мс/70мА), TX Data (20мс/220мА) */
    double q_active_uc = 40.0 * 20.0 + 200.0 * 75.0 + 120.0 * 95.0 + 1200.0 * 70.0 + 20.0 * 220.0;
    double t_active_s = (40.0 + 200.0 + 120.0 + 1200.0 + 20.0) / 1000.0;
    double t_sleep_s = (interval_s > t_active_s) ? (interval_s - t_active_s) : 0.0;
    double q_sleep_uc = (trx->i_deep_sleep_ua / 1000.0) * (t_sleep_s * 1000.0);
    double q_total_uc = q_active_uc + q_sleep_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

SimResult sim_fast_reconnect(const BatterySpec *bat, const TransceiverSpec *trx, double interval_s) {
    /* Фази: Wake RTC (5мс/15мА), Ch Assoc PMKSA (35мс/85мА), Static IP TX (15мс/220мА) */
    double q_active_uc = 5.0 * 15.0 + 35.0 * 85.0 + 15.0 * 220.0;
    double t_active_s = (5.0 + 35.0 + 15.0) / 1000.0;
    double t_sleep_s = (interval_s > t_active_s) ? (interval_s - t_active_s) : 0.0;
    double q_sleep_uc = (trx->i_deep_sleep_ua / 1000.0) * (t_sleep_s * 1000.0);
    double q_total_uc = q_active_uc + q_sleep_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

SimResult sim_dtim_light_sleep(const BatterySpec *bat, const TransceiverSpec *trx, int dtim, double interval_s) {
    double t_dtim_s = dtim * 0.1024;
    double t_guard_ms = 2.0 * t_dtim_s * trx->rtc_drift_ppm * 0.001 + trx->t_xtal_settle_ms;
    double t_beacon_rx_ms = 1.2;
    double q_beacon_uc = trx->i_cpu_active_ma * trx->t_xtal_settle_ms + trx->i_rx_ma * (t_guard_ms + t_beacon_rx_ms);
    double q_dtim_sleep_uc = trx->i_light_sleep_ma * (t_dtim_s * 1000.0 - (t_guard_ms + t_beacon_rx_ms));
    double i_background_ma = (q_beacon_uc + q_dtim_sleep_uc) / (t_dtim_s * 1000.0);

    /* TX подія: 15 мс активності при 220 мА */
    double q_tx_event_uc = 15.0 * 220.0;
    double q_total_uc = (i_background_ma * interval_s * 1000.0) + q_tx_event_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

SimResult sim_wifi6_twt(const BatterySpec *bat, const TransceiverSpec *trx, double interval_s) {
    /* TWT SP: 10мс RX (70мА) + 5мс TX (220мА) */
    double q_sp_uc = 10.0 * 70.0 + 5.0 * 220.0;
    double t_active_s = 15.0 / 1000.0;
    double t_sleep_s = (interval_s > t_active_s) ? (interval_s - t_active_s) : 0.0;
    double q_sleep_uc = (trx->i_deep_sleep_ua / 1000.0) * (t_sleep_s * 1000.0);
    double q_total_uc = q_sp_uc + q_sleep_uc;

    SimResult res;
    res.q_cycle_uc = q_total_uc;
    res.i_avg_ua = (q_total_uc / (interval_s * 1000.0)) * 1000.0;
    
    double eff_cap_mah = bat->cap_mah * bat->k_use;
    double self_leak_ua = (eff_cap_mah * (bat->self_discharge_pct / 100.0) * 1000.0) / 8760.0;
    double total_current_ma = (res.i_avg_ua + self_leak_ua) / 1000.0;
    
    double life_hours = eff_cap_mah / total_current_ma;
    res.life_days = life_hours / 24.0;
    res.life_years = life_hours / 8760.0;
    return res;
}

int main(void) {
    BatterySpec aa_lithium = { 3.0, 2400.0, 1.0, 0.85 };
    TransceiverSpec esp32 = { 10.0, 1.2, 20.0, 75.0, 240.0, 1.5, 50.0 };
    double interval_s = 600.0; /* Відправка даних раз на 10 хвилин */

    SimResult r_cold = sim_cold_boot(&aa_lithium, &esp32, interval_s);
    SimResult r_fast = sim_fast_reconnect(&aa_lithium, &esp32, interval_s);
    SimResult r_dtim = sim_dtim_light_sleep(&aa_lithium, &esp32, 3, interval_s);
    SimResult r_twt  = sim_wifi6_twt(&aa_lithium, &esp32, interval_s);

    printf("Стратегія 1 (Cold Boot):       I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_cold.i_avg_ua, r_cold.life_days, r_cold.life_years);
    printf("Стратегія 2 (Fast Reconnect):   I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_fast.i_avg_ua, r_fast.life_days, r_fast.life_years);
    printf("Стратегія 3 (Light DTIM-3):    I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_dtim.i_avg_ua, r_dtim.life_days, r_dtim.life_years);
    printf("Стратегія 4 (Wi-Fi 6 TWT):     I_avg = %7.2f uA | Життя = %6.1f діб (%4.2f р)\n",
           r_twt.i_avg_ua,  r_twt.life_days,  r_twt.life_years);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <string_view>

struct BatterySpec {
    double voltage_v{3.0};
    double capacity_mah{2400.0};
    double self_discharge_pct_year{1.0};
    double capacity_retention_factor{0.85};

    [[nodiscard]] constexpr double effective_capacity_mah() const noexcept {
        return capacity_mah * capacity_retention_factor;
    }

    [[nodiscard]] constexpr double self_discharge_leak_ua() const noexcept {
        return (effective_capacity_mah() * (self_discharge_pct_year / 100.0) * 1000.0) / 8760.0;
    }
};

struct TransceiverSpec {
    double deep_sleep_current_ua{10.0};
    double light_sleep_current_ma{1.2};
    double cpu_active_current_ma{20.0};
    double rx_current_ma{75.0};
    double tx_current_ma{240.0};
    double xtal_settle_time_ms{1.5};
    double rtc_drift_ppm{50.0};
};

struct SimulationResult {
    double cycle_charge_uc{0.0};
    double average_current_ua{0.0};
    double lifetime_days{0.0};
    double lifetime_years{0.0};
};

class WiFiPowerSimulator {
public:
    explicit constexpr WiFiPowerSimulator(BatterySpec battery, TransceiverSpec transceiver) noexcept
        : battery_(battery), trx_(transceiver) {}

    [[nodiscard]] SimulationResult simulate_cold_boot(double interval_seconds) const noexcept {
        const double q_active_uc = 40.0 * 20.0 + 200.0 * 75.0 + 120.0 * 95.0 + 1200.0 * 70.0 + 20.0 * 220.0;
        const double t_active_s = (40.0 + 200.0 + 120.0 + 1200.0 + 20.0) / 1000.0;
        const double t_sleep_s = std::max(0.0, interval_seconds - t_active_s);
        const double q_sleep_uc = (trx_.deep_sleep_current_ua / 1000.0) * (t_sleep_s * 1000.0);
        return compute_metrics(q_active_uc + q_sleep_uc, interval_seconds);
    }

    [[nodiscard]] SimulationResult simulate_fast_reconnect(double interval_seconds) const noexcept {
        const double q_active_uc = 5.0 * 15.0 + 35.0 * 85.0 + 15.0 * 220.0;
        const double t_active_s = (5.0 + 35.0 + 15.0) / 1000.0;
        const double t_sleep_s = std::max(0.0, interval_seconds - t_active_s);
        const double q_sleep_uc = (trx_.deep_sleep_current_ua / 1000.0) * (t_sleep_s * 1000.0);
        return compute_metrics(q_active_uc + q_sleep_uc, interval_seconds);
    }

    [[nodiscard]] SimulationResult simulate_dtim_light_sleep(int dtim_multiplier, double interval_seconds) const noexcept {
        const double t_dtim_s = dtim_multiplier * 0.1024;
        const double t_guard_ms = 2.0 * t_dtim_s * trx_.rtc_drift_ppm * 0.001 + trx_.xtal_settle_time_ms;
        constexpr double t_beacon_rx_ms = 1.2;

        const double q_beacon_uc = trx_.cpu_active_current_ma * trx_.xtal_settle_time_ms 
                                 + trx_.rx_current_ma * (t_guard_ms + t_beacon_rx_ms);
        const double q_dtim_sleep_uc = trx_.light_sleep_current_ma * (t_dtim_s * 1000.0 - (t_guard_ms + t_beacon_rx_ms));
        const double i_background_ma = (q_beacon_uc + q_dtim_sleep_uc) / (t_dtim_s * 1000.0);

        constexpr double q_tx_event_uc = 15.0 * 220.0;
        const double q_total_uc = (i_background_ma * interval_seconds * 1000.0) + q_tx_event_uc;
        return compute_metrics(q_total_uc, interval_seconds);
    }

    [[nodiscard]] SimulationResult simulate_wifi6_twt(double interval_seconds) const noexcept {
        constexpr double q_sp_uc = 10.0 * 70.0 + 5.0 * 220.0;
        constexpr double t_active_s = 15.0 / 1000.0;
        const double t_sleep_s = std::max(0.0, interval_seconds - t_active_s);
        const double q_sleep_uc = (trx_.deep_sleep_current_ua / 1000.0) * (t_sleep_s * 1000.0);
        return compute_metrics(q_sp_uc + q_sleep_uc, interval_seconds);
    }

private:
    [[nodiscard]] SimulationResult compute_metrics(double q_total_uc, double interval_seconds) const noexcept {
        SimulationResult res;
        res.cycle_charge_uc = q_total_uc;
        res.average_current_ua = (q_total_uc / (interval_seconds * 1000.0)) * 1000.0;

        const double eff_cap_mah = battery_.effective_capacity_mah();
        const double total_current_ma = (res.average_current_ua + battery_.self_discharge_leak_ua()) / 1000.0;
        const double life_hours = eff_cap_mah / total_current_ma;

        res.lifetime_days = life_hours / 24.0;
        res.lifetime_years = life_hours / 8760.0;
        return res;
    }

    BatterySpec battery_;
    TransceiverSpec trx_;
};

int main() {
    constexpr BatterySpec aa_cell{ 3.0, 2400.0, 1.0, 0.85 };
    constexpr TransceiverSpec esp32_spec{ 10.0, 1.2, 20.0, 75.0, 240.0, 1.5, 50.0 };
    constexpr double interval_s = 600.0; // 10 хвилин

    const WiFiPowerSimulator sim(aa_cell, esp32_spec);

    const auto print_row = [](std::string_view name, const SimulationResult& r) {
        std::cout << std::left << std::setw(30) << name << " | I_avg = " 
                  << std::right << std::setw(7) << std::fixed << std::setprecision(2) << r.average_current_ua << " uA | "
                  << "Життя = " << std::setw(6) << std::setprecision(1) << r.lifetime_days << " діб ("
                  << std::setw(4) << std::setprecision(2) << r.lifetime_years << " р)\n";
    };

    std::cout << "=== Порівняння стратегій живлення Wi-Fi (T_цикл = 10 хв, батарея 2400 мА·год) ===\n";
    print_row("Стратегія 1 (Cold Boot)", sim.simulate_cold_boot(interval_s));
    print_row("Стратегія 2 (Fast Reconnect)", sim.simulate_fast_reconnect(interval_s));
    print_row("Стратегія 3 (Light DTIM-3)", sim.simulate_dtim_light_sleep(3, interval_s));
    print_row("Стратегія 4 (Wi-Fi 6 TWT)", sim.simulate_wifi6_twt(interval_s));

    return 0;
}
```
:::

## Інженерні пастки при проєктуванні батарейних Wi-Fi вузлів

При практичній реалізації низькоспоживаючих вузлів розробники найчастіше стикаються з трьома критичними проблемами, які руйнують теоретичні розрахунки:

1. **Динамічне просідання напруги під час радіоімпульсу (ESR батареї).**
   У момент увімкнення вихідного каскаду підсилювача потужності (PA) на рівень +18...+20 dBm струм навантаження зростає від 10 мкА до 250–350 мА за час менше 1 мкс. Хімічні джерела живлення (особливо літієві дисульфід-залізні Li-FeS2 або літій-тіонілхлоридні Li-SOCl2 комірки) мають помітний внутрішній опір `R_int ≈ 1.0–2.5 Ом`, який додатково зростає при низьких температурах та наприкінці розряду.
   Стрибок струму `ΔI = 0.3 А` на опорі `2.0 Ом` викликає миттєве падіння напруги на виводах батареї на `ΔU = 0.6 В`. Якщо напруга живлення мікроконтролера знижується нижче порога спрацьовування внутрішнього детектора спаду напруги (Brownout Reset, типово 2.5–2.7 В для шини 3.3 В), процесор аварійно скидається, починаючи нескінченний цикл перезавантажень (англ. *brownout loop*).
   *Рішення:* обов'язкове встановлення локального буферного накопичувача — керамічних конденсаторів X5R/X7R ємністю 22–47 мкФ у парі з танталовим конденсатором ємністю 100–220 мкФ із низьким ESR безпосередньо біля виводів живлення радіотракту.

2. **Шторм широкомовного трафіку в режимах зі збереженням асоціації (DTIM).**
   Коли пристрій використовує Light-Sleep і регулярно прокидається на DTIM-маяки, будь-який широкомовний або багатоадресний пакет у локальній мережі (ARP-запити від сусідніх комп'ютерів, широкомовні повідомлення протоколів mDNS, SSDP, NetBIOS, оновлення маршрутизації) змушує точку доступу виставляти біт у карті TIM і транслювати кадр одразу після DTIM-маяка.
   У типовій домашній або корпоративній мережі з десятками клієнтів інтенсивність широкомовних пакетів досягає 5–30 кадрів на секунду. Вузол замість короткого сну перебуває в режимі прийому майже 100% часу, внаслідок чого середній струм зростає з розрахункових 1.5 мА до 30–60 мА, вичерпуючи батарею за кілька днів.
   *Рішення:* ізоляція пристроїв у виділений IoT VLAN із повним фільтруванням широкомовного трафіку на рівні точки доступу, або повний перехід на Deep-Sleep із розривом асоціації після кожного сеансу зв'язку.

3. **Температурний дрейф низькочастотного генератора.**
   Використання внутрішнього низькочастотного RC-генератора замість прецизійного зовнішнього кварцового резонатора 32.768 кГц призводить до похибки частоти до `±1000–5000 ppm`. На інтервалі сну 300 мс похибка часу сягає 1.5 мс, через що приймач змушений вмикатися за 3–4 мс до маяка для гарантованого прийому преамбули. Це подвоює тривалість фази активного прийому RX і збільшує енерговитрати кожного DTIM-пробудження на 80–120%.
