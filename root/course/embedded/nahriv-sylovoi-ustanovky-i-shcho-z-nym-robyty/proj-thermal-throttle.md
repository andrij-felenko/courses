# ⚙️ Бортовий тепловий спостерігач і захист регулятора

Більшість польотних контролерів безпілотників та регуляторів швидкості мають критичну асиметрію сенсорного оснащення: на платі ESC встановлено аналоговий NTC-термістор, що вимірює температуру силових MOSFET-транзисторів, тоді як безколекторні мотори позбавлені будь-яких вбудованих давачів температури задля зниження маси, вартості та габаритів. Якщо регулятор може напряму повідомити свій нагрів через телеметрію DShot або послідовний порт, то перегрів обмоток мотора та ризик розмагнічування неодимових магнітів залишаються «сліпою зоною» автопілота.

Нижче розібрано практичну реалізацію бортового модуля теплового моніторингу для польотного контролера (ArduPilot / PX4 / Betaflight). Модуль розв'язує два взаємопов'язані інженерні завдання:
1. **Тепловий спостерігач мотора (Thermal Observer):** обчислює в реальному часі оцінку температури мідних обмоток `T_winding` та заліза статора `T_core` на основі виміряного фазного струму, обертів eRPM та оцінки конвективного охолодження від набігаючого потоку;
2. **Адаптивний термотротлінг (Thermal Throttling):** плавно обмежує максимальну скважність газу при наближенні регулятора або мотора до критичного теплового порогу, запобігаючи руйнуванню силових ключів та розмагнічуванню ротора.

## Протоколи бортової телеметрії та отримання даних

Щоб тепловий спостерігач міг коректно розрахувати виділення тепла, мікроконтролер польотного контролера повинен безперервно отримувати з регулятора три фізичні величини: споживаний струм, напругу батареї та електричну частоту обертання ротора `eRPM`. 

Сучасні системи використовують два альтернативні канали передачі даних:
- **Двонаправлений DShot (Bidirectional DShot):** зворотний зв'язок передається тим самим сигнальним проводом, що й команди керування мотором. Після кожного вихідного пакета команд ESC надсилає контролеру 16-бітний кадр з даними періоду комутації (eRPM) та статусу, захищений контрольною сумою CRC4. Оновлення обертів відбувається з надвисокою частотою (до 4–8 кГц);
- **Послідовна телеметрія ESC (KISS / BLHeli_32 / AM32 Telemetry):** окрема лінія UART (115200 бод), якою регулятор транслює циклічний 10-байтний пакет зі швидкістю 50–100 Гц. Пакет містить температуру NTC-термістора (°C), напругу (соті вольта), струм (соті ампера), витрачені міліампер-години та оберти eRPM.

Перед використанням у теплових рівняннях сирі покази термодавача ESC проходять цифрову фільтрацію низьких частот (Low-Pass Filter, LPF) для усунення високочастотних комутаційних завад, викликаних роботою силових ключів інвертора.

## Математична структура теплового спостерігача

Модель описує тепловий стан мотора двома дискретними вузлами: теплоємністю мідних обмоток `C_wind` та теплоємністю статора `C_core`.

Динаміка нагріву описується системою зв'язаних диференціальних рівнянь першого порядку:

```
C_wind · (d T_wind / dt) = P_copper − (T_wind − T_core) / R_th_wind_core
C_core · (d T_core / dt) = P_iron + (T_wind − T_core) / R_th_wind_core − (T_core − T_amb) / R_th_air
```

На кожному кроці дискретизації за часом `dt`:
1. Розраховуються омічні втрати в міді з урахуванням температурного коефіцієнта опору:
   `P_cu = 1.5 · I_phase² · R_0 · (1 + α · (T_wind − 20))`;
2. Розраховуються магнітні втрати в статорі за швидкістю обертання:
   `P_fe = k_fe · (eRPM / 1000)^1.8`;
3. Ефективний тепловий опір конвекції `R_th_air` динамічно зменшується зі зростанням обертів пропелера, оскільки набігаючий потік повітря зриває нагрітий примежовий шар статора;
4. Температури обмотки й статора інтегруються дискретним методом Ейлера.

## Реалізація модуля теплового захисту

