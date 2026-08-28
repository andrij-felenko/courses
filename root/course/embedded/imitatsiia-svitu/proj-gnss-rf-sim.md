# ⚙️ Генерація радіосигналу GNSS на SDR та автоматизоване керування атенюатором

Тестування навігаційного приймача на рівні радіочастотного тракту (RF) вимагає не просто подачі розрахованих координат у послідовний порт мікроконтролера, а синтезу реальних електромагнітних коливань супутникового сузір'я. Програмно-визначене радіо (SDR, Software Defined Radio) синтезує суміш високочастотних сигналів від багатьох навігаційних космічних апаратів, враховуючи просторовий рух випробуваного апарата, обертання Землі, релятивістські ефекти, доплерівські зсуви частоти та затухання сигналу в атмосферних шарах.

Нижче наведено практичну реалізацію інженерного конвеєра: розрахунок орбітальних параметрів супутників за даними ефемерид, генерація псевдовипадкових далекомірних кодів Gold, формування квадратурних потоків I/Q та синхронне динамічне керування цифровим атенюатором через стандартний інтерфейс SCPI для моделювання радіозавад і зміни дистанції.

---

## 1. Орбітальна механіка та математична модель радіосигналу

Синтезатор починає роботу з читання стандартного навігаційного файлу RINEX (Receiver Independent Exchange Format), що містить параметри кеплерівських орбіт для кожного супутника сузір'я.

Для довільного моменту модельного часу `t` обчислюється вектор просторових координат супутника з індексом `i` у геоцентричній обертовій системі ECEF (Earth-Centered, Earth-Fixed):

```
X[i](t) = r[i](t) · (cos(Ω[i](t))·cos(u[i](t)) - sin(Ω[i](t))·sin(u[i](t))·cos(i[i]))
Y[i](t) = r[i](t) · (sin(Ω[i](t))·cos(u[i](t)) + cos(Ω[i](t))·sin(u[i](t))·cos(i[i]))
Z[i](t) = r[i](t) · (sin(u[i](t))·sin(i[i]))
```
де `r[i](t)` — поточний радіус-вектор супутника з урахуванням ексцентриситету орбіти, `u[i](t)` — аргумент широти, `Ω[i](t)` — довгота висхідного вузла з поправкою на кутову швидкість обертання Землі, а `i[i]` — орбітальний нахил.

Геометрична дистанція між фазовим центром антени супутника та приймачем на борту апарата `u` визначається евклідовою відстанню:

```
R[i](t) = √((X[i](t) - X[u](t))² + (Y[i](t) - Y[u](t))² + (Z[i](t) - Z[u](t))²)
```

Повна псевдовідстань `ρ[i](t)` враховує часову розбіжність бортових годинників та атмосферну затримку:

```
ρ[i](t) = R[i](t) + c·(δt[u](t) - δt[i](t)) + I[i](t) + T[i](t)
```
де:
- `c = 299 792 458 м/с` — швидкість світла у вакуумі;
- `δt[u](t)` — зсув шкали часу внутрішнього кварцового генератора приймача;
- `δt[i](t)` — похибка бортового атомного стандарту частоти супутника (визначається поліномом із файлу ефемерид);
- `I[i](t)` — додаткова фазова затримка в іоносфері (розраховується за моделлю Клобучара);
- `T[i](t)` — тропосферне запізнення радіохвилі (модель Саастамойнена).

Внаслідок взаємного просторового руху супутника зі швидкістю `V[i]` та випробуваного апарата зі швидкістю `V[u]` несуча частота радіосигналу зазнає доплерівського зсуву `Δf[i]`:

```
Δf[i](t) = - f₀ · ((V[i](t) - V[u](t)) · e[i](t)) / c
```
де `f₀ = 1575.42 МГц` (для цивільного діапазону GPS L1 C/A), а `e[i](t)` — одиничний вектор прямої видимості від приймача до супутника.

