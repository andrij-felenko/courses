# ⚙️ Практичний обчислювач бюджету радіолінії та максимуму дальності

При проектуванні та налагодженні сучасних бездротових систем (від локальних датчиків LoRa/Zigbee до радіорелейних ліній та телеметрії безпілотних апаратів) інженерам необхідно регулярно розраховувати баланс потужності, перевіряти запас за згасанням (*Link Margin*) та обчислювати граничну відстань стійкого прийому (*Maximum Coverage Range*).

Нижче наведено завершений, готовий до практичного використання обчислювальний модуль для розрахунку бюджету лінії, аналізу чутливості та оцінки граничного радіуса покриття радіосистеми.

---

## Архітектура та математична модель обчислювального ядра

Обчислювальний модуль приймає на вхід три незалежні групи конфігураційних параметрів, що описують фізичну структуру радіоканала:

1. **Параметри передавача (TX):**
   - Вихідну потужність підсилювача `P_TX` (у dBm).
   - Сумарні втрати у з'єднувальному кателі, фільтрах та пігтейлі `L_tx` (у dB).
   - Коефіцієнт підсилення антени передавача `G_TX` (у dBi).

2. **Параметри траси поширення хвилі (Channel):**
   - Робочу несучу частоту сигналу `f` (у МГц).
   - Поточну фізичну відстань між антенами `d` (у км).
   - Загальне атмосферне поглинання `L_atm` (у dB).
   - Закладений інженерний запас на дрібномасштабні завмирання `L_fade` (у dB).
   - Додаткові технологічні втрати (разом: розузгодження поляризації, розстроювання частоти гетеродинів) `L_misc` (у dB).

3. **Параметри приймача (RX):**
   - Коефіцієнт підсилення приймальної антени `G_RX` (у dBi).
   - Втрати у кателі та роз'ємах приймача `L_rx` (у dB).
   - Еквівалентну шумова смуга пропускання `B` (у Гц).
   - Власний коефіцієнт шуму приймача `N_F` (у dB).
   - Порогове співвідношення сигнал/шум демодулятора `SNR_min` (у dB).

### Послідовність обчислювальних кроків:

- **Крок 1 (Обчислення EIRP):** `EIRP = P_TX - L_tx + G_TX` (dBm).
- **Крок 2 (Обчислення FSPL):** `FSPL = 20·log10(d_km) + 20·log10(f_MHz) + 32.44` (dB).
- **Крок 3 (Загальні втрати траси):** `L_total = FSPL + L_atm + L_fade + L_misc` (dB).
- **Крок 4 (Потужність сигналу у RX):** `P_RX = EIRP - L_total + G_RX - L_rx` (dBm).
- **Крок 5 (Поріг чутливості RX):** `P_sens = -173.98 + 10·log10(B_Hz) + N_F + SNR_min` (dBm).
- **Крок 6 (Запас радіолінії):** `Margin = P_RX - P_sens` (dB).
- **Крок 7 (Гранична відстань d_max):** Обчислюються максимально припустимі втрати у вільному просторі `FSPL_max` при умові `Margin = 0 dB`, після чого вираховується відстань `d_max`:
  ```
  FSPL_max = EIRP - L_atm - L_fade - L_misc + G_RX - L_rx - P_sens
  d_max = 10 ^ ( (FSPL_max - 20·log10(f_MHz) - 32.44) / 20 )
  ```

---

## Реалізація на C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Структури конфігурації радіолінії */
typedef struct {
    double pwr_tx_dbm;      /* Потужність передавача (dBm) */
    double loss_tx_db;      /* Втрати у кабелі TX (dB) */
    double gain_tx_dbi;     /* Підсилення антени TX (dBi) */
} tx_config_t;

typedef struct {
    double freq_mhz;        /* Несуча частота (МГц) */
    double distance_km;     /* Відстань між антенами (км) */
    double loss_atm_db;     /* Атмосферні втрати (dB) */
    double loss_fade_db;    /* Запас на завмирання (dB) */
    double loss_misc_db;    /* Додаткові втрати (dB) */
} channel_config_t;

