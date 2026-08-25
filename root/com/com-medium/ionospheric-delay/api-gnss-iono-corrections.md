# 📋 Інтерфейс і структури даних GNSS-поправок іоносфери

Цей довідник описує специфікації програмувальних інтерфейсів, бітові структури даних, системи одиниць вимірювання, масштабування та діапазони допустимих значень параметрів іоносферних поправок, що транслюються супутниковими навігаційними угрупованнями (GPS Klobuchar, Galileo NeQuick-G, SBAS) та передаються у глобальних сіткових форматах IONEX.

Довідник призначений для розробників навігаційного програмного забезпечення, прошивок GNSS-приймачів, бібліотек первинної обробки сигналів (DSP) та систем високоточного позиціонування (RTK/PPP).

### 1. GPS Klobuchar Broadcast Interface (IS-GPS-200)

Параметри моделі Клобучара передаються у 4-му підкадрі (Subframe 4, Page 18) основного навігаційного кадру GPS L1 C/A. Цей набір містить 8 масштабованих коефіцієнтів: 4 альфа-коефіцієнти для обчислення амплітуди добової косинусоїди та 4 бета-коефіцієнти для обчислення її періоду. Параметри оновлюються наземним сегментом управління GPS приблизно один раз на добу, проте зберігають працездатність протягом 14 днів у разі втрати зв'язку з наземними станціями.

При декодуванні сирого бітового потоку навігаційного кадру 8-бітові цілочисельні значення зі знаком (у формі доповнення до двійки) помножуються на відповідний масштабний множник LSB (Least Significant Bit) для отримання плаваючих значень у міжнародній системі одиниць СІ.

#### Механізм масштабування бітів кадру GPS

Декодування бінарного поля `α_i_raw` або `β_i_raw` у фізичне значення виконується за точними бітовими зсувами. Альфа-коефіцієнти задають амплітуду затримки у секундах та степенях геомагнітної широти. Бета-коефіцієнти задають період косинусоїди у секундах та степенях геомагнітної широти.

- `α₀`: 8 біт зі знаком, LSB = `2⁻³⁰` с. Фізична значення дорівнює `α₀_raw · 2⁻³⁰`.
- `α₁`: 8 біт зі знаком, LSB = `2⁻²⁷` с/напівколо. Фізична значення дорівнює `α₁_raw · 2⁻²⁷`.
- `α₂`: 8 біт зі знаком, LSB = `2⁻²⁴` с/напівколо². Фізична значення дорівнює `α₂_raw · 2⁻²⁴`.
- `α₃`: 8 біт зі знаком, LSB = `2⁻²⁴` с/напівколо³. Фізична значення дорівнює `α₃_raw · 2⁻²⁴`.
- `β₀`: 8 біт зі знаком, LSB = `2¹¹` с. Фізична значення дорівнює `β₀_raw · 2¹¹`.
- `β₁`: 8 біт зі знаком, LSB = `2¹⁴` с/напівколо. Фізична значення дорівнює `β₁_raw · 2¹⁴`.
- `β₂`: 8 біт зі знаком, LSB = `2¹⁶` с/напівколо². Фізична значення дорівнює `β₂_raw · 2¹⁶`.
- `β₃`: 8 біт зі знаком, LSB = `2¹⁶` с/напівколо³. Фізична значення дорівнює `β₃_raw · 2¹⁶`.

#### Таблиця параметрів супутникового кадру GPS Klobuchar

| Параметр | Опис | Кількість біт | Масштабний множник (LSB) | Одиниці вимірювання | Допустимий діапазон |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `α₀` | Нульовий коефіцієнт амплітуди | 8 (доповн. 2) | `2⁻³⁰` | секунди | `-1.19e-07 .. +1.18e-07` |
| `α₁` | Перший коефіцієнт амплітуди | 8 (доповн. 2) | `2⁻²⁷` | с / напівколо | `-9.54e-07 .. +9.47e-07` |
| `α₂` | Другий коефіцієнт амплітуди | 8 (доповн. 2) | `2⁻²⁴` | с / напівколо² | `-7.63e-06 .. +7.57e-06` |
| `α₃` | Третій коефіцієнт амплітуди | 8 (доповн. 2) | `2⁻²⁴` | с / напівколо³ | `-6.10e-05 .. +6.05e-05` |
| `β₀` | Нульовий коефіцієнт періоду | 8 (доповн. 2) | `2¹¹` | секунди | `0 .. 522240` |
| `β₁` | Перший коефіцієнт періоду | 8 (доповн. 2) | `2¹⁴` | с / напівколо | `-4.18e+06 .. +4.16e+06` |
| `β₂` | Другий коефіцієнт періоду | 8 (доповн. 2) | `2¹⁶` | с / напівколо² | `-3.35e+07 .. +3.33e+07` |
| `β₃` | Третій коефіцієнт періоду | 8 (доповн. 2) | `2¹⁶` | с / напівколо³ | `-2.68e+08 .. +2.66e+08` |