---

## 2. Структура радіокадру цивільного сигналу L1 C/A

Радіосигнал кожного супутника формується множенням трьох компонентів:
1. **Високочастотна несуча:** гармонійне коливання з частотою `f₀ = 1575.42 МГц` із фазовим зсувом `φ[i](t)`.
2. **Далекомірний псевдовипадковий код (C/A Code):** унікальна для кожного супутника послідовність Голда довжиною 1023 чипи, що повторюється щомілісекунди (тактова частота коду 1.023 Мчип/с). Код генерується двома 10-розрядними регістрами зсуву з лінійним зворотним зв'язком (LFSR G1 та G2).
3. **Навігаційне повідомлення (Navigation Data):** двійковий потік даних зі швидкістю 50 біт/с, що містить альманах, ефемериди, параметри корекції годинників та стан сузір'я.

Сумарний квадратурний радіочастотний сигнал, що випромінюється в антену SDR, являє собою когерентну суму сигналів від усіх одночасно видимих над горизонтом космічних апаратів:

```
s_RF(t) = ∑ [ A[i](t) · D[i](t) · C[i](t - τ[i]) · cos(2·π·(f₀ + Δf[i])·t + φ[i](0)) ]
```
де `A[i](t)` — амплітуда сигналу супутника (з урахуванням діаграми спрямованості антени та затухання), `D[i](t)` — біт навігаційних даних, `C[i]` — далекомірний код Голда, а `τ[i] = ρ[i] / c` — повний час поширення хвилі.

---

## 3. Програмна реалізація генератора та керування атенюатором

Нижче наведено модуль мовами C та C++, який виконує:
- Обчислення одиничного вектора прямої видимості та доплерівської частоти для кожного каналу.
- Синтез дискретних I/Q вибірок на частоті дискретизації 2.6 Мвиб/с для передавача SDR.
- Асинхронне керування кроковим RF-атенюатором за протоколом SCPI через інтерфейс UART/RS-232 для моделювання зміни потужності сигналу.