:::tabs
```c
// thermal_protection.h / thermal_protection.c
#include <stdint.h>
#include <stdbool.h>

#define THERMAL_MAX_CHANNELS 4

typedef struct {
    // Параметри мотора
    float r_phase_20c;       // Опір фази при 20°C (Ом)
    float alpha_copper;      // Температурний коефіцієнт міді (0.00393 1/°C)
    float c_th_wind;         // Теплоємність міді обмоток (Дж/°C)
    float c_th_core;         // Теплоємність статора (Дж/°C)
    float r_th_wind_core;    // Тепловий опір обмотка-залізо (°C/Вт)
    float r_th_core_air_base;// Базовий тепловий опір залізо-повітря без обдуву (°C/Вт)
    float k_iron_loss;       // Емпіричний коефіцієнт втрат у залізі

    // Пороги тротлінгу для регулятора (°C)
    float esc_temp_warn;     // Початок лінійного тротлінгу (напр. 95°C)
    float esc_temp_crit;     // Повний тротлінг / мінімальна тяга (напр. 115°C)

    // Пороги тротлінгу для мотора (°C)
    float motor_temp_warn;   // Початок тротлінгу обмотки (напр. 100°C)
    float motor_temp_crit;   // Критична межа ізоляції/магнітів (напр. 130°C)
    float min_throttle_scale;// Мінімальний коефіцієнт газу при тротлінгу (напр. 0.35f)
} ThermalConfig;

typedef struct {
    float t_wind_est;        // Оцінка температури обмотки (°C)
    float t_core_est;        // Оцінка температури статора (°C)
    float esc_temp_filtered; // Фільтрована температура телеметрії ESC (°C)
    float throttle_scale;    // Поточний коефіцієнт обмеження газу (0.0 .. 1.0)
    bool  is_overheated;     // Прапорець активного захисту від перегріву
} ThermalState;

typedef struct {
    ThermalConfig config;
    ThermalState  channels[THERMAL_MAX_CHANNELS];
    float         ambient_temp_c;
} ThermalManager;

void thermal_init(ThermalManager *mgr, const ThermalConfig *cfg, float amb_temp) {
    mgr->config = *cfg;
    mgr->ambient_temp_c = amb_temp;
    for (int i = 0; i < THERMAL_MAX_CHANNELS; ++i) {
        mgr->channels[i].t_wind_est = amb_temp;
        mgr->channels[i].t_core_est = amb_temp;
        mgr->channels[i].esc_temp_filtered = amb_temp;
        mgr->channels[i].throttle_scale = 1.0f;
        mgr->channels[i].is_overheated = false;
    }
}

// Оновлення теплового стану мотора та ESC на одному каналі
void thermal_update_channel(ThermalManager *mgr, uint8_t ch, float current_amps,
                            uint32_t erpm, float esc_raw_temp, float dt_sec) {
    if (ch >= THERMAL_MAX_CHANNELS || dt_sec <= 0.0f) return;

    ThermalState *st = &mgr->channels[ch];
    const ThermalConfig *cfg = &mgr->config;

    // 1. Фільтрація виміряної температури ESC (Low-Pass Filter, стала часу ~0.5 с)
    float alpha_lpf = dt_sec / (0.5f + dt_sec);
    st->esc_temp_filtered += alpha_lpf * (esc_raw_temp - st->esc_temp_filtered);

    // 2. Тепловий спостерігач мотора
    // Опір міді з урахуванням температури
    float r_cu = cfg->r_phase_20c * (1.0f + cfg->alpha_copper * (st->t_wind_est - 20.0f));
    float p_copper = 1.5f * current_amps * current_amps * r_cu;

    // Магнітні втрати в статорі
    float erpm_k = (float)erpm * 0.001f;
    float p_iron = cfg->k_iron_loss * erpm_k * erpm_k;

    // Динамічний тепловий опір у повітря (конвекція зростає з обертами)
    float airflow_factor = 1.0f + 0.05f * erpm_k;
    float r_th_air = cfg->r_th_core_air_base / airflow_factor;

    // Теплові потоки
    float q_wind_to_core = (st->t_wind_est - st->t_core_est) / cfg->r_th_wind_core;
    float q_core_to_air  = (st->t_core_est - mgr->ambient_temp_c) / r_th_air;

    // Диференціальні рівняння нагріву (метод Ейлера)
    float d_t_wind = (p_copper - q_wind_to_core) / cfg->c_th_wind;
    float d_t_core = (q_wind_to_core + p_iron - q_core_to_air) / cfg->c_th_core;

    st->t_wind_est += d_t_wind * dt_sec;
    st->t_core_est += d_t_core * dt_sec;

    // 3. Розрахунок коефіцієнтів тротлінгу
    // Тротлінг за температурою ESC
    float scale_esc = 1.0f;
    if (st->esc_temp_filtered > cfg->esc_temp_warn) {
        float span = cfg->esc_temp_crit - cfg->esc_temp_warn;
        scale_esc = 1.0f - (st->esc_temp_filtered - cfg->esc_temp_warn) / span;
        if (scale_esc < cfg->min_throttle_scale) scale_esc = cfg->min_throttle_scale;
    }

    // Тротлінг за оцінкою температури обмотки мотора
    float scale_motor = 1.0f;
    if (st->t_wind_est > cfg->motor_temp_warn) {
        float span = cfg->motor_temp_crit - cfg->motor_temp_warn;
        scale_motor = 1.0f - (st->t_wind_est - cfg->motor_temp_warn) / span;
        if (scale_motor < cfg->min_throttle_scale) scale_motor = cfg->min_throttle_scale;
    }

    // Беремо найсуворіше обмеження з двох компонентів
    float target_scale = (scale_esc < scale_motor) ? scale_esc : scale_motor;

    // Швидкісне згладжування тротлінгу (Rate Limiter) для виключення ривків тяги
    float max_slew = 0.5f * dt_sec; // Максимальна зміна газу не більше 50%/сек
    if (target_scale < st->throttle_scale) {
        st->throttle_scale -= max_slew;
        if (st->throttle_scale < target_scale) st->throttle_scale = target_scale;
    } else {
        st->throttle_scale += max_slew;
        if (st->throttle_scale > target_scale) st->throttle_scale = target_scale;
    }

    st->is_overheated = (st->throttle_scale < 0.98f);
}

// Застосування теплового обмеження до вхідної команди газу
float thermal_apply_throttle(const ThermalManager *mgr, uint8_t ch, float requested_throttle) {
    if (ch >= THERMAL_MAX_CHANNELS) return requested_throttle;
    if (requested_throttle <= 0.0f) return 0.0f;
    return requested_throttle * mgr->channels[ch].throttle_scale;
}
```
```cpp
// ThermalProtection.hpp — Ідіоматичний C++20 модуль моніторингу
#pragma once
#include <array>
#include <algorithm>
#include <span>
#include <cstdint>

namespace propulsion::thermal {

struct Config {
    float r_phase_20c{0.045f};         // Опір фази мотора при 20°C (Ом)
    float alpha_copper{0.00393f};       // Температурний коефіцієнт опору міді
    float c_th_wind{3.5f};              // Теплоємність міді обмотки (Дж/°C)
    float c_th_core{18.0f};             // Теплоємність статора (Дж/°C)
    float r_th_wind_core{1.2f};         // Тепловий опір обмотка-статор (°C/Вт)
    float r_th_core_air_base{4.8f};     // Тепловий опір статор-повітря (°C/Вт)
    float k_iron_loss{0.0025f};         // Коефіцієнт магнітних втрат статора

    float esc_temp_warn{95.0f};         // Початок тротлінгу ESC (°C)
    float esc_temp_crit{115.0f};        // Критична межа ESC (°C)
    float motor_temp_warn{100.0f};      // Початок тротлінгу мотора (°C)
    float motor_temp_crit{130.0f};      // Критична межа мотора (°C)
    float min_throttle_scale{0.35f};    // Мінімально допустимий газ тротлінгу
};

struct ChannelState {
    float t_wind_est{25.0f};
    float t_core_est{25.0f};
    float esc_temp_filtered{25.0f};
    float throttle_scale{1.0f};
    bool  is_overheated{false};
};

template <std::size_t NumChannels = 4>
class ThermalProtectionManager {
public:
    explicit constexpr ThermalProtectionManager(const Config& config, float ambient_c = 25.0f) noexcept
        : config_{config}, ambient_temp_c_{ambient_c} {
        for (auto& ch : channels_) {
            ch.t_wind_est = ambient_c;
            ch.t_core_est = ambient_c;
            ch.esc_temp_filtered = ambient_c;
        }
    }

    void update(std::size_t channel, float current_amps, uint32_t erpm,
                float esc_raw_temp, float dt_sec) noexcept {
        if (channel >= NumChannels || dt_sec <= 0.0f) return;

        auto& st = channels_[channel];

        // 1. Фільтрація температури ESC
        const float alpha_lpf = dt_sec / (0.5f + dt_sec);
        st.esc_temp_filtered += alpha_lpf * (esc_raw_temp - st.esc_temp_filtered);

        // 2. Тепловий спостерігач обмотки мотора
        const float r_cu = config_.r_phase_20c * (1.0f + config_.alpha_copper * (st.t_wind_est - 20.0f));
        const float p_copper = 1.5f * current_amps * current_amps * r_cu;

        const float erpm_k = static_cast<float>(erpm) * 0.001f;
        const float p_iron = config_.k_iron_loss * erpm_k * erpm_k;

        const float airflow_factor = 1.0f + 0.05f * erpm_k;
        const float r_th_air = config_.r_th_core_air_base / airflow_factor;

        const float q_wind_to_core = (st.t_wind_est - st.t_core_est) / config_.r_th_wind_core;
        const float q_core_to_air  = (st.t_core_est - ambient_temp_c_) / r_th_air;

        const float d_t_wind = (p_copper - q_wind_to_core) / config_.c_th_wind;
        const float d_t_core = (q_wind_to_core + p_iron - q_core_to_air) / config_.c_th_core;

        st.t_wind_est += d_t_wind * dt_sec;
        st.t_core_est += d_t_core * dt_sec;

        // 3. Розрахунок тротлінгу
        auto compute_scale = [this](float temp, float warn, float crit) noexcept -> float {
            if (temp <= warn) return 1.0f;
            if (temp >= crit) return config_.min_throttle_scale;
            return std::clamp(1.0f - (temp - warn) / (crit - warn),
                              config_.min_throttle_scale, 1.0f);
        };

        const float target_scale = std::min(
            compute_scale(st.esc_temp_filtered, config_.esc_temp_warn, config_.esc_temp_crit),
            compute_scale(st.t_wind_est, config_.motor_temp_warn, config_.motor_temp_crit)
        );

        // Плавний перехід (Rate Limiter 50%/с)
        const float max_slew = 0.5f * dt_sec;
        if (target_scale < st.throttle_scale) {
            st.throttle_scale = std::max(target_scale, st.throttle_scale - max_slew);
        } else {
            st.throttle_scale = std::min(target_scale, st.throttle_scale + max_slew);
        }

        st.is_overheated = (st.throttle_scale < 0.98f);
    }

    [[nodiscard]] constexpr float apply_throttle(std::size_t channel, float requested_throttle) const noexcept {
        if (channel >= NumChannels || requested_throttle <= 0.0f) return requested_throttle;
        return requested_throttle * channels_[channel].throttle_scale;
    }

    [[nodiscard]] const ChannelState& channel_state(std::size_t channel) const noexcept {
        return channels_[channel];
    }

private:
    Config config_;
    float  ambient_temp_c_{25.0f};
    std::array<ChannelState, NumChannels> channels_{};
};

} // namespace propulsion::thermal
```
:::

