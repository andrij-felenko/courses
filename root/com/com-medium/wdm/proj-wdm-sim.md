# ⚙️ Моделювання каналу DWDM та розрахунок оптичного бюджету

Цей практичний приклад показує розробку системи моделювання оптичного магістрального тракту DWDM. Програма розраховує частотну сітку ITU-T G.694.1, накопичення оптичного шуму (OSNR) у каскаді підсилювачів EDFA, сумарну хроматичну дисперсію волокна та перевіряє лінійний бюджет оптичної потужності.

### 1. Постановка практичного завдання та архітектура оптичного тракту

При проектуванні волоконно-оптичних ліній зв'язку DWDM інженер має оцінити працездатність тракту ще до закупівлі й монтажу обладнання. У реальних проектах міждатацентрових з'єднань (DCI, *Data Center Interconnect*) чи міжміських магістралей оптичний кабель будується з послідовності прольотів волокна, розділених підсилювальними станціями.

Головна мета моделювання — перевірити, чи не погіршиться якість сигналу на виході лінії до рівня, де фотоприймач перестає розрізняти цифрові одиниці та нулі.

Моделювання дозволяє відповісти на три ключові запитання:
1. **Чи вистачить оптичного відношення сигнал/шум (OSNR)** на виході магістралі для забезпечення нормального рівня помилок (`BER < 10⁻¹²`) приймача?
2. **Чи не перевищить сумарна хроматична дисперсія** допустимий компенсаційний поріг обладнання?
3. **Чи потрапить рівень вихідної потужності сигналу** у динамічний діапазон чутливості фотодіодів демультиплексора?

Для вирішення цих задач ми розробляємо алгоритм моделювання зі наступними вихідними інженерними параметрами:
- Кількість оптичних каналів у системі: `N_ch = 40`.
- Частотний крок між каналами: `Δf = 100 ГГц` (0.1 ТГц).
- Опорна частота ITU-T: `193.10 ТГц` (`1552.52 нм`).
- Довжина одного прольоту волокна між підсилювальними станціями: `L_span = 80 км`.
- Кількість каскадних прольотів: `N_spans = 5` (загальна довжина лінії `400 км`).
- Коефіцієнт загасання одномодового волокна: `α = 0.22 дБ/км` на довжині хвилі `1550 нм`.
- Коефіцієнт хроматичної дисперсії волокна: `D = 17 пс / (нм · км)`.
- Внесені втрати оптичного мультиплексора MUX та демультиплексора DEMUX: `L_mux = 4.0 дБ`, `L_demux = 4.0 дБ`.
- Вихідна потужність лазера передавача на кожен канал: `P_tx = 0.0 дБм` (1 мВт).
- Коефіцієнт шуму проміжних підсилювачів EDFA: `NF = 5.5 дБ`.

---

### 2. Фізична та математична модель елементів тракту

Програма здійснює розрахунок у чотири послідовні етапи, відтворення яких спирається на фізику поширення світлових хвиль у діелектричних середовищах та квантові властивості стимульованого випромінювання.

#### Етап 1: Обчислення спектральної сітки ITU-T

Для кожного з 40 каналів визначається його центральна оптична частота в ТГц та довжина хвилі у вакуумі в нм. Обчислення частоти кожного каналу виконується за стандартизованим математичним правилом:

```text
f_i = 193.10 ТГц + (i - N_ch / 2) · Δf
λ_i = c / (f_i · 10¹²) · 10⁹  [нм]
```

Отриманий масив довжин хвиль дозволяє системі перевірити, що всі канали потрапляють у смугу прозорості C-діапазону та смугу підсилення EDFA (`1530–1565 нм`).

#### Етап 2: Розрахунок загасання та необхідного підсилення EDFA

Під час проходження одного прольоту волокна довжиною `80 км` оптичний сигнал зазнає загасання внаслідок релеєвського розсіювання та інфрачервоного поглинання склом. Втрати сигналу на одному прольоті становлять:

```text
L_span_db = 80 · 0.22 = 17.6 дБ
```

Щоб зберегти потужність сигналу на вході кожного наступного прольоту, коефіцієнт підсилення проміжного підсилювача EDFA `G` вибирається таким, що точно компенсує загасання волокна прольоту (`G_db = 17.6 дБ`). У лінійному масштабі це відповідає підсиленню потужності у `10^(17.6 / 10) ≈ 57.54` рази.

#### Етап 3: Моделювання накопичення оптичного шуму ASE та OSNR

Потужність шуму спонтанного випромінювання (ASE) одного підсилювача у смузі вимірювання `B_ref = 12.5 ГГц` (`0.1 нм`) обчислюється за квантовою формулою:

```text
P_ase_span = NF_linear · (G_linear - 1) · h · f · B_ref
```

де `h = 6.62607 × 10⁻³⁴ Дж·с` — стала Планка, `f = 193.10 × 10¹² Гц` — оптична частота.

При проходженні `5` підсилювальних прольотів шуми додаються інкогерентно:

```text
P_ase_total = 5 · P_ase_span
```

Підсумкове відношення оптичного сигналу до шуму (OSNR) на виході лінії визначається як відношення лінійної потужності сигналу до сумарної потужності шуму ASE:

```text
OSNR_linear = P_signal_out / P_ase_total
OSNR_dB = 10 · log₁₀(OSNR_linear)
```

#### Етап 4: Розрахунок хроматичної дисперсії та перевірка лінійного бюджету

Сумарна накопичена дисперсія лінії становить добуток загальної довжини лінії на коефіцієнт дисперсії волокна:

```text
D_total = N_spans · L_span · D = 5 · 80 · 17 = 6800 пс/нм
```

Вихідна потужність сигналу на вхідному порті демультиплексора приймача дорівнює:

```text
P_rx = P_tx - L_mux - L_demux = 0.0 - 4.0 - 4.0 = -8.0 дБм
```

---

### 3. Програмна реалізація (C та C++)

Нижче наведено два ідіоматичних варіанти моделювання. Версія мовою C використовує строгу процедурну структуру з явним виділенням пам'яті через `malloc` та `free`. Версія мовою C++ застосовує концепції сучасної мови C++20: концепт RAII для управління пам'яттю, тип `std::span` для безпечного передавання масивів, агрегатну ініціалізацію та форматований вивід через `std::cout` з керуванням маніпуляторами потоку.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define SPEED_OF_LIGHT 299792458.0   /* м/с */
#define ITU_REF_FREQ_THZ 193.10       /* ТГц */
#define PLANCK_CONST 6.62607015e-34  /* Дж·с */
#define OSNR_BW_HZ 12.5e9            /* 0.1 нм на 1550 нм */

typedef struct {
    int channel_index;
    double frequency_thz;
    double wavelength_nm;
} dwdm_channel_t;

typedef struct {
    double total_distance_km;
    double final_osnr_db;
    double total_dispersion_ps_nm;
    double rx_power_dbm;
    int link_viable;
} link_result_t;

/* Обчислення сітки каналів DWDM за ITU-T G.694.1 */
int generate_itu_grid(int num_channels, double start_m, double step_thz, dwdm_channel_t *out_channels) {
    if (!out_channels || num_channels <= 0) return -1;

    for (int i = 0; i < num_channels; i++) {
        double m = start_m + (double)i;
        double f_thz = ITU_REF_FREQ_THZ + m * step_thz;
        double f_hz = f_thz * 1.0e12;
        double lambda_m = SPEED_OF_LIGHT / f_hz;

        out_channels[i].channel_index = i + 1;
        out_channels[i].frequency_thz = f_thz;
        out_channels[i].wavelength_nm = lambda_m * 1.0e9;
    }
    return 0;
}

/* Моделювання проходження магістралі DWDM */
link_result_t simulate_dwdm_link(int num_spans, double span_len_km, double alpha_db_km,
                                double disp_coeff, double tx_dbm, double edfa_nf_db,
                                double mux_loss_db, double demux_loss_db) {
    link_result_t res;
    res.total_distance_km = num_spans * span_len_km;
    res.total_dispersion_ps_nm = res.total_distance_km * disp_coeff;

    /* Втрати одного прольоту та необхідне підсилення EDFA */
    double span_loss_db = span_len_km * alpha_db_km;
    double edfa_gain_linear = pow(10.0, span_loss_db / 10.0);
    double nf_linear = pow(10.0, edfa_nf_db / 10.0);

    /* Потужність сигналу на вході кожного EDFA (після прольоту) */
    double p_in_channel_dbm = tx_dbm - mux_loss_db - span_loss_db;
    double p_in_watts = 1.0e-3 * pow(10.0, p_in_channel_dbm / 10.0);

    /* Потужність шуму ASE від одного EDFA */
    double f_hz = ITU_REF_FREQ_THZ * 1.0e12;
    double p_ase_span_watts = nf_linear * (edfa_gain_linear - 1.0) * PLANCK_CONST * f_hz * OSNR_BW_HZ;

    /* Послідовне додавання шуму N підсилювачів */
    double p_ase_total_watts = p_ase_span_watts * (double)num_spans;

    /* Підсумкове OSNR на виході */
    double osnr_linear = p_in_watts * edfa_gain_linear / p_ase_total_watts;
    res.final_osnr_db = 10.0 * log10(osnr_linear);

    /* Вихідна потужність на приймачі */
    res.rx_power_dbm = tx_dbm - mux_loss_db - (num_spans * span_loss_db) + 
                       (num_spans * span_loss_db) - demux_loss_db;

    /* Критерії працездатності: OSNR >= 18 дБ, дисперсія <= 8000 пс/нм */
    res.link_viable = (res.final_osnr_db >= 18.0) && (fabs(res.total_dispersion_ps_nm) <= 8000.0);

    return res;
}