typedef struct {
    double gain_rx_dbi;     /* Підсилення антени RX (dBi) */
    double loss_rx_db;      /* Втрати у кабелі RX (dB) */
    double bandwidth_hz;    /* Смуга частот приймача (Гц) */
    double noise_figure_db; /* Коефіцієнт шуму N_F (dB) */
    double snr_min_db;      /* Поріг демодуляції SNR (dB) */
} rx_config_t;

typedef struct {
    double eirp_dbm;        /* EIRP = P_TX - L_tx + G_TX */
    double fspl_db;        /* Втрати у вільному просторі */
    double loss_path_total;/* Загальні втрати траси */
    double pwr_rx_dbm;     /* Потужність на вході RX */
    double sensitivity_dbm;/* Поріг чутливості RX */
    double margin_db;      /* Запас радіолінії (Margin) */
    double max_distance_km;/* Максимальна відстань при Margin=0 */
    bool is_link_viable;   /* Ознака успішності зв'язку (Margin >= 0) */
} link_budget_result_t;

/* Обчислення бюджету лінії */
link_budget_result_t calculate_link_budget(const tx_config_t *tx,
                                           const channel_config_t *channel,
                                           const rx_config_t *rx) {
    link_budget_result_t res;

    /* 1. Розрахунок EIRP */
    res.eirp_dbm = tx->pwr_tx_dbm - tx->loss_tx_db + tx->gain_tx_dbi;

    /* 2. Розрахунок FSPL у dB: 20*log10(d_km) + 20*log10(f_MHz) + 32.44 */
    res.fspl_db = 20.0 * log10(channel->distance_km) + 
                  20.0 * log10(channel->freq_mhz) + 32.44;

    /* 3. Загальні втрати траси */
    res.loss_path_total = res.fspl_db + channel->loss_atm_db + 
                          channel->loss_fade_db + channel->loss_misc_db;

    /* 4. Потужність сигналу на вхідному роз'ємі приймача */
    res.pwr_rx_dbm = res.eirp_dbm - res.loss_path_total + rx->gain_rx_dbi - rx->loss_rx_db;

    /* 5. Обчислення порогу чутливості: P_sens = -174 + 10*log10(B) + N_F + SNR_min */
    double thermal_noise_dbm = -173.98 + 10.0 * log10(rx->bandwidth_hz);
    res.sensitivity_dbm = thermal_noise_dbm + rx->noise_figure_db + rx->snr_min_db;

    /* 6. Запас радіолінії (Link Margin) */
    res.margin_db = res.pwr_rx_dbm - res.sensitivity_dbm;
    res.is_link_viable = (res.margin_db >= 0.0);

    /* 7. Максимально припустимі втрати FSPL_max при Margin = 0 */
    double fspl_max_db = res.eirp_dbm - channel->loss_atm_db - channel->loss_fade_db 
                         - channel->loss_misc_db + rx->gain_rx_dbi - rx->loss_rx_db 
                         - res.sensitivity_dbm;

    /* d_max = 10 ^ ( (FSPL_max - 20*log10(f_MHz) - 32.44) / 20 ) */
    double exp_val = (fspl_max_db - 20.0 * log10(channel->freq_mhz) - 32.44) / 20.0;
    res.max_distance_km = pow(10.0, exp_val);

    return res;
}