Зазначені одиниці вимірювання використовують кутові одиниці **напівкола (semi-circles)**, де 1 напівколо дорівнює `π` радіанів або `180` градусів. Використання напівкіл замість радіанів спрощує арифметику мобільних процесорів, оскільки нормована широта `φ / 180°` напряму потрапляє в діапазон `[-1.0, +1.0]`.

#### Заголовочні структури даних у коді C та C++

У програмуванні приймачів бінарний потік даних із демодулятора спочатку розпаковується у бітові поля сирої структури, після чого декодувальний модуль масштабує біти у плаваючі величини та перевіряє їх на відповідність діапазонам специфікації IS-GPS-200.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#pragma pack(push, 1)
/* Сирий бінарний пакет Subframe 4 Page 18 (упакований) */
typedef struct {
    int8_t  alpha0_raw; /* LSB = 2^-30 s */
    int8_t  alpha1_raw; /* LSB = 2^-27 s/semi-circle */
    int8_t  alpha2_raw; /* LSB = 2^-24 s/semi-circle^2 */
    int8_t  alpha3_raw; /* LSB = 2^-24 s/semi-circle^3 */
    int8_t  beta0_raw;  /* LSB = 2^11 s */
    int8_t  beta1_raw;  /* LSB = 2^14 s/semi-circle */
    int8_t  beta2_raw;  /* LSB = 2^16 s/semi-circle^2 */
    int8_t  beta3_raw;  /* LSB = 2^16 s/semi-circle^3 */
} gps_klobuchar_raw_t;
#pragma pack(pop)

/* Декодовані фізичні параметри у міжнародних одиницях */
typedef struct {
    double alpha[4];    /* Альфа-коефіцієнти амплітуди (с, с/напівколо, ...) */
    double beta[4];     /* Бета-коефіцієнти періоду (с, с/напівколо, ...) */
    uint32_t tow_sec;   /* Час тижня GPS (Time of Week) */
    bool   is_valid;    /* Прапорець цілісності й коректності декодування */
} gps_klobuchar_decoded_t;

/**
 * Декодує сирі біти супутникового кадру GPS у фізичні параметри Klobuchar.
 */
static inline void gps_klobuchar_decode(const gps_klobuchar_raw_t* raw, uint32_t tow, gps_klobuchar_decoded_t* out) {
    out->alpha[0] = raw->alpha0_raw * pow(2.0, -30);
    out->alpha[1] = raw->alpha1_raw * pow(2.0, -27);
    out->alpha[2] = raw->alpha2_raw * pow(2.0, -24);
    out->alpha[3] = raw->alpha3_raw * pow(2.0, -24);

    out->beta[0]  = raw->beta0_raw  * pow(2.0, 11);
    out->beta[1]  = raw->beta1_raw  * pow(2.0, 14);
    out->beta[2]  = raw->beta2_raw  * pow(2.0, 16);
    out->beta[3]  = raw->beta3_raw  * pow(2.0, 16);

    out->tow_sec  = tow;
    out->is_valid = true;
}
```
```cpp
#include <array>
#include <cstdint>
#include <cmath>
#include <optional>

namespace gnss::api {

/* Зпакована сира бітова структура кадру IS-GPS-200 */
struct alignas(1) GpsKlobucharRaw {
    std::int8_t alpha0_raw;
    std::int8_t alpha1_raw;
    std::int8_t alpha2_raw;
    std::int8_t alpha3_raw;
    std::int8_t beta0_raw;
    std::int8_t beta1_raw;
    std::int8_t beta2_raw;
    std::int8_t beta3_raw;
};

/* Ідіоматична структура C++ з вбудованою валидацією */
struct GpsKlobucharBroadcast {
    std::array<double, 4> alpha{};
    std::array<double, 4> beta{};
    std::uint32_t         tow_sec{0};
    bool                  valid{false};