:::tabs
```c
/* gnss_rf_controller.c - С-версія модуля керування генератором та атенюатором */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define GPS_L1_FREQ_HZ   1575420000.0
#define SPEED_OF_LIGHT   299792458.0
#define SAMPLE_RATE_SPS  2600000.0
#define NUM_SATELLITES   8

typedef struct {
    double x, y, z;       /* Координати ECEF у метрах */
    double vx, vy, vz;    /* Швидкість у м/с */
} ecef_state_t;

typedef struct {
    int sat_prn;
    ecef_state_t pos;
    double doppler_hz;
    double pseudorange_m;
    double carrier_phase_rad;
    double snr_dbhz;
} satellite_channel_t;

typedef struct {
    int serial_fd;
    double current_attenuation_db;
} rf_attenuator_t;

/* Розрахунок доплерівського зсуву частоти */
double calculate_doppler(const ecef_state_t *user, const ecef_state_t *sat) {
    double dx = sat->x - user->x;
    double dy = sat->y - user->y;
    double dz = sat->z - user->z;
    double range = sqrt(dx*dx + dy*dy + dz*dz);
    if (range < 1.0) return 0.0;

    /* Одиничний вектор прямої видимості */
    double ex = dx / range;
    double ey = dy / range;
    double ez = dz / range;

    /* Вектор відносної швидкості */
    double dvx = sat->vx - user->vx;
    double dvy = sat->vy - user->vy;
    double dvz = sat->vz - user->vz;

    double v_relative = dvx * ex + dvy * ey + dvz * ez;
    return -GPS_L1_FREQ_HZ * (v_relative / SPEED_OF_LIGHT);
}

/* Формування SCPI команди для зміни загасання крокового атенюатора */
bool attenuator_set_db(rf_attenuator_t *att, double db) {
    if (db < 0.0) db = 0.0;
    if (db > 95.0) db = 95.0;

    char cmd_buffer[64];
    int len = snprintf(cmd_buffer, sizeof(cmd_buffer), ":ATT:VAL %.2f\n", db);
    if (len <= 0) return false;

    /* Надсилання команди в послідовний порт керування */
    printf("[SCPI TX] %s", cmd_buffer);
    att->current_attenuation_db = db;
    return true;
}

/* Генерація одного блоку 16-бітних I/Q вибірок для передавача SDR */
void generate_iq_block(satellite_channel_t *sats, int num_sats,
                       int16_t *iq_buffer, size_t num_samples) {
    const double dt = 1.0 / SAMPLE_RATE_SPS;

    for (size_t n = 0; n < num_samples; ++n) {
        double total_i = 0.0;
        double total_q = 0.0;

        for (int s = 0; s < num_sats; ++s) {
            satellite_channel_t *ch = &sats[s];
            
            /* Інтегрування фази з урахуванням доплера */
            ch->carrier_phase_rad += 2.0 * M_PI * ch->doppler_hz * dt;
            if (ch->carrier_phase_rad > 2.0 * M_PI) {
                ch->carrier_phase_rad -= 2.0 * M_PI;
            }

            /* Квадратурна модуляторна сума */
            total_i += cos(ch->carrier_phase_rad);
            total_q += sin(ch->carrier_phase_rad);
        }

        /* Масштабування до діапазону ЦАП SDR (-32768..+32767) */
        iq_buffer[2 * n]     = (int16_t)(total_i * 1000.0);
        iq_buffer[2 * n + 1] = (int16_t)(total_q * 1000.0);
    }
}
```
```cpp
/* gnss_rf_controller.hpp / .cpp - C++20 версія з типізованими класами та RAII */
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <string>
#include <format>
#include <expected>

constexpr double GPS_L1_FREQ_HZ  = 1575420000.0;
constexpr double SPEED_OF_LIGHT  = 299792458.0;
constexpr double SAMPLE_RATE_SPS = 2600000.0;

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
    [[nodiscard]] Vector3D operator-(const Vector3D& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }
    [[nodiscard]] double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }
};

struct SatelliteChannel {
    int prn{0};
    Vector3D position;
    Vector3D velocity;
    double doppler_hz{0.0};
    double carrier_phase_rad{0.0};
};

class RfAttenuator {
public:
    enum class Error { CommunicationFailed, OutOfRange };

    explicit RfAttenuator(std::string port_name) : port_{std::move(port_name)} {}

    [[nodiscard]] std::expected<void, Error> set_attenuation_db(double db) noexcept {
        if (db < 0.0 || db > 95.0) {
            return std::unexpected(Error::OutOfRange);
        }
        attenuation_db_ = db;
        std::string scpi_command = std::format(":ATT:VAL {:.2f}\n", db);
        
        /* Надсилання SCPI команди в апаратний порт */
        std::cout << "[SCPI C++ TX] " << scpi_command;
        return {};
    }

    [[nodiscard]] double current_db() const noexcept { return attenuation_db_; }

private:
    std::string port_;
    double attenuation_db_{0.0};
};

class GnssSignalSynthesizer {
public:
    explicit GnssSignalSynthesizer(std::vector<SatelliteChannel> channels)
        : channels_{std::move(channels)} {}

    void update_user_state(const Vector3D& user_pos, const Vector3D& user_vel) noexcept {
        for (auto& sat : channels_) {
            Vector3D los = sat.position - user_pos;
            double range = los.norm();
            if (range < 1.0) continue;

            Vector3D los_unit = {los.x / range, los.y / range, los.z / range};
            Vector3D rel_vel = sat.velocity - user_vel;
            sat.doppler_hz = -GPS_L1_FREQ_HZ * (rel_vel.dot(los_unit) / SPEED_OF_LIGHT);
        }
    }

    void generate_iq_samples(std::span<int16_t> interleaved_iq) noexcept {
        const double dt = 1.0 / SAMPLE_RATE_SPS;
        const size_t sample_count = interleaved_iq.size() / 2;

        for (size_t n = 0; n < sample_count; ++n) {
            double i_acc = 0.0;
            double q_acc = 0.0;

            for (auto& sat : channels_) {
                sat.carrier_phase_rad += 2.0 * std::numbers::pi * sat.doppler_hz * dt;
                if (sat.carrier_phase_rad > 2.0 * std::numbers::pi) {
                    sat.carrier_phase_rad -= 2.0 * std::numbers::pi;
                }
                i_acc += std::cos(sat.carrier_phase_rad);
                q_acc += std::sin(sat.carrier_phase_rad);
            }

            interleaved_iq[2 * n]     = static_cast<int16_t>(i_acc * 1000.0);
            interleaved_iq[2 * n + 1] = static_cast<int16_t>(q_acc * 1000.0);
        }
    }

private:
    std::vector<SatelliteChannel> channels_;
};
```
:::

