# ⚙️ Програма керування антенним трекером

Програма обчислює кути наведення спрямованої антени в просторі (азимут і кут місця) на основі поточних GPS-координат наземної станції та безпілотного апарата, транслюючи розраховані значення у фізичні імпульси керування сервоприводами або кроковими двигунами. Без автоматичного алгоритму з компенсацією кривини Землі, фільтрацією дрижання та захистом від скручування кабелів утримати вузький радіопромінь (15°–25°) на рухомому борті неможливо.

## Архітектура та математична модель

Керувальний цикл працює як автономна служба (на мікроконтролері STM32/ESP32 або вбудованому Linux-комп'ютері), підключена до потоку телеметрії MAVLink через послідовний порт UART або мережевий сокет UDP (порт за замовчуванням `14550` або `14555`).

Система виконує чотири послідовні задачі в кожному такті (типова частота 10–20 Гц):
1. **Декодування телеметрії**: виділення повідомлення `GLOBAL_POSITION_INT` (ID 33), що містить широту `lat` (в градусах `× 10⁷`), довготу `lon` (в градусах `× 10⁷`) та абсолютну висоту `alt` (в міліметрах над рівнем моря AMSL).
2. **Сферичний геодезичний розрахунок**: визначення ортодромічного азимуту (Bearing) та прямої кутової елевації (Elevation) відносно опорної точки старту (Home Position) за формулами прямої сферичної тригонометрії з урахуванням радіуса Землі `R ≈ 6371000 м`.
3. **Фільтрація та обмеження динаміки**:
   - *Зона нечутливості (Deadband)*: якщо зміна кута менша за 1.5°, приводи залишаються нерухомими, що запобігає постійному високочастотному дрижанню (hunting) та перегріву двигунів.
   - *Обмеження кутової швидкості (Slew Rate Limiter)*: максимальна швидкість повороту обмежується на рівні 45°/с, щоб виключити інерційні удари по редукторах важкої антени при різких маневрах борту.
4. **Генерація сигналів керування**: перетворення кутів у тривалість імпульсів ШІМ (1000–2000 мкс) або крокові імпульси Step/Dir з трапецеїдальним профілем прискорення.

```
+-------------------+      MAVLink UDP/UART     +------------------------+
| Політний контролер| =======================> | MAVLink Parser         |
| (Борт UAV)        |  GLOBAL_POSITION_INT     | (lat, lon, alt)        |
+-------------------+                          +------------------------+
                                                           |
                                                           v
+-------------------+                          +------------------------+
| Базова точка GCS  | -----------------------> | Геодезичний калькулятор|
| (Home lat/lon/alt)|                          | (Azimuth, Elevation)   |
+-------------------+                          +------------------------+
                                                           |
                                                           v
+-------------------+                          +------------------------+
| Сервоприводи      | <----------------------- | Фільтр Deadband & Slew |
| Pan / Tilt        |     ШІМ 1000..2000 мкс   | (Захист від перевантажень)|
+-------------------+                          +------------------------+
```

## Протокол взаємодії та синтаксичний аналіз телеметрії

Контролер підтримує два варіанти прийому телеметрії:
- **Пряме з'єднання UART**: фізичний роз'єм на щоглі, швидкість за замовчуванням 57600 або 115200 бод, 8N1. Використовується при встановленні контролера трекера в одному боксі з радіомодулем телеметрії.
- **Мережевий потік UDP/IP**: прийом MAVLink-пакетів через екрановану кручену пару Ethernet на сокет `0.0.0.0:14555`. Це дозволяє основній програмі GCS (наприклад, QGroundControl) перенаправляти потік телеметрії на IP-адресу трекера без фізичного підключення додаткових кабелів до автопілота.

Синтаксичний автомат розпізнає стартові байти MAVLink 1 (`0xFE`) та MAVLink 2 (`0xFD`), перевіряє довжину корисного навантаження, інкремент лічильника послідовності (`seq`) та обчислює контрольну суму `CRC-16-CCITT` з додаванням специфічного для структури байта насіння (`CRC_EXTRA = 104` для `GLOBAL_POSITION_INT`). Це гарантує, що пошкоджені радіоперешкодами пакети відкидаються до того, як спотворені координати потраплять у математичний калькулятор наведення.

## Реалізація алгоритму на C та C++

Нижче наведено робочу реалізацію контролера антенного трекера двома мовами: модульний C99/C11 (придатний для вбудованих RTOS та мікроконтролерів STM32/ESP32) та ідіоматичний сучасний C++20 (з використанням строгих типів, `std::span`, `std::expected` та RAII для мережевих ресурсів).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define DEG_TO_RAD (3.14159265358979323846 / 180.0)
#define RAD_TO_DEG (180.0 / 3.14159265358979323846)
#define EARTH_RADIUS_M 6371000.0

/* Структура географічних координат */
typedef struct {
    double lat; /* широта в градусах */
    double lon; /* довгота в градусах */
    double alt; /* висота в метрах над рівнем моря */
} GeoCoord;

/* Розраховані кути стеження */
typedef struct {
    double azimuth_deg;   /* 0..360 градусів від True North */
    double elevation_deg; /* 0..90 градусів від горизонту */
    double distance_m;    /* пряма відстань до цілі */
} TrackerAngles;

/* Стан фільтрації та приводів трекера */
typedef struct {
    GeoCoord home;
    bool has_home;
    double current_azimuth;
    double current_elevation;
    double max_slew_rate_deg_s; /* максимальна швидкість град/с */
    double deadband_deg;        /* поріг нечутливості */
} TrackerController;

/* Ініціалізація контролера */
void tracker_init(TrackerController *tc, double max_slew_rate, double deadband) {
    tc->has_home = false;
    tc->current_azimuth = 0.0;
    tc->current_elevation = 0.0;
    tc->max_slew_rate_deg_s = max_slew_rate;
    tc->deadband_deg = deadband;
}

/* Встановлення домашньої позиції наземної станції */
void tracker_set_home(TrackerController *tc, double lat, double lon, double alt) {
    tc->home.lat = lat;
    tc->home.lon = lon;
    tc->home.alt = alt;
    tc->has_home = true;
}

/* Обчислення сферичного азимуту та елевації */
TrackerAngles tracker_calculate(const GeoCoord *home, const GeoCoord *target) {
    TrackerAngles res = {0.0, 0.0, 0.0};

    double phi1 = home->lat * DEG_TO_RAD;
    double phi2 = target->lat * DEG_TO_RAD;
    double delta_phi = (target->lat - home->lat) * DEG_TO_RAD;
    double delta_lambda = (target->lon - home->lon) * DEG_TO_RAD;

    /* Розрахунок ортодромічної горизонтальної відстані (Haversine) */
    double a = sin(delta_phi / 2.0) * sin(delta_phi / 2.0) +
               cos(phi1) * cos(phi2) *
               sin(delta_lambda / 2.0) * sin(delta_lambda / 2.0);
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));
    double ground_distance = EARTH_RADIUS_M * c;

    /* Розрахунок азимуту (Bearing) */
    double y = sin(delta_lambda) * cos(phi2);
    double x = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(delta_lambda);
    double az_rad = atan2(y, x);
    double az_deg = az_rad * RAD_TO_DEG;
    if (az_deg < 0.0) {
        az_deg += 360.0;
    }

    /* Різниця висот з корекцією на кривину Землі */
    double earth_curvature = (ground_distance * ground_distance) / (2.0 * EARTH_RADIUS_M);
    double delta_alt = (target->alt - home->alt) - earth_curvature;

    /* Розрахунок кута елевації */
    double el_rad = atan2(delta_alt, ground_distance);
    double el_deg = el_rad * RAD_TO_DEG;
    if (el_deg < 0.0) el_deg = 0.0;
    if (el_deg > 90.0) el_deg = 90.0;

    res.azimuth_deg = az_deg;
    res.elevation_deg = el_deg;
    res.distance_m = sqrt(ground_distance * ground_distance + delta_alt * delta_alt);

    return res;
}