    [[nodiscard]] static constexpr GpsKlobucharBroadcast decode(const GpsKlobucharRaw& raw, std::uint32_t tow) noexcept {
        GpsKlobucharBroadcast decoded{};
        decoded.alpha[0] = raw.alpha0_raw * std::pow(2.0, -30);
        decoded.alpha[1] = raw.alpha1_raw * std::pow(2.0, -27);
        decoded.alpha[2] = raw.alpha2_raw * std::pow(2.0, -24);
        decoded.alpha[3] = raw.alpha3_raw * std::pow(2.0, -24);

        decoded.beta[0]  = raw.beta0_raw  * std::pow(2.0, 11);
        decoded.beta[1]  = raw.beta1_raw  * std::pow(2.0, 14);
        decoded.beta[2]  = raw.beta2_raw  * std::pow(2.0, 16);
        decoded.beta[3]  = raw.beta3_raw  * std::pow(2.0, 16);

        decoded.tow_sec  = tow;
        decoded.valid    = decoded.checkBounds();
        return decoded;
    }

    [[nodiscard]] constexpr bool checkBounds() const noexcept {
        for (double a : alpha) {
            if (std::isnan(a)) return false;
        }
        for (double b : beta) {
            if (std::isnan(b)) return false;
        }
        return true;
    }
};

} // namespace gnss::api
```
:::

### 2. Galileo NeQuick-G Broadcast Interface (Galileo OS SIS ICD)

Європейська супутникова система Galileo використовує тривимірну адаптивну модель іоносфери **NeQuick-G**. Замість 8 коефіцієнтів часової косинусоїди, як у GPS, супутники Galileo транслюють у складі повідомлення I/NAV (на відкритій частоті E1-B) лише 3 параметри ефективного сонячного потоку `a_z0, a_z1, a_z2` (Broadcast Ionospheric Coefficients), а також 5 біт регіональних прапорців активності (Ionospheric Region Flags).

Параметри `a_z` описують залежність ефективного сонячного потоку `A_z` (вимірюється в одиницях сонячного випромінювання SFU, Solar Flux Units, `1 SFU = 10⁻²² Вт/(м²·Гц)`) від модифікованої дипольної широти MODIP `μ`:

```
A_z = a_z0 + a_z1 · μ + a_z2 · μ²
```

Модифікована дипольна широта MODIP `μ` є геомагнітною величиною, що задовольняє співвідношенню `tan(μ) = I / √(cos(φ))`, де `I` — магнітне нахилення, а `φ` — географічна широта. Використання широти MODIP дозволяє моделі NeQuick-G враховувати екваторіальну іоносферну аномалію (EIA) з двома симетричними максимумами електронної густини по обидва боки від геомагнітного екватора.

#### Таблиця параметрів супутникового кадру Galileo NeQuick-G

| Параметр | Опис | Кількість біт | Масштабний множник (LSB) | Одиниці вимірювання | Диапазон |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `a_z0` | Постійний коефіцієнт сонячного потоку | 11 (без знаку) | `2⁻² = 0.25` | SFU | `0.0 .. 511.75` |
| `a_z1` | Лінійний коефіцієнт за широтою MODIP | 11 (доповн. 2) | `2⁻⁸ = 0.00390625` | SFU / градус | `-4.0 .. +4.0` |
| `a_z2` | Квадратичний коефіцієнт за широтою MODIP | 14 (доповн. 2) | `2⁻¹⁵ = 0.000030517578125` | SFU / градус² | `-0.25 .. +0.25` |
| `Region Flags` | Прапорці штормової активності іоносферних регіонів | 5 (бітове поле) | 1 | бітова маска | `0 .. 31` |

Регіональні прапорці `Region Flags` вказують, для яких саме географічних зон Землі поточні коефіцієнти були оптимізовані наземним сегментом Galileo. Якщо біт відповідного регіону скинутий у `0`, приймач використовує стандартний розрахунок; якщо біт встановлений у `1`, це сигналізує про підвищену іоносферну або геомагнітну активність у цьому регіоні.

#### Структури даних Galileo NeQuick-G у коді C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    double a_z0;            /* Ефективне значення сонячного потоку Az (SFU) */
    double a_z1;            /* Лінійний коефіцієнт за широтою MODIP */
    double a_z2;            /* Квадратичний коефіцієнт за широтою MODIP */
    uint8_t region_flags;   /* 5 біт регіональних прапорців іоносферного шторму */
    uint32_t issue_of_data; /* Ідентифікатор версії даних IODN (Issue of Data) */
    bool is_valid;
} galileo_nequick_broadcast_t;

/**
 * Ініціалізує структуру NeQuick-G за замовчуванням при відсутності супутникових поправок.
 */
static inline void galileo_nequick_set_default(galileo_nequick_broadcast_t* params) {
    params->a_z0 = 63.7;  /* Середнє значення сонячного потоку у спокійний період */
    params->a_z1 = 0.0;
    params->a_z2 = 0.0;
    params->region_flags = 0;
    params->issue_of_data = 0;
    params->is_valid = false;
}
```
```cpp
#include <cstdint>
#include <optional>

namespace gnss::api {

struct GalileoNeQuickBroadcast {
    double        a_z0{63.7};
    double        a_z1{0.0};
    double        a_z2{0.0};
    std::uint8_t  region_flags{0};
    std::uint32_t issue_of_data{0};
    bool          valid{false};

    [[nodiscard]] constexpr double calculateAz(double modip_deg) const noexcept {
        return a_z0 + a_z1 * modip_deg + a_z2 * modip_deg * modip_deg;
    }
};

} // namespace gnss::api
```
:::