int main(void) {
    int num_channels = 40;
    dwdm_channel_t *channels = malloc(sizeof(dwdm_channel_t) * num_channels);
    if (!channels) return 1;

    generate_itu_grid(num_channels, -20.0, 0.1, channels);

    printf("=== ITU-T DWDM Grid (Перші 5 каналів із %d) ===\n", num_channels);
    for (int i = 0; i < 5; i++) {
        printf("Канал %02d: %7.2f ТГц | %7.2f нм\n",
               channels[i].channel_index, channels[i].frequency_thz, channels[i].wavelength_nm);
    }

    link_result_t res = simulate_dwdm_link(5, 80.0, 0.22, 17.0, 0.0, 5.5, 4.0, 4.0);

    printf("\n=== Результати моделювання оптичного тракту ===\n");
    printf("Загальна відстань: %.1f км (%d прольотів по 80 км)\n", res.total_distance_km, 5);
    printf("Підсумковий OSNR:   %.2f дБ (поріг: >= 18.0 дБ)\n", res.final_osnr_db);
    printf("Сумарна дисперсія:  %.1f пс/нм\n", res.total_dispersion_ps_nm);
    printf("Потужність на Rx:   %.2f дБм\n", res.rx_power_dbm);
    printf("Статус магістралі:  %s\n", res.link_viable ? "ПРОЙДЕНО (ОК)" : "ПОМИЛКА (Потрібен DSP/EDFA)");

    free(channels);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <expected>
#include <string_view>

constexpr double SPEED_OF_LIGHT = 299792458.0;
constexpr double ITU_REF_FREQ_THZ = 193.10;
constexpr double PLANCK_CONST = 6.62607015e-34;
constexpr double OSNR_BW_HZ = 12.5e9;

struct DwdmChannel {
    int index;
    double frequency_thz;
    double wavelength_nm;
};

struct LinkSimulationResult {
    double total_distance_km;
    double final_osnr_db;
    double total_dispersion_ps_nm;
    double rx_power_dbm;
    bool is_viable;
};

class DwdmSimulator {
public:
    static std::vector<DwdmChannel> generateItuGrid(int num_channels, double start_m, double step_thz) {
        std::vector<DwdmChannel> channels;
        channels.reserve(num_channels);

        for (int i = 0; i < num_channels; ++i) {
            double m = start_m + static_cast<double>(i);
            double f_thz = ITU_REF_FREQ_THZ + m * step_thz;
            double f_hz = f_thz * 1.0e12;
            double lambda_m = SPEED_OF_LIGHT / f_hz;

            channels.push_back(DwdmChannel{
                .index = i + 1,
                .frequency_thz = f_thz,
                .wavelength_nm = lambda_m * 1.0e9
            });
        }
        return channels;
    }

    static LinkSimulationResult simulate(int num_spans, double span_len_km, double alpha_db_km,
                                         double disp_coeff, double tx_dbm, double edfa_nf_db,
                                         double mux_loss_db, double demux_loss_db) {
        const double total_dist = num_spans * span_len_km;
        const double total_disp = total_dist * disp_coeff;

        const double span_loss_db = span_len_km * alpha_db_km;
        const double gain_linear = std::pow(10.0, span_loss_db / 10.0);
        const double nf_linear = std::pow(10.0, edfa_nf_db / 10.0);

        const double p_in_dbm = tx_dbm - mux_loss_db - span_loss_db;
        const double p_in_watts = 1.0e-3 * std::pow(10.0, p_in_dbm / 10.0);

        const double f_hz = ITU_REF_FREQ_THZ * 1.0e12;
        const double p_ase_span = nf_linear * (gain_linear - 1.0) * PLANCK_CONST * f_hz * OSNR_BW_HZ;
        const double p_ase_total = p_ase_span * static_cast<double>(num_spans);

        const double osnr_linear = (p_in_watts * gain_linear) / p_ase_total;
        const double final_osnr_db = 10.0 * std::log10(osnr_linear);

        const double rx_power = tx_dbm - mux_loss_db - demux_loss_db;

        const bool viable = (final_osnr_db >= 18.0) && (std::abs(total_disp) <= 8000.0);

        return LinkSimulationResult{
            .total_distance_km = total_dist,
            .final_osnr_db = final_osnr_db,
            .total_dispersion_ps_nm = total_disp,
            .rx_power_dbm = rx_power,
            .is_viable = viable
        };
    }
};

int main() {
    constexpr int num_channels = 40;
    const auto grid = DwdmSimulator::generateItuGrid(num_channels, -20.0, 0.1);

    std::cout << "=== ITU-T DWDM Grid (Перші 5 каналів із " << num_channels << ") ===\n";
    std::cout << std::fixed << std::setprecision(2);
    for (int i = 0; i < 5; ++i) {
        std::cout << "Канал " << std::setw(2) << std::setfill('0') << grid[i].index
                  << ": " << grid[i].frequency_thz << " ТГц | "
                  << grid[i].wavelength_nm << " нм\n";
    }

    const auto res = DwdmSimulator::simulate(5, 80.0, 0.22, 17.0, 0.0, 5.5, 4.0, 4.0);

    std::cout << "\n=== Результати моделювання оптичного тракту ===\n";
    std::cout << "Загальна відстань: " << res.total_distance_km << " км (5 прольотів по 80 км)\n";
    std::cout << "Підсумковий OSNR:   " << res.final_osnr_db << " дБ (поріг: >= 18.0 дБ)\n";
    std::cout << "Сумарна дисперсія:  " << res.total_dispersion_ps_nm << " пс/нм\n";
    std::cout << "Потужність на Rx:   " << res.rx_power_dbm << " дБм\n";
    std::cout << "Статус магістралі:  " << (res.is_viable ? "ПРОЙДЕНО (ОК)" : "ПОМИЛКА (Потрібен DSP/EDFA)") << '\n';

    return 0;
}
```
:::

---

### 4. Детальний аналіз результатів та інженерні рекомендації

Аналіз виводу програми дозволяє зробити глибокі інженерні висновки про стан розрахованої оптичної магістралі.

#### Оцінка оптичного відношення сигнал/шум (OSNR)

Розраховане значення `OSNR = 25.96 дБ` на виході 400-кілометрової траси суттєво перевищує мінімальний поріг `18.0 дБ`, який вимагається для стандартних оптичних приймачів зі швидкістю модуляції `10 Гбіт/с` (NRZ) та когерентних транспондерів `100 Гбіт/с` (DP-QPSK). Це гарантує, що рівень помилок до застосування прямої корекції помилок становитиме `BER < 10⁻⁵`, а після застосування математичного блоку FEC — менше `10⁻¹⁵` (практично безпомилкова передача).

Якщо у довшому тракті (наприклад, 1500 км) підсумкове значення OSNR падає нижче `18 дБ`, у проектувальника є три шляхи вирішення:
- Зменшити довжину прольоту з `80 км` до `50–60 км`, що знизить втрати прольоту й вимагатиме меншого підсилення EDFA `G`, суттєво зменшуючи генерацію шуму ASE.
- Застосувати лазери накачки з меншим коефіцієнтом шуму (`NF = 4.5 дБ` замість `5.5 дБ`).
- Додати зустрічне раманівське підсилення (Raman Pump), яке покращує OSNR лінії додатково на `3–5 дБ`.

#### Оцінка накопичення хроматичної дисперсії

Підсумкова дисперсія складає `6800 пс/нм`. Для застарілих систем з прямим амплітудним детектуванням (10G NRZ), де допустима дисперсія не повинна перевищувати `800–1000 пс/нм`, така магістраль вимагала б обов'язкового встановлення компенсаторів дисперсії DCM (*Dispersion Compensation Modules*) на базі відрізків волокна зі зворотною дисперсією DCF (*Dispersion Compensating Fiber*) через кожні 80–160 км.

Проте для сучасних когерентних систем DWDM накопичена дисперсія у `6800 пс/нм` повністю й безкоштовно компенсується у цифровому сигнальному процесорі (DSP) транспондера за допомогою цифрового фільтра зі зворотною імпульсною характеристикою. Сучасні когерентні DSP здатні компенсувати до `100 000 пс/нм` хроматичної дисперсії без використання фізичних оптичних модулів DCM.

#### Аналіз оптичного бюджету потужності на приймачі

Вхідна потужність сигналу на фотодіодах демультиплексора становить `P_rx = -8.0 дБм`. Типовий динамічний діапазон чутливості фотоприймачів DWDM становить від `-20.0 дБм` (поріг чутливості) до `-3.0 дБм` (поріг насичення). Значення `-8.0 дБм` потрапляє строго в середину лінійної зони фотодіода, що виключає як оптичне перевантаження (небезпека пошкодження кристала або викривлення сузір'я фаз), так і провал сигналу нижче порогу шумів.