int main(void) {
    /* Налаштування сценарію: 868 МГц LoRa лінк на 10 км */
    tx_config_t tx = { .pwr_tx_dbm = 14.0, .loss_tx_db = 1.0, .gain_tx_dbi = 2.15 };
    channel_config_t ch = { 
        .freq_mhz = 868.0, 
        .distance_km = 10.0, 
        .loss_atm_db = 0.5, 
        .loss_fade_db = 10.0, 
        .loss_misc_db = 1.5 
    };
    rx_config_t rx = { 
        .gain_rx_dbi = 2.15, 
        .loss_rx_db = 1.0, 
        .bandwidth_hz = 125000.0, /* 125 кГц */
        .noise_figure_db = 6.0, 
        .snr_min_db = -10.0       /* CSS розширення спектра */
    };

    link_budget_result_t res = calculate_link_budget(&tx, &ch, &rx);

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ БЮДЖЕТУ ЛІНІЇ ===\n");
    printf("EIRP передавача:       %+.2f dBm\n", res.eirp_dbm);
    printf("Втрати простору FSPL:   %.2f dB\n", res.fspl_db);
    printf("Загальні втрати траси:  %.2f dB\n", res.loss_path_total);
    printf("Прийнята потужність:   %+.2f dBm\n", res.pwr_rx_dbm);
    printf("Поріг чутливості RX:   %+.2f dBm\n", res.sensitivity_dbm);
    printf("Запас лінії (Margin):   %+.2f dB [%s]\n", 
           res.margin_db, res.is_link_viable ? "ПРАЦЮЄ" : "ПОМИЛКА СИГНАЛУ");
    printf("Максимальна дальність:  %.2f км\n", res.max_distance_km);

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <iomanip>
#include <string_view>
#include <expected>

namespace rf {

struct TxConfig {
    double power_dbm{14.0};       // Вихідна потужність (dBm)
    double cable_loss_db{1.0};    // Втрати кабелю (dB)
    double antenna_gain_dbi{2.15};// Підсилення антени (dBi)

    [[nodiscard]] constexpr double eirp() const noexcept {
        return power_dbm - cable_loss_db + antenna_gain_dbi;
    }
};

struct ChannelConfig {
    double frequency_mhz{868.0};  // Несуча частота (МГц)
    double distance_km{10.0};     // Відстань між вузлами (км)
    double atm_loss_db{0.5};      // Поглинання атмосферою (dB)
    double fade_margin_db{10.0};  // Запас на завмирання (dB)
    double misc_loss_db{1.5};     // Додаткові втрати (dB)

    [[nodiscard]] double fspl() const noexcept {
        return 20.0 * std::log10(distance_km) + 20.0 * std::log10(frequency_mhz) + 32.44;
    }

    [[nodiscard]] double total_path_loss() const noexcept {
        return fspl() + atm_loss_db + fade_margin_db + misc_loss_db;
    }
};

struct RxConfig {
    double antenna_gain_dbi{2.15};// Підсилення антени (dBi)
    double cable_loss_db{1.0};    // Втрати кабелю (dB)
    double bandwidth_hz{125000.0};// Смуга частот (Гц)
    double noise_figure_db{6.0};  // Коефіцієнт шуму (dB)
    double snr_min_db{-10.0};     // Поріг демодуляції (dB)

    [[nodiscard]] double thermal_noise_floor() const noexcept {
        return -173.98 + 10.0 * std::log10(bandwidth_hz);
    }

    [[nodiscard]] double sensitivity() const noexcept {
        return thermal_noise_floor() + noise_figure_db + snr_min_db;
    }
};

struct LinkResult {
    double eirp_dbm;
    double fspl_db;
    double path_loss_total_db;
    double rx_power_dbm;
    double sensitivity_dbm;
    double margin_db;
    double max_distance_km;
    bool is_viable;
};

enum class LinkError {
    InvalidFrequency,
    InvalidDistance,
    InvalidBandwidth
};

[[nodiscard]] std::expected<LinkResult, LinkError> 
calculate_budget(const TxConfig& tx, const ChannelConfig& ch, const RxConfig& rx) noexcept {
    if (ch.frequency_mhz <= 0.0) return std::unexpected(LinkError::InvalidFrequency);
    if (ch.distance_km <= 0.0)  return std::unexpected(LinkError::InvalidDistance);
    if (rx.bandwidth_hz <= 0.0) return std::unexpected(LinkError::InvalidBandwidth);

    LinkResult res;
    res.eirp_dbm = tx.eirp();
    res.fspl_db = ch.fspl();
    res.path_loss_total_db = ch.total_path_loss();
    res.rx_power_dbm = res.eirp_dbm - res.path_loss_total_db + rx.antenna_gain_dbi - rx.cable_loss_db;
    res.sensitivity_dbm = rx.sensitivity();
    res.margin_db = res.rx_power_dbm - res.sensitivity_dbm;
    res.is_viable = (res.margin_db >= 0.0);

    double fspl_max_db = res.eirp_dbm - ch.atm_loss_db - ch.fade_margin_db 
                         - ch.misc_loss_db + rx.antenna_gain_dbi - rx.cable_loss_db 
                         - res.sensitivity_dbm;

    double exp_val = (fspl_max_db - 20.0 * std::log10(ch.frequency_mhz) - 32.44) / 20.0;
    res.max_distance_km = std::pow(10.0, exp_val);

    return res;
}

} // namespace rf

int main() {
    rf::TxConfig tx{.power_dbm = 14.0, .cable_loss_db = 1.0, .antenna_gain_dbi = 2.15};
    rf::ChannelConfig ch{.frequency_mhz = 868.0, .distance_km = 10.0, .fade_margin_db = 10.0};
    rf::RxConfig rx{.bandwidth_hz = 125000.0, .snr_min_db = -10.0};

    auto budget_opt = rf::calculate_budget(tx, ch, rx);
    if (!budget_opt) {
        std::cerr << "Некоректні вхідні параметри радіолінії!\n";
        return 1;
    }

    const auto& res = budget_opt.value();

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ОБЧИСЛЕННЯ БЮДЖЕТУ РАДІОЛІНІЇ (C++23) ===\n";
    std::cout << "EIRP:                  " << std::showpos << res.eirp_dbm << " dBm\n";
    std::cout << "Втрати простору FSPL:  " << std::noshowpos << res.fspl_db << " dB\n";
    std::cout << "Прийнята потужність:  " << std::showpos << res.rx_power_dbm << " dBm\n";
    std::cout << "Поріг чутливості:      " << std::showpos << res.sensitivity_dbm << " dBm\n";
    std::cout << "Запас лінії (Margin):  " << std::showpos << res.margin_db << " dB "
              << (res.is_viable ? "[OK]" : "[FAIL]") << "\n";
    std::cout << "Гранична дальність:    " << std::noshowpos << res.max_distance_km << " км\n";

    return 0;
}
```
:::

---

## Детальний розбір логіки та апаратних зв'язків

### 1. Покрокове розгортання математичного алгоритму
У коді реалізовано детермінований послідовний алгоритм обчислень:
- Спочатку обчислюється величина `EIRP`, яка визначає сумарний енергетичний потенціал передавального вузла.
- Далі функція розраховує фундаментальне геометричне згасання хвилі у вільному просторі `FSPL` за логарифмічною формулою Фрііса. Завдяки використанню коефіцієнта `32.44` доданок `20*log10(f)` приймає частоту у мегагерцах, а `20*log10(d)` — відстань у кілометрах.
- Потім вираховується підсумкова потужність сигналу `P_RX`, яка потрапляє у демодулятор після проходження усіх згашувачів та підсилення приймальної антени.
- Незалежно від потужності передавача обчислюється фізичний поріг чутливості `P_sens`. Він базується на фундаментальній константі теплового шуму `-173.98 dBm/Hz` при еталонній температурі 290 К.
- Різниця між `P_RX` та `P_sens` дає підсумковий запас лінії `margin_db`. Якщо `margin_db >= 0`, прапор `is_link_viable` встановлюється в `true`.
- Нарешті, зворотне розв'язання логарифмічного рівняння дозволяє виразити граничну відстань `max_distance_km`, при якій `margin_db` знизиться рівно до 0 dB.

### 2. Алгоритм автоматичної адаптації вихідної потужності (Adaptive Power Control)
У бездротових сенсорних мережах (LoRaWAN, Zigbee, Thread) обчислювальне ядро лінк-бюджету використовується в зворотній петлі зв'язку для адаптивного регулювання вихідної потужності передавача `P_TX`:

У разі регулярного прийому пакетів із високим значенням `Margin > 15 dB` базовий контролер надсилає команду розширення ADR на зниження потужності. Це не лише знижує енергоспоживання вузла, але й запобігає перенасиченню вхідного каскаду (LNA) розташованих поруч приймачів.

### 3. Інтеграція з реальним апаратним забезпеченням (Semtech SX1276 / SX1262)
У практичних вбудованих розробках розрахований запас радіолінії постійно порівнюють із телеметричними регістрами реального радіотрансивера.

Наприклад, популярні чипи Semtech SX1276 та SX1262 повертають після прийому кожного пакету два значення з внутрішніх регістрів:
1. `RegPktRssiValue` — виміряну індикаторну потужність прийому (RSSI, у dBm).
2. `RegPktSnrValue` — виміряне відношення сигнал/шум прийнятого пакету (SNR, у dB).

#### Алгоритм порівняння теорії з експериментом:

:::tabs
```c
/* Приклад зчитування регістрів з трансивера Semtech SX1276 (C) */
int8_t raw_snr = read_spi_register(REG_PKT_SNR_VALUE);
int16_t raw_rssi = read_spi_register(REG_PKT_RSSI_VALUE);

/* Перерахунок SNR: регістр зберігає знакову величину у чвертях дБ */
float measured_snr_db = (float)raw_snr / 4.0f;

/* Перерахунок RSSI у dBm (для частот High-Band > 779 МГц) */
float measured_rssi_dbm = -157.0f + (float)raw_rssi;

/* Якщо SNR < 0, корекція RSSI за рекомендацією виробника (Semtech Datasheet) */
if (measured_snr_db < 0.0f) {
    measured_rssi_dbm += measured_snr_db;
}

/* Розрахунок фактичного запасу лінії на основі реального SNR */
float measured_margin_db = measured_snr_db - required_snr_min_db;
```
```cpp
// Приклад зчитування регістрів з трансивера Semtech SX1276 (C++23)
struct TelemetryPacket {
    float measured_snr_db;
    float measured_rssi_dbm;
    float measured_margin_db;
};

[[nodiscard]] inline TelemetryPacket 
decode_sx1276_telemetry(int8_t raw_snr, int16_t raw_rssi, float required_snr_min_db) noexcept {
    float snr = static_cast<float>(raw_snr) * 0.25f;
    float rssi = -157.0f + static_cast<float>(raw_rssi);
    if (snr < 0.0f) {
        rssi += snr;
    }
    return TelemetryPacket{
        .measured_snr_db = snr,
        .measured_rssi_dbm = rssi,
        .measured_margin_db = snr - required_snr_min_db
    };
}
```
:::

Якщо теоретично розрахований `P_RX` становить `-85 dBm`, а виміряний `measured_rssi_dbm` показує `-102 dBm`, інженер негайно бачить наявність **додаткових втрат у 17 дБ**, яких не було враховано у теоретичному розрахунку. Це свідчить про наявність розстроювання антени, деградації кабелю або перекриття зони Френеля.

---

## Методика польової верифікації та аудиту радіоканалу

При аудиті новозбудованої радіолінії розробники виконують покрокову процедуру польової перевірки бюджету:

1. **Еталонний вимір потужності передавача:** Вихідну потужність `P_TX` перевіряють за допомогою спектроаналізатора або ваттметра (наприклад, Bird 43) із підключеним атенюатором `-30 dB`. Записують реальне значення потужності у dBm.
2. **Вимір втрат фідерної лінії:** Кабель перевіряють за допомогою векторного аналізатора кіл (VNA) на параметри зворотних втрат `S11` (КСХН) та втрат на проходження `S21`. Втрати понад 1.5 дБ на метр на частоті 2.4 ГГц свідчать про брак або потрапляння вологи у роз'єм.
3. **Вимір спектрального шуму ефіру:** Приймач переводять у режим вимірювання завад при вимкненому передавачі. Якщо виміряний поріг шумів `N_measured` вищий за розрахований `N_th = -174 + 10·log10(B) + N_F` більше ніж на 6 дБ, у зоні роботи присутнє стороннє промислове джерело завад (імпульсні джерела живлення, сонячні інвертори).
4. **Порівняльний аудит запасу сигналу:** Виміряний рівень `RSSI` порівнюють із розрахованим `P_RX`. Відхилення у межах `±2 dB` вважається ідеальним збігом теорії та експерименту.

---

## Розрахунок втрат на друкованій платі (PCB Trace Loss)

У сучасних мобільних пристроях радіомодуль монтується безпосередньо на друковану плату (PCB), а фідерною лінією служить мікросмужкова або копланарна лінія передачі.

Згасання сигналу в мікросмужковій лінії складається з двох факторів:
1. **Омічні втрати в мідному провіднику (`L_cond`):** Спричинені поверхневим ефектом (Skin Effect), через який струм високої частоти протікає лише у тонкому поверхневому шарі міді завтовшки близько 1.3 мікрона на частоті 2.4 ГГц.
2. **Діелектричні втрати у матеріалі підкладки (`L_dielectric`):** Обчислюються через тангенс кута діелектричних втрат (`tan δ`). Для стандартного дешевого склотекстоліту FR-4 (`tan δ ≈ 0.02`) втрати на частоті 2.4 ГГц становлять до `0.15 dB/см`.

Якщо довжина мікросмужкової лінії від трансивера до антени становить 10 см, втрати на друкованій платі викривлять лінк-бюджет додатковими `1.5 dB`. Для високочастотних плат (5.8–24 ГГц) замість FR-4 застосовують спеціальні НВЧ-ламінати (Rogers RO4003C, Taconic) із `tan δ < 0.002`, що знижує втрати на платі у 10 разів.

---

## Вплив температурних режимів (від -40°C до +85°C) на бюджет лінії

Електронні компоненти передавача та приймача змінюють свої параметри при коливанні температури навколишнього середовища:

- **Підсилювач потужності (PA):** Зі зростанням температури від +25°C до +85°C коефіцієнт підсилення напівпровідникового транзистора падає, що викликає зниження вихідної потужності `P_TX` на `1.0 ... 1.8 dB`.
- **Малошумний підсилювач (LNA):** При нагріванні зростає швидкість теплового руху електронів, що призводить до збільшення власного коефіцієнта шуму `N_F` на `0.5 ... 1.2 dB`.
- **Спектральний шум:** Фундаментальна шумова підлога `N_0 = k_B · T` при +85°C (358 K) зростає від `-173.98 dBm/Hz` до `-173.07 dBm/Hz` (на `0.91 dB`).

Сумарно в спеку (+85°C) підсумковий запас лінії `Margin` зменшується приблизно на `3.5 dB`. Інженер зобов'язаний закладати цей температурний зсув у підсумковий лінк-бюджет промислових та авіаційних систем.

---

## Пастки реальної розробки та крайові випадки

1. **Неправильні одиниці вимірювання в логарифмах:** Найпоширеніша помилка — додавання коефіцієнта підсилення в дБ до лінійних Ватт. Завжди перевіряйте, що додавання виконується виключно в однакових логарифмічних одиницях (dBm з dB, або dBW з dB).
2. **Ігнорування температурного фактора `T`:** При зміні температури від `290 K` до `350 K` (наприклад, приймач у металевому боксі під прямим сонцем) рівень теплового шуму зростає на `10 · log10(350/290) = +0.82 dB`. Якщо лінія розрахована «впритул» із малим запасом, зв'язок пропаде саме вдень при нагріванні.
3. **Нехтування втратами поляризації:** Якщо одна антена орієнтована вертикально, а інша відхилилася на 45 градусів через вітер, додаткові втрати у лінк-бюджеті становитимуть `3 dB` (`10·log10(cos²(45°))`). При ортогональній поляризації (90 градусів) втрати перевищують `20–30 dB`.
4. **Обчислювальні помилки переповнення або втрати точності:** При використанні 32-бітної арифметики з плаваючою комою на мікроконтролерах без FPU (ARM Cortex-M0/M3) обчислення `10^(x/20)` вимагає виклику бібліотечної функції `powf()`. Якщо вхідне значення степеня стає надто великим (наприклад, `> 38`), виникає переповнення `float`. Завжди перевіряйте межі вхідних втрат перед викликом подібних функцій.
5. **Фіксована кратна арифметика для 8-бітних МК (AVR/PIC):** На слабких 8-бітних процесорах обчислення `log10()` та `pow()` забирає тисячі тактів. У таких системах використовують цілочисельну табличну апроксимацію (Look-Up Table, LUT) для логарифмів із фіксованою комою (Fixed-point 16.16), що прискорює розрахунок бюджету у 50 разів.