### 3. SBAS Ionospheric Grid Point Interface (ICAO Annex 10 / RTCA DO-229)

Авіаційні системи диференціальної корекції SBAS (WAAS у Північній Америці, EGNOS у Європі, SDCM у Східній Європі, MSAS у Японії) передають іоносферні поправки високої точності через геостаціонарні супутники у спеціальних кадрах Message Type 26 (MT26).

Замість глобальних формульних моделей, SBAS передає масив вертикальних іоносферних затримок безпосередньо у фіксованих вузлах географічної сітки **IGP (Ionospheric Grid Points)** на висоті `h_m = 350 км`. Наземна мережа опорних станцій у режимі реального часу вимірює стан плазми та транслює вертикальну затримку й індекс невизначеності для кожного вузла сітки.

Приймач визначає пробійну точку IPP для кожного супутника, знаходить 4 оточуючих вузли сітки IGP і виконує двовимірну білінійну або трикутну інтерполяцію вертикальної затримки `VTEC_IPP`, після чого множить її на похилий картографічний фактор `F(e)`.

#### Специфікація вузла сітки IGP у повідомленні MT26

| Поле | Кількість біт | Масштаб (LSB) | Одиниці | Значення спеціальних кодів |
| :--- | :--- | :--- | :--- | :--- |
| `IGP Vertical Delay` | 9 (без знаку) | `0.125` | метри | `0 .. 63.75 м` (`511` = «Вузол не контролюється») |
| `GIVEI` | 4 (без знаку) | 1 (індекс) | індекс СКО | `0..14` (індекс помилки), `15` = «Небезпечно для використання» |

Індекс **GIVEI (Grid Ionospheric Vertical Error Index)** визначає верхню межу середньоквадратичного відхилення помилки (99.9% довірчий інтервал цілісності), що є критично важливим для авіаційних систем посадки літаків за стандартами ICAO.

#### Таблиця декодування індексу GIVEI у СКО вертикальної помилки (σ_GIVE)

| GIVEI індекс | СКО вертикальної помилки σ_GIVE (м) | Інтервал довірчості цілісності (99.9%) |
| :--- | :--- | :--- |
| `0` | `0.05 м` | `0.3 м` |
| `1` | `0.10 м` | `0.6 м` |
| `2` | `0.15 м` | `0.9 м` |
| `3` | `0.20 м` | `1.2 м` |
| `4` | `0.25 м` | `1.5 м` |
| `5` | `0.30 м` | `1.8 м` |
| `6` | `0.35 м` | `2.1 м` |
| `7` | `0.40 м` | `2.4 м` |
| `8` | `0.50 м` | `3.0 м` |
| `9` | `0.60 м` | `3.6 м` |
| `10` | `0.75 м` | `4.5 м` |
| `11` | `1.00 м` | `6.0 м` |
| `12` | `1.50 м` | `9.0 м` |
| `13` | `2.50 м` | `15.0 м` |
| `14` | `7.50 м` | `45.0 м` |
| `15` | `∞` («Недоступно / Шторм») | «Небезпечно використовувати для навігації» |

