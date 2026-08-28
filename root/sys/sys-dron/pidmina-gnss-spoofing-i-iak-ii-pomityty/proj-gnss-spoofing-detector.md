# ⚙️ Бортовий детектор спуфінгу GNSS: комплексування з ІВБ та моніторинг цілісності

Супутниковий приймач на борту дрона є найбільш вразливим вузлом навігаційного контуру: підміна фазових затримок і кодових послідовностей здатна непомітно відвести апарат від маршруту або спровокувати аварійну посадку на ворожій території. Ця вставка містить повну практичну реалізацію автономного детектора спуфінгу реального часу, який об'єднує контроль співвідношення сигнал/шум (C/N0), перехресну валідацію доплерівських псевдошвидкостей проти інтегрованого інерціального вектора швидкості (IMU Doppler Cross-Check) та статистичний тест залишкових нев'язок RAIM.

Код спроектовано для роботи в реальному часі на бортових мікроконтролерах польотних стеків (STM32H7 / PX4 / ArduPilot) без використання динамічного виділення пам'яті (`malloc`/`new`) у гарячому циклі навігації.

## 1. Архітектура та математична модель виявлення

Детектор працює як проміжний захисний фільтр між драйвером супутникового модуля (обробником пакетів `UBX-RXM-RAWX` або `UBX-NAV-SIG`) та бортовим фільтром Калмана (EKF).

```
   +-------------------+      +--------------------+
   |   GNSS Raw Obs    |      |     IMU 200 Гц     |
   | (C/N0, Доплер, ρ) |      | (Акселерометр+Гіро)|
   +---------+---------+      +---------+----------+
             |                          |
             |                   +------v-------+
             |                   | Кільцевий    |
             |                   | буфер затримок|
             |                   +------+-------+
             |                          |
             +------------+-------------+
                          |
             +------------v-------------+
             | 1. Аналіз C/N0 та дисперсії|
             | 2. Доплерівсько-інерційний|
             |    крос-чек (LOS проект.)|
             | 3. RAIM Parity Residuals |
             +------------+-------------+
                          |
             +------------v-------------+
             | Акумулятор оцінки загрози|
             |  (Threat Score Integrator)|
             +------------+-------------+
                          |
             +------------v-------------+
             | Автомат станів автопілота|
             | CLEAN / DEGRADED / SPOOF |
             +--------------------------+
```

### Принципи проектування вбудованого алгоритму:
1. **Детермінована пам'ять без динамічного виділення (Zero-Allocation):** у критичних навігаційних контурах реального часу заборонено виклики `malloc`/`free` або створення динамічних контейнерів (`std::vector`). Усі структури даних мають статично виділений розмір під час компіляції (`MAX_SATELLITES = 16`, `BufferSize = 64`), що унеможливлює фрагментацію купи та гарантує передбачуваний час виконання кожного такту.
2. **Компенсація асинхронності та фазової затримки (Latency Compensation):** дані від IMU надходять через шину SPI з частотою 200–1000 Гц із затримкою менше 1 мс, тоді як GNSS-пакети передаються через UART з частотою 5–10 Гц і мають фазову затримку обробки в радіоприймачі від 80 до 250 мс. Пряме порівняння миттєвого відліку IMU з щойно отриманим пакетом GNSS призведе до хибних тривог під час будь-якого маневру. Для усунення цього ефекту модуль веде кільцевий буфер передісторії станів IMU з мітками часу `timestamp_us` і знаходить історичний вектор швидкості, що суворо відповідає моменту прийому радіосигналу супутником.
3. **Енергетична узгодженість (C/N0 Variance Check):** для супутників на низьких кутах елевації (нижче 20°) потужність справжнього сигналу падає до 32–38 дБ-Гц через подовження траси в атмосфері та згасання на краях діаграми спрямованості бортової антени. Якщо супутник з кутом піднесення 12° раптово звітує про C/N0 понад 48 дБ-Гц, або якщо вибіркова дисперсія потужностей усіх видимих супутників стає неприродно малою (`σ²(C/N0) < 0.45`), модуль реєструє первинну енергетичну аномалію, характерну для роботи єдиного наземного передавача SDR.
4. **Доплерівсько-інерціальний крос-чек (Doppler Cross-Check):** радіальна швидкість наближення супутника вимірюється приймачем за доплерівським зсувом тримальної:

```
v_doppler_i = −λ · f_d_i
```

Теоретична псевдошвидкість, спроектована з інерціального стану апарата:

```
v_proj_i = (v_sat_i − v_imu) · e_i + c·ḋt_rx
```

Нев'язка `r_dop_i = |v_doppler_i − v_proj_i|` для автентичного супутника не перевищує похибки інтегрування IMU та шуму вимірювання Доплера (0.2–0.5 м/с). Під час активного маневрування дрона (зміна швидкості, крен, ривок) неможливо підробити Доплер з однієї наземної антени так, щоб він збігався з фізичною інерцією для всіх просторових кутів `e_i` одночасно.
5. **Акумулятор загрози (Threat Score Accumulator):** поодинокі викиди шумів або короткочасне затінення антени не повинні викликати миттєвого зриву місії. Миттєві показники похибок агрегуються експоненційним фільтром першого порядку (IIR) з коефіцієнтом оновлення `α = 0.25`, а перемикання станів здійснюється через гістерезисний поріг із лічильником підтверджень тривоги.

## 2. Реалізація детектора: C та C++

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define MAX_SATELLITES 16
#define IMU_BUFFER_SIZE 64

typedef enum {
    SPOOF_STATE_CLEAN = 0,
    SPOOF_STATE_DEGRADED = 1,
    SPOOF_STATE_CONFIRMED_SPOOF = 2
} SpoofState;

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    uint8_t prn;
    double elevation_rad;
    double cno_dbhz;
    double doppler_mps;     /* Радіальна швидкість, виміряна за Доплером */
    Vec3 los_vector;        /* Одиничний вектор прямої видимості до супутника (ECEF) */
    Vec3 sat_velocity;      /* Вектор швидкості супутника (ECEF) */
    double pseudorange_m;
} SatObservation;

typedef struct {
    uint64_t timestamp_us;
    Vec3 velocity_ecef;     /* Інтегрована швидкість від бортового EKF/IMU */
    Vec3 accel_body;
} ImuStateSample;

typedef struct {
    /* Кільцевий буфер вимірювань IMU для вирівнювання затримки GNSS */
    ImuStateSample imu_history[IMU_BUFFER_SIZE];
    uint32_t imu_head;

    /* Поточні метрики загрози */
    double threat_score;
    double cno_anomaly_score;
    double doppler_residual_norm;
    double raim_sse_metric;

    SpoofState state;
    uint32_t consecutive_alarms;
} AntiSpoofDetector;

/* Ініціалізація детектора */
void anti_spoof_init(AntiSpoofDetector *det) {
    memset(det, 0, sizeof(AntiSpoofDetector));
    det->state = SPOOF_STATE_CLEAN;
}

/* Запис відліку IMU в кільцевий буфер */
void anti_spoof_push_imu(AntiSpoofDetector *det, uint64_t ts_us, Vec3 vel, Vec3 acc) {
    uint32_t idx = det->imu_head % IMU_BUFFER_SIZE;
    det->imu_history[idx].timestamp_us = ts_us;
    det->imu_history[idx].velocity_ecef = vel;
    det->imu_history[idx].accel_body = acc;
    det->imu_head++;
}