---

## 4. Багатопроменевість та крайові часові події

У реальних умовах сигнал супутника потрапляє в антену не лише прямою лінією видимості, а й після відбиття від земної поверхні, води чи металевих конструкцій (Multipath Propagation). 

Відбитий промінь проходить додаткову відстань `ΔL = 2·h·sin(θ)`, де `h` — висота антени над площиною відбиття, а `θ` — кут підвищення супутника. Це створює затриману копію сигналу з фазовим зсувом:

```
Δτ = (2·h·sin(θ)) / c
```

Симулятор синтезує відбитий промінь із коефіцієнтом відбиття `Γ` (типово 0.3..0.7 для ґрунту) та оберненою поляризацією (з правого кругового обертання RHCP на ліве LHCP). Інтерференція прямого та відбитого променів викликає глибокі інтерференційні завмирання амплітуди та спотворення форми автокореляційного піка в кореляторі приймача, що зміщує оцінку псевдовідстані на 5–50 метрів.

Окремим критичним тестом є імітація стрибків системного часу:
- **Введення секунди координації (Leap Second):** перевірка коректності обробки стрибка різниці між шкалами UTC та GPS Time (GPS не містить секунд координації, поправка транслюється в навігаційному кадрі).
- **Переповнення лічильника тижнів (GPS Week Number Rollover):** 10-бітний лічильник тижнів переповнюється кожні 1024 тижні (приблизно 19.7 років). Стенд перевіряє, чи не скине прошивка дату на 1980 або 1999 рік.

---

## 5. Практичні правила експлуатації та захисту обладнання

1. **Каскад фіксованого розв'язання затухання:** вихідний підсилювач потужності SDR генерує сигнал на рівні 0 дБм (1 мВт). Чутливість сучасних багатосистемних приймачів становить -160 дБм (0.1 фемтоват). Між виходом SDR і входом приймача **завжди** підключають каскад фіксованих високочастотних атенюаторів сумарним номіналом не менше 60–80 дБ, після чого встановлюють керований цифровий атенюатор. Пряме підключення випалює вхідний LNA-транзистор навігаційного чипа за лічені мікросекунди.
2. **Радіоізоляція (Faraday Enclosure):** випробуваний приймач у процесі симуляції обов'язково розміщують усередині герметичного екранованого боксу із загасанням радіополя понад 80 дБ. Це повністю блокує справжні навігаційні сигнали з вулиці та унеможливлює випромінювання штучного радіосигналу назовні, що суворо заборонено правилами використання радіочастотного спектра.
3. **Тактування від спільного опорного генератора 10 МГц:** у разі тривалих прогонів системний кварц SDR та тактовий генератор стендового хоста можуть дрейфувати, викликаючи розсинхронізацію фази. Використання термостатованого опорного генератора (OCXO) гарантує стабільність фази та усуває розриви у відстеженні несучої частоти.