#### Структури даних SBAS IGP у коді C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t igp_number;       /* Номер вузла сітки IGP (1..201) */
    double   delay_vertical_m; /* Вертикальна затримка в метрах (0.125 м LSB) */
    uint8_t  givei;            /* Індекс помилки цілісності (0..15) */
    double   sigma_give_m;     /* Декодоване СКО помилки в метрах */
    bool     is_monitored;     /* Прапорець активного моніторингу */
} sbas_igp_point_t;

/* Двовимірна картографічна інтерполяція в осередку IGP */
typedef struct {
    sbas_igp_point_t corners[4]; /* 4 кутові вузли сітки навколо IPP */
    bool is_valid_quad;          /* Чи всі 4 вузли придатні для інтерполяції */
} sbas_igp_cell_t;
```
```cpp
#include <array>
#include <cstdint>

namespace gnss::api {

struct SbasIgpPoint {
    std::uint16_t igp_id{0};
    double        delay_vertical_m{0.0};
    std::uint8_t  givei{15};
    double        sigma_give_m{1e9};
    bool          monitored{false};

    [[nodiscard]] static constexpr double decodeGiveiSigma(std::uint8_t givei) noexcept {
        constexpr std::array<double, 15> give_table{
            0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
            0.50, 0.60, 0.75, 1.00, 1.50, 2.50, 7.50
        };
        if (givei < 15) return give_table[givei];
        return 1e9; /* Поріг непридатності */
    }
};

struct SbasIgpCell {
    std::array<SbasIgpPoint, 4> corners{};

    [[nodiscard]] bool isValidForNavigation() const noexcept {
        for (const auto& pt : corners) {
            if (!pt.monitored || pt.givei >= 15) return false;
        }
        return true;
    }
};

} // namespace gnss::api
```
:::

### 4. Стандартний файл обміну картами іоносфери IONEX (v1.0 / v2.0)

Формат **IONEX (Ionosphere Map Exchange Format)** розроблено Міжнародною службою GNSS (IGS) для стандартизованого обміну двовимірними та тривимірними сітковими картами повного електронного вмісту (VTEC) та RMS-помилок між науковими центрами та геодезичними користувачами.

Файл IONEX є текстовим файлом у кодуванні ASCII зі строгою 80-стовпчиковою текстовою структурою. Він дозволяє зберігати послідовні карти VTEC з часовим інтервалом (наприклад, 1 або 2 години) та географічним кроком (наприклад, 2.5° за широтою та 5.0° за довготою).

При обробці файлів IONEX програмне забезпечення виконує двопросторову інтерполяцію VTEC у просторі між вузлами сітки поточної епохи, а потім часову інтерполяцію між двома сусідніми епохами.

#### Обов'язкові заголовкові записи файлу IONEX

```text
     1.0            IONOSPHERE MAPS     GPS                 IONEX VERSION / TYPE
IGS IONOSPHERE DETERMINATION GROUP                          PGM / RUN BY / DATE 
  2026     8    16    12     0     0                        EPOCH OF FIRST MAP  
  2026     8    16    23    59     0                        EPOCH OF LAST MAP   
  86400                                                     INTERVAL            
     1                                                      # OF MAPS IN FILE   
  NONE                                                      MAPPING FRIEND      
   350.0                                                    HEIGHT HGT          
    87.5  -87.5    2.5                                      LAT1 / LAT2 / DLAT  
  -180.0  180.0    5.0                                      LON1 / LON2 / DLON  
    -1                                                      EXPONENT            
                                                            END OF HEADER       
```

#### Блок даних сітки VTEC у IONEX

```text
     1                                                      START OF TEC MAP    
  2026     8    16    12     0     0                        EPOCH OF CURRENT MAP
    87.5 -180.0 180.0    5.0   350.0                        LAT/LON1/LON2/DLON/H
   120   122   125   128   130   132   135   137   140   142
   145   147   150   152   155   158   160   162   165   168
   ...
                                                            END OF TEC MAP      