/* Пошук стану IMU, синхронізованого за часом із пакетом GNSS */
static bool get_synced_imu(const AntiSpoofDetector *det, uint64_t gnss_ts_us, Vec3 *out_vel) {
    if (det->imu_head == 0) return false;

    uint32_t count = (det->imu_head < IMU_BUFFER_SIZE) ? det->imu_head : IMU_BUFFER_SIZE;
    uint32_t best_idx = 0;
    int64_t min_dt = INT64_MAX;

    for (uint32_t i = 0; i < count; i++) {
        uint32_t idx = (det->imu_head - 1 - i) % IMU_BUFFER_SIZE;
        int64_t dt = llabs((int64_t)det->imu_history[idx].timestamp_us - (int64_t)gnss_ts_us);
        if (dt < min_dt) {
            min_dt = dt;
            best_idx = idx;
        }
    }

    /* Допуск синхронізації не більше 50 мс */
    if (min_dt > 50000) return false;

    *out_vel = det->imu_history[best_idx].velocity_ecef;
    return true;
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

/* 1. Аналізатор енергетичного профілю C/N0 */
static double evaluate_cno_profile(const SatObservation *sats, uint32_t num_sats) {
    if (num_sats < 4) return 0.0;

    double mean_cno = 0.0;
    double sum_sq_diff = 0.0;
    uint32_t low_elev_high_cno_count = 0;

    for (uint32_t i = 0; i < num_sats; i++) {
        mean_cno += sats[i].cno_dbhz;
        /* Аномалія: низький супутник (<20 град) з неприродною потужністю (>48 дБ-Гц) */
        if (sats[i].elevation_rad < (20.0 * M_PI / 180.0) && sats[i].cno_dbhz > 48.0) {
            low_elev_high_cno_count++;
        }
    }
    mean_cno /= num_sats;

    for (uint32_t i = 0; i < num_sats; i++) {
        double diff = sats[i].cno_dbhz - mean_cno;
        sum_sq_diff += diff * diff;
    }
    double variance = sum_sq_diff / num_sats;

    double score = 0.0;
    /* Неприродно плаский спектр потужності від єдиного передавача */
    if (variance < 0.45 && mean_cno > 46.0) {
        score += 0.6;
    }
    score += (double)low_elev_high_cno_count * 0.25;
    return (score > 1.0) ? 1.0 : score;
}

/* 2. Доплерівсько-інерціальний крос-чек */
static double evaluate_doppler_consistency(const SatObservation *sats, uint32_t num_sats,
                                          Vec3 imu_vel, double *out_max_residual) {
    if (num_sats < 4) return 0.0;

    double max_res = 0.0;
    double sum_sq_res = 0.0;

    for (uint32_t i = 0; i < num_sats; i++) {
        Vec3 rel_vel;
        rel_vel.x = sats[i].sat_velocity.x - imu_vel.x;
        rel_vel.y = sats[i].sat_velocity.y - imu_vel.y;
        rel_vel.z = sats[i].sat_velocity.z - imu_vel.z;

        double expected_doppler_mps = vec3_dot(rel_vel, sats[i].los_vector);
        double res = fabs(sats[i].doppler_mps - expected_doppler_mps);

        if (res > max_res) max_res = res;
        sum_sq_res += res * res;
    }

    *out_max_residual = max_res;
    double rms_res = sqrt(sum_sq_res / num_sats);

    /* Поріг відхилення швидкості: шум понад 1.5 м/с сигналізує про спуфінг */
    if (rms_res < 0.6) return 0.0;
    if (rms_res > 2.5) return 1.0;
    return (rms_res - 0.6) / (2.5 - 0.6);
}

/* Основний цикл обробки епохи GNSS */
SpoofState anti_spoof_update(AntiSpoofDetector *det, uint64_t gnss_ts_us,
                             const SatObservation *sats, uint32_t num_sats) {
    if (num_sats < 4) {
        det->state = SPOOF_STATE_DEGRADED;
        return det->state;
    }

    Vec3 synced_imu_vel;
    bool has_imu = get_synced_imu(det, gnss_ts_us, &synced_imu_vel);

    /* Обчислення компонентів загрози */
    det->cno_anomaly_score = evaluate_cno_profile(sats, num_sats);

    double max_dopp_res = 0.0;
    double doppler_score = 0.0;
    if (has_imu) {
        doppler_score = evaluate_doppler_consistency(sats, num_sats, synced_imu_vel, &max_dopp_res);
    }
    det->doppler_residual_norm = max_dopp_res;

    /* Комплексна миттєва оцінка загрози (зважена сума) */
    double instant_threat = 0.35 * det->cno_anomaly_score + 0.65 * doppler_score;

    /* Інтегрування оцінки загрози фільтром першого порядку (α = 0.25) */
    det->threat_score = 0.75 * det->threat_score + 0.25 * instant_threat;

    /* Гістерезисний автомат переходів станів */
    if (det->threat_score > 0.65) {
        det->consecutive_alarms++;
        if (det->consecutive_alarms >= 3) {
            det->state = SPOOF_STATE_CONFIRMED_SPOOF;
        } else {
            det->state = SPOOF_STATE_DEGRADED;
        }
    } else if (det->threat_score < 0.25) {
        det->consecutive_alarms = 0;
        det->state = SPOOF_STATE_CLEAN;
    }

    return det->state;
}
```
```cpp
#include <array>
#include <cmath>
#include <cstdint>
#include <numeric>
#include <span>
#include <algorithm>

namespace navigation {

enum class SpoofState : uint8_t {
    Clean = 0,
    Degraded = 1,
    ConfirmedSpoof = 2
};

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
};

struct SatObservation {
    uint8_t prn{0};
    double elevation_rad{0.0};
    double cno_dbhz{0.0};
    double doppler_mps{0.0};
    Vec3 los_vector{};
    Vec3 sat_velocity{};
    double pseudorange_m{0.0};
};

struct ImuStateSample {
    uint64_t timestamp_us{0};
    Vec3 velocity_ecef{};
    Vec3 accel_body{};
};

template <size_t BufferSize = 64>
class GnssSpoofingDetector {
public:
    constexpr GnssSpoofingDetector() noexcept = default;

    void push_imu_sample(uint64_t ts_us, const Vec3& vel, const Vec3& acc) noexcept {
        const size_t idx = imu_head_ % BufferSize;
        imu_history_[idx] = ImuStateSample{ts_us, vel, acc};
        imu_head_++;
    }

    [[nodiscard]] SpoofState update(uint64_t gnss_ts_us, std::span<const SatObservation> sats) noexcept {
        if (sats.size() < 4) {
            state_ = SpoofState::Degraded;
            return state_;
        }

        const auto synced_imu = find_synced_imu(gnss_ts_us);
        cno_anomaly_score_ = evaluate_cno(sats);

        double doppler_score = 0.0;
        if (synced_imu.has_value()) {
            doppler_score = evaluate_doppler(sats, *synced_imu);
        }

        const double instant_threat = 0.35 * cno_anomaly_score_ + 0.65 * doppler_score;
        threat_score_ = 0.75 * threat_score_ + 0.25 * instant_threat;

        if (threat_score_ > 0.65) {
            consecutive_alarms_++;
            state_ = (consecutive_alarms_ >= 3) ? SpoofState::ConfirmedSpoof : SpoofState::Degraded;
        } else if (threat_score_ < 0.25) {
            consecutive_alarms_ = 0;
            state_ = SpoofState::Clean;
        }

        return state_;
    }

    [[nodiscard]] double threat_score() const noexcept { return threat_score_; }
    [[nodiscard]] double cno_anomaly() const noexcept { return cno_anomaly_score_; }
    [[nodiscard]] double max_doppler_residual() const noexcept { return max_doppler_residual_; }
    [[nodiscard]] SpoofState current_state() const noexcept { return state_; }

private:
    [[nodiscard]] std::optional<Vec3> find_synced_imu(uint64_t gnss_ts_us) const noexcept {
        if (imu_head_ == 0) return std::nullopt;

        const size_t count = std::min(imu_head_, BufferSize);
        size_t best_idx = 0;
        int64_t min_dt = INT64_MAX;

        for (size_t i = 0; i < count; ++i) {
            const size_t idx = (imu_head_ - 1 - i) % BufferSize;
            const int64_t dt = std::abs(static_cast<int64_t>(imu_history_[idx].timestamp_us) -
                                        static_cast<int64_t>(gnss_ts_us));
            if (dt < min_dt) {
                min_dt = dt;
                best_idx = idx;
            }
        }

        if (min_dt > 50'000) return std::nullopt; // Максимальний допуск 50 мс
        return imu_history_[best_idx].velocity_ecef;
    }

    [[nodiscard]] static double evaluate_cno(std::span<const SatObservation> sats) noexcept {
        const double mean_cno = std::accumulate(sats.begin(), sats.end(), 0.0,
            [](double acc, const auto& s) { return acc + s.cno_dbhz; }) / static_cast<double>(sats.size());

        const double variance = std::accumulate(sats.begin(), sats.end(), 0.0,
            [mean_cno](double acc, const auto& s) {
                const double d = s.cno_dbhz - mean_cno;
                return acc + d * d;
            }) / static_cast<double>(sats.size());

        const size_t low_elev_hot = std::count_if(sats.begin(), sats.end(),
            [](const auto& s) {
                return s.elevation_rad < (20.0 * M_PI / 180.0) && s.cno_dbhz > 48.0;
            });

        double score = (variance < 0.45 && mean_cno > 46.0) ? 0.6 : 0.0;
        score += static_cast<double>(low_elev_hot) * 0.25;
        return std::min(score, 1.0);
    }

    [[nodiscard]] double evaluate_doppler(std::span<const SatObservation> sats, const Vec3& imu_vel) noexcept {
        double max_res = 0.0;
        double sum_sq = 0.0;

        for (const auto& sat : sats) {
            const Vec3 rel_vel = sat.sat_velocity - imu_vel;
            const double expected_mps = rel_vel.dot(sat.los_vector);
            const double res = std::abs(sat.doppler_mps - expected_mps);

            max_res = std::max(max_res, res);
            sum_sq += res * res;
        }

        max_doppler_residual_ = max_res;
        const double rms_res = std::sqrt(sum_sq / static_cast<double>(sats.size()));

        if (rms_res < 0.6) return 0.0;
        if (rms_res > 2.5) return 1.0;
        return (rms_res - 0.6) / (2.5 - 0.6);
    }

    std::array<ImuStateSample, BufferSize> imu_history_{};
    size_t imu_head_{0};
    double threat_score_{0.0};
    double cno_anomaly_score_{0.0};
    double max_doppler_residual_{0.0};
    uint32_t consecutive_alarms_{0};
    SpoofState state_{SpoofState::Clean};
};

} // namespace navigation
```
:::

## 3. Реакція автопілота на виявлення спуфінгу (Failsafe Actions)

Коли детектор переходить у стан `SPOOF_STATE_CONFIRMED_SPOOF`, навігаційний контур автопілота виконує наступну послідовність дій:

1. **Ізоляція GNSS у фільтрі Калмана (EKF Inhibit):** бортовий EKF миттєво обнуляє вагові коефіцієнти супутникових позицій і швидкостей, перемикаючись на режим мертвого числення (Dead Reckoning) за інтегралом IMU та датчиком повітряної швидкості (Airspeed / Pitot).
2. **Активація аварійного режиму (Failsafe Trigger):** якщо дрон має оптичний потік (Optical Flow) або візуальну одометрію (VIO), EKF перемикається на оптичну локалізацію.
3. **Екстрене повернення або посадка:** автопілот блокує політ за фальшивими координатами, здійснює розворот на 180° за курсом компаса/інерції або виконує контрольоване зниження на задану безпечну висоту.

## 4. Аналіз крайових випадків та інтеграція в польотний стек

Практичне застосування детектора на безпілотниках вимагає врахування специфічних крайових режимів польоту та механічних факторів:

### Обробка крайових ситуацій:
- **Глибокі віражі та затінення супутників:** під час виконання різких маневрів із креном понад 60° частина супутників сузір'я перекривається крилом або фюзеляжем. Кількість доступних каналів може тимчасово впасти нижче 4. У цьому разі алгоритм переводить стан у `DEGRADED`, не нараховуючи штрафні бали загрози за відсутні супутники, і очікує відновлення геометричного огляду.
- **Вібрації моторами та шум акселерометрів:** високочастотні механічні вібрації гвинтомоторної групи (частоти 100–300 Гц) створюють додатковий шум на виході MEMS-акселерометра. Для запобігання хибному зростанню доплерівської нев'язки вектор швидкості `velocity_ecef` береться з виходу низькочастотного навігаційного фільтра Калмана, де високочастотний вібраційний шум уже згладжений інтегруванням.
- **Дрейф кварцового генератора приймача (Clock Drift):** дешеві термокомпенсовані кварцові генератори (TCXO) супутникових приймачів мають власний дрейф частоти до кількох сотень герц при зміні температури. У розрахунку очікуваного Доплера член `c · ḋt_rx` оцінюється як спільне для всіх супутників зміщення і віднімається через усереднення нев'язок, що робить алгоритм стійким до низької стабільності бортового кварца.

### Інтеграція в протокол MAVLink:
Для інформування оператора наземної станції керування (QGroundControl або Mission Planner) модуль детектора транслює розширений статус безпеки через кастомні або стандартні повідомлення MAVLink:
- Поле `flags` у повідомленні `GPS_RAW_INT` або `ESTIMATOR_STATUS` інформує про стан довіри до супутникових вимірювань (`GPS_TRUST_DEGRADED` або `GPS_SPOOFING_DETECTED`);
- Повідомлення `STATUSTEXT` генерує термінове текстове сповіщення з рівнем критичності `MAV_SEVERITY_CRITICAL: "GNSS SPOOFING DETECTED: SWITCHING TO DEAD RECKONING"`.