## Взаємодія з PID-регулятором і калібрування констант

Впровадження обмеження тяги за температурою безпосередньо впливає на контур стабілізації апарата. Якщо польотний контролер зменшує тягу окремого мотора через локальний перегрів, PID-регулятор кутової швидкості (Rate PID) спробує компенсувати крен або тангаж збільшенням інтегральної складової (I-term).

Щоб запобігти інтегральному насиченню (англ. *Integrator Windup*) та розгойдуванню дрона:
1. **Синхронне зниження стелі мікшера (Collective Derating):** Якщо перегрівається один мотор або регулятор на чотиримоторній платформі, коефіцієнт тротлінгу застосовується до загальної шини газу (Throttle Base), зберігаючи при цьому симетричний диференційний запас для кутової стабілізації;
2. **Anti-Windup тригер:** Коли `throttle_scale < 1.0`, інтегратор осі, яка впирається в обмеження, заморожується від подальшого накопичення помилки;
3. **Калібрування теплових параметрів на стенді:** Теплоємності `C_wind` та базовий тепловий опір `R_th_core_air_base` визначаються експериментально на динамометричному стенді шляхом подачі східчастого імпульсу струму (Step Response) та вимірювання кривої охолодження тепловізором або контактною термопарою.

## Інженерні пастки при розробці прошивки

1. **Втрата пакетів телеметрії DShot або UART:** Якщо через високовольтні імпульсні перешкоди від комутації фаз збивається контрольна сума кадру телеметрії, обробник не повинен скидати виміряну температуру в нуль або кімнатну температуру — це призведе до миттєвого вимкнення захисту й різкого стрибка газу. Прошивка повинна утримувати останнє достовірне значення впродовж 1.0–2.0 секунд (Hold Last Valid State), а в разі тривалого збою переходити в консервативний безпечний режим;
2. **Різкий стрибок тяги (Throttle Jerk):** Ступінчасте зменшення скважності газу на 30–50% за один цикл (1–2 мс) призводить до втрати висоти та різкого зриву стабілізації. Використання обмежувача темпу наростання (*rate limiter*) на рівні 30–50%/с гарантує плавний перехід без створення аварійної ситуації;
3. **Теплова інерція датчика NTC:** NTC-термістор на платі ESC змонтований на деякій відстані від кремнієвих кристалів MOSFET. Через тепловий опір текстоліту виміряна температура відстає від реальної температури переходу `T_j` на 1–3 секунди. Тому поріг початку тротлінгу `esc_temp_warn` завжди обирають із запасом (наприклад, 95 °C при граничній межі кристала 150 °C).