```

Значення елемента масиву перераховується у фізичні одиниці **TECU** за допомогою експоненціального множника `EXPONENT`:

```
VTEC_TECU = Value_raw · 10^(EXPONENT)
```

За замовчуванням у файлах IGS `EXPONENT = -1`, отже значення `120` відповідає `120 · 10⁻¹ = 12.0 TECU`.

#### C та C++ структури для парсингу файлів IONEX

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

typedef struct {
    double lat1_deg;     /* Стартова широта (-87.5) */
    double lat2_deg;     /* Кінцева широта (+87.5) */
    double dlat_deg;     /* Крок сітки за широтою (2.5) */
    double lon1_deg;     /* Стартова довгота (-180.0) */
    double lon2_deg;     /* Кінцева довгота (+180.0) */
    double dlon_deg;     /* Крок сітки за довготою (5.0) */
    double height_km;    /* Висота іоносферної оболонки (350.0 км) */
    int32_t exponent;    /* Масштабний експоненційний множник (зазвичай -1) */
} ionex_header_t;

typedef struct {
    uint32_t epoch_seconds;   /* Час епохи карти (Unix timestamp) */
    int16_t* grid_data_raw;   /* Одновимірний масив розміру (n_lat * n_lon) */
    size_t   n_lat;
    size_t   n_lon;
} ionex_map_t;

/**
 * Отримує фізичне значення VTEC у TECU для заданого індексу сітки.
 */
static inline double ionex_get_vtec_tecu(const ionex_map_t* map, int32_t exp_val, size_t i_lat, size_t i_lon) {
    if (i_lat >= map->n_lat || i_lon >= map->n_lon) return 0.0;
    size_t idx = i_lat * map->n_lon + i_lon;
    return (double)map->grid_data_raw[idx] * pow(10.0, exp_val);
}
```
```cpp
#include <vector>
#include <cstdint>
#include <cmath>
#include <cstddef>

namespace gnss::api {

struct IonexHeader {
    double       lat1_deg{-87.5};
    double       lat2_deg{87.5};
    double       dlat_deg{2.5};
    double       lon1_deg{-180.0};
    double       lon2_deg{180.0};
    double       dlon_deg{5.0};
    double       height_km{350.0};
    std::int32_t exponent{-1};
};

class IonexMapGrid {
public:
    IonexMapGrid(std::size_t rows, std::size_t cols, std::int32_t exp_val)
        : num_rows_(rows), num_cols_(cols), exponent_(exp_val), data_(rows * cols, 0) {}

    void setRawValue(std::size_t row, std::size_t col, std::int16_t val) noexcept {
        if (row < num_rows_ && col < num_cols_) {
            data_[row * num_cols_ + col] = val;
        }
    }

    [[nodiscard]] double getVtecTecu(std::size_t row, std::size_t col) const noexcept {
        if (row >= num_rows_ || col >= num_cols_) return 0.0;
        return static_cast<double>(data_[row * num_cols_ + col]) * std::pow(10.0, exponent_);
    }

private:
    std::size_t num_rows_;
    std::size_t num_cols_;
    std::int32_t exponent_;
    std::vector<std::int16_t> data_;
};

} // namespace gnss::api
```
:::

### 5. Обробка помилок та відмова від відповідальності (Error Handling)

При обробці іоносферних поправок у реальному часі навігаційний модуль повинен перевіряти статус даних і генерувати відповідні коди помилок:

| Код помилки | Ідентифікатор | Опис ситуації | Рекомендована дія ПЗ |
| :--- | :--- | :--- | :--- |
| `0` | `IONO_OK` | Поправку розраховано успішно | Використовувати у рівнянні спостережень |
| `-1` | `IONO_ERR_EXPIRED` | Застарілі параметри Klobuchar/NeQuick (>24 год) | Знизити вагу спостереження, видати попередження |
| `-2` | `IONO_ERR_ELEVATION_CUTOFF` | Елевація супутника нижче порогу (<5°) | Відкинути супутник з рішення PVT |
| `-3` | `IONO_ERR_IGP_UNAVAILABLE` | Недостатньо моніторируваних вузлів SBAS | Перейти на базову модель Клобучара |
| `-4` | `IONO_ERR_STORM_UNHEALTHY` | Геомагнітний шторм, GIVEI = 15 | Виключити супутник із засобів контролю цілісності (RAIM) |