/* Оновлення положення з фільтрацією deadband та slew rate */
void tracker_update(TrackerController *tc, const GeoCoord *target, double dt_sec, uint16_t *pwm_pan, uint16_t *pwm_tilt) {
    if (!tc->has_home) return;

    TrackerAngles target_angles = tracker_calculate(&tc->home, target);

    /* Найкоротша кутова різниця для азимуту (-180..+180) */
    double diff_az = target_angles.azimuth_deg - tc->current_azimuth;
    while (diff_az > 180.0) diff_az -= 360.0;
    while (diff_az < -180.0) diff_az += 360.0;

    /* Перевірка зони нечутливості */
    if (fabs(diff_az) > tc->deadband_deg) {
        double max_step = tc->max_slew_rate_deg_s * dt_sec;
        if (diff_az > max_step) diff_az = max_step;
        if (diff_az < -max_step) diff_az = -max_step;

        tc->current_azimuth += diff_az;
        if (tc->current_azimuth >= 360.0) tc->current_azimuth -= 360.0;
        if (tc->current_azimuth < 0.0) tc->current_azimuth += 360.0;
    }

    /* Елевація */
    double diff_el = target_angles.elevation_deg - tc->current_elevation;
    if (fabs(diff_el) > tc->deadband_deg) {
        double max_step = tc->max_slew_rate_deg_s * dt_sec;
        if (diff_el > max_step) diff_el = max_step;
        if (diff_el < -max_step) diff_el = -max_step;
        tc->current_elevation += diff_el;
    }

    /* Конвертація кутів у ШІМ (1000..2000 мкс): Pan 0..360, Tilt 0..90 */
    *pwm_pan = (uint16_t)(1000.0 + (tc->current_azimuth / 360.0) * 1000.0);
    *pwm_tilt = (uint16_t)(1000.0 + (tc->current_elevation / 90.0) * 1000.0);
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <span>
#include <algorithm>
#include <chrono>

namespace tracker {

struct GeoCoord {
    double lat{0.0}; // Градуси (-90.0 .. +90.0)
    double lon{0.0}; // Градуси (-180.0 .. +180.0)
    double alt{0.0}; // Метри AMSL
};

struct TargetAngles {
    double azimuth_deg{0.0};   // 0.0 .. 360.0
    double elevation_deg{0.0}; // 0.0 .. 90.0
    double slant_range_m{0.0}; // Пряма лінійна дальність
};

struct ServoPwm {
    uint16_t pan_us{1500};
    uint16_t tilt_us{1000};
};

enum class TrackerError {
    HomeNotSet,
    InvalidCoordinates,
    Timeout
};

class AntennaTracker {
public:
    constexpr static double EarthRadiusM = 6371000.0;

    explicit AntennaTracker(double max_slew_rate_deg_s = 45.0, double deadband_deg = 1.5)
        : max_slew_rate_{max_slew_rate_deg_s}, deadband_{deadband_deg} {}

    void set_home(const GeoCoord& home) noexcept {
        home_pos_ = home;
        has_home_ = true;
    }

    [[nodiscard]] std::expected<TargetAngles, TrackerError>
    calculate_target(const GeoCoord& uav) const noexcept {
        if (!has_home_) {
            return std::unexpected(TrackerError::HomeNotSet);
        }

        constexpr double deg2rad = std::numbers::pi / 180.0;
        constexpr double rad2deg = 180.0 / std::numbers::pi;

        const double phi1 = home_pos_.lat * deg2rad;
        const double phi2 = uav.lat * deg2rad;
        const double d_phi = (uav.lat - home_pos_.lat) * deg2rad;
        const double d_lambda = (uav.lon - home_pos_.lon) * deg2rad;

        // Ортодромічна дистанція на поверхні еліпсоїда (сферичне наближення)
        const double a = std::sin(d_phi / 2.0) * std::sin(d_phi / 2.0) +
                         std::cos(phi1) * std::cos(phi2) *
                         std::sin(d_lambda / 2.0) * std::sin(d_lambda / 2.0);
        const double c = 2.0 * std::atan2(std::sqrt(a), std::sqrt(1.0 - a));
        const double ground_distance = EarthRadiusM * c;

        // Істинний азимут (Great Circle Initial Bearing)
        const double y = std::sin(d_lambda) * std::cos(phi2);
        const double x = std::cos(phi1) * std::sin(phi2) -
                         std::sin(phi1) * std::cos(phi2) * std::cos(d_lambda);
        double azimuth = std::atan2(y, x) * rad2deg;
        if (azimuth < 0.0) {
            azimuth += 360.0;
        }

        // Корекція кривини Землі для кута елевації
        const double curvature_drop = (ground_distance * ground_distance) / (2.0 * EarthRadiusM);
        const double delta_alt = (uav.alt - home_pos_.alt) - curvature_drop;

        double elevation = std::atan2(delta_alt, ground_distance) * rad2deg;
        elevation = std::clamp(elevation, 0.0, 90.0);

        const double slant_range = std::hypot(ground_distance, delta_alt);

        return TargetAngles{azimuth, elevation, slant_range};
    }

    [[nodiscard]] ServoPwm update(const GeoCoord& uav, double dt_sec) noexcept {
        auto target = calculate_target(uav);
        if (!target) {
            return ServoPwm{1500, 1000};
        }

        // Азимутальна фільтрація найкоротшого шляху
        double d_az = target->azimuth_deg - current_azimuth_;
        while (d_az > 180.0) d_az -= 360.0;
        while (d_az < -180.0) d_az += 360.0;

        if (std::abs(d_az) > deadband_) {
            const double max_step = max_slew_rate_ * dt_sec;
            d_az = std::clamp(d_az, -max_step, max_step);
            current_azimuth_ += d_az;
            if (current_azimuth_ >= 360.0) current_azimuth_ -= 360.0;
            if (current_azimuth_ < 0.0) current_azimuth_ += 360.0;
        }

        // Елеваційна фільтрація
        double d_el = target->elevation_deg - current_elevation_;
        if (std::abs(d_el) > deadband_) {
            const double max_step = max_slew_rate_ * dt_sec;
            d_el = std::clamp(d_el, -max_step, max_step);
            current_elevation_ += d_el;
        }

        // Перетворення в ШІМ мікросекунди
        auto pan_us = static_cast<uint16_t>(1000.0 + (current_azimuth_ / 360.0) * 1000.0);
        auto tilt_us = static_cast<uint16_t>(1000.0 + (current_elevation_ / 90.0) * 1000.0);

        return ServoPwm{pan_us, tilt_us};
    }

private:
    GeoCoord home_pos_{};
    bool has_home_{false};
    double current_azimuth_{0.0};
    double current_elevation_{0.0};
    double max_slew_rate_{45.0};
    double deadband_{1.5};
};

} // namespace tracker
```
:::

## Інтерфейси фізичних приводів

Для керування електромеханічною частиною трекера програма підтримує два типи апаратних виходів:
1. **Сервоприводи з прямим ШІМ-керуванням**: генерація стандартного сервоімпульсу частотою 50 Гц або 330 Гц (період 20 мс або 3 мс) за допомогою апаратних таймерів мікроконтролера або зовнішнього 12-бітного I2C ШІМ-контролера PCA9685. Ширина імпульсу 1000 мкс відповідає куту 0°, 1500 мкс — 180°, 2000 мкс — 360° (для панорами) або 0°..90° (для елевації).
2. **Крокові двигуни (Stepper Motors) з драйверами Step/Dir**: для важких антен вагою понад 2.5 кг застосовуються крокові двигуни NEMA 17/23 з редукторами хвильового типу (Harmonic Drive) або безлюфтовими черв'ячними передачами. Програма генерує пачки імпульсів `STEP` із плавним розгоном та гальмуванням, що виключає пропуск кроків при різкому пориві вітру. Поточне положення контролюється абсолютним магнітним енкодером AS5048A через шину SPI.

## Підводні камені та крайові випадки

1. **Сингулярність у зеніті (Zenith Singularity)**: коли борт пролітає безпосередньо над трекером (елевація 85°–90°), кутова швидкість азимуту прямує до нескінченності: мінімальне лінійне зміщення борту на кілька метрів вимагає миттєвого розвороту платформи на 180°. Якщо не обмежити кутову швидкість через slew-rate limiter, привід панорами зірветься в безперервне обертання та розхитає щоглу. При досягненні кута елевації понад 85° алгоритм автоматично фіксує азимут і чекає, поки борт вийде із зони сингулярності.
2. **Втрата телеметрії (Failsafe Timeout)**: якщо пакети MAVLink не надходять довше 3.0 секунд (наприклад, через постановку ворожої завади або затінення рельєфом), трекер зобов'язаний зафіксувати останні відомі кути або перейти в режим повільного секторного сканування ±15° від останнього вектора, а не скидати антени в нульове положення.
3. **Різниця висот над геоїдом та еліпсоїдом**: координати GPS у MAVLink передаються у висоті над середнім рівнем моря (AMSL). Якщо на наземній станції оператор використовує відносну барометричну висоту (AGL), різниця тиску між точками старту та зоною виконання місії призведе до кутової похибки елевації на кілька градусів. Для антени з шириною променя 12° на дистанціях понад 15 км така похибка повністю виведе борт за межі головної пелюстки діаграми спрямованості.
4. **Апаратний сторожовий таймер (Hardware Watchdog)**: оскільки контролер трекера встановлюється на верхівці щогли і недоступний для оперативного ручного перезапуску, внутрішній таймер WDT налаштовується на скидання мікроконтролера у разі зависання керувального циклу довше ніж на 500 мс, відновлюючи збережені в енергонезалежній пам'яті координати бази `Home` без участі оператора.
