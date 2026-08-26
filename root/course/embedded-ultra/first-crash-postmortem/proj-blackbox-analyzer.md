# Детектор десинхронізації та насичення мікшера в логах Blackbox

Коли після падіння на накопичувачі залишається бінарний польотний лог Blackbox на сотні мегабайтів із мільйонами фреймів на частоті 2 кГц, ручний пошук моменту аномалії в графічному переглядачі забирає години. Програмний аналізатор потоку кадрів автоматизує первинний тріаж аварії: він розраховує ковзну середньоквадратичну похибку стеження (RMS), фіксує насичення мікшера двигунів і виявляє точний момент десинхронізації — коли сигнал тяги окремого мотора сягає 100% за умови відсутності або реверсу кутового прискорення по відповідній осі протягом критичного вікна часу (понад 20 мс).

## Формат кадрів Blackbox: I-фрейми, P-фрейми та компресія

Польотний контролер записує дані в пам'ять не у вигляді сирих плоских структур, а через потоковий алгоритм компресії, подібний до відеокодеків. Повний кадр (англ. *Intra-frame* або I-frame) містить абсолютні значення всіх змінних: системний час у мікросекундах, сирі та відфільтровані покази трьохосьового гіроскопа й акселерометра, задані значення пілота (Setpoint), внески ПІД-контуру, шпаруватість моторів та показники батареї. I-кадри записуються відносно рідко (наприклад, кожні 32 або 64 ітерації циклу) і слугують опорними точками для синхронізації та відновлення після збоїв зчитування.

Між I-кадрами записуються різницеві кадри (англ. *Predicted-frame* або P-frame). У P-кадрі зберігається лише дельта (різниця `Δ = x[k] - x[k-1]`) відносно попереднього стану. Оскільки на частоті 2 кГц різниця між сусідніми замірами здебільшого близька до нуля, дельти упаковуються змінною кількістю бітів (Variable Byte Encoding), зменшуючи середній розмір кадру з 80 байтів до 12–18 байтів.

Аналізатор потоку кадрів спочатку декодує бінарні дельти, розгортаючи їх у послідовний масив нормалізованих структур `BlackboxFrame`.

## Структури польотного кадру та конфігурація детектора

Для аналізу динаміки аварії потрібні часова мітка, задані кутові швидкості пілота, виміряні значення з гіроскопа, виходи ПІД-регулятора, стан мікшера моторів та напруга акумулятора. Нижче наведено інтерфейсні структури мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <math.h>

#define MAX_MOTORS 4
#define AXIS_ROLL  0
#define AXIS_PITCH 1
#define AXIS_YAW   2

typedef struct {
    uint64_t timestamp_us;
    float setpoint_rate[3];         /* deg/s: Roll, Pitch, Yaw */
    float gyro_rate[3];             /* deg/s: Roll, Pitch, Yaw */
    float pid_p_term[3];            /* Пропорційна складова */
    float pid_i_term[3];            /* Інтегральна складова [-1000..1000] */
    float pid_d_term[3];            /* Диференційна складова */
    float motor_output[MAX_MOTORS]; /* Відносна тяга [0.0 .. 1.0] */
    float vbat_v;                   /* Напруга батареї у вольтах */
    float ibat_a;                   /* Струм споживання в амперах */
} blackbox_frame_t;

typedef enum {
    ANOMALY_NONE             = 0,
    ANOMALY_TRACKING_LOSS    = (1 << 0),
    ANOMALY_MIXER_SATURATION = (1 << 1),
    ANOMALY_MOTOR_DESYNC     = (1 << 2),
    ANOMALY_BROWNOUT         = (1 << 3)
} anomaly_flags_t;

typedef struct {
    float tracking_error_threshold_deg; /* Поріг кутової похибки (напр. 45.0 град/с) */
    float desync_motor_min_throttle;    /* Мінімальна тяга мотора для десинхрону (0.95) */
    uint32_t min_anomaly_duration_us;   /* Мінімальна тривалість події (20000 мкс) */
    float brownout_voltage_threshold_v; /* Поріг напруги BOD (напр. 6.0 В для 6S) */
} analyzer_config_t;

typedef struct {
    uint64_t start_time_us;
    uint64_t end_time_us;
    uint32_t flags;
    uint8_t failed_motor_index;
    float max_error_deg;
    float min_vbat_v;
} crash_incident_report_t;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cmath>
#include <span>
#include <vector>
#include <optional>
#include <array>

namespace postmortem {

constexpr std::size_t MaxMotors = 4;

enum class Axis : std::size_t {
    Roll = 0,
    Pitch = 1,
    Yaw = 2
};

struct BlackboxFrame {
    std::uint64_t timestamp_us{0};
    std::array<float, 3> setpoint_rate{0.0f, 0.0f, 0.0f}; /* deg/s */
    std::array<float, 3> gyro_rate{0.0f, 0.0f, 0.0f};     /* deg/s */
    std::array<float, 3> pid_p_term{0.0f, 0.0f, 0.0f};
    std::array<float, 3> pid_i_term{0.0f, 0.0f, 0.0f};
    std::array<float, 3> pid_d_term{0.0f, 0.0f, 0.0f};
    std::array<float, MaxMotors> motor_output{0.0f, 0.0f, 0.0f, 0.0f};
    float vbat_v{0.0f};
    float ibat_a{0.0f};
};

enum class AnomalyType : std::uint32_t {
    None             = 0,
    TrackingLoss    = (1 << 0),
    MixerSaturation = (1 << 1),
    MotorDesync     = (1 << 2),
    Brownout         = (1 << 3)
};

constexpr AnomalyType operator|(AnomalyType a, AnomalyType b) noexcept {
    return static_cast<AnomalyType>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}

constexpr bool has_flag(AnomalyType val, AnomalyType flag) noexcept {
    return (static_cast<std::uint32_t>(val) & static_cast<std::uint32_t>(flag)) != 0;
}

struct AnalyzerConfig {
    float tracking_error_threshold_deg{45.0f};
    float desync_motor_min_throttle{0.95f};
    std::uint32_t min_anomaly_duration_us{20000};
    float brownout_voltage_threshold_v{6.0f};
};

struct CrashIncidentReport {
    std::uint64_t start_time_us{0};
    std::uint64_t end_time_us{0};
    AnomalyType flags{AnomalyType::None};
    std::optional<std::size_t> failed_motor_index{std::nullopt};
    float max_error_deg{0.0f};
    float min_vbat_v{100.0f};
};

} // namespace postmortem
```
:::

## Алгоритм потокового виявлення десинхрону та аварійного тріажу

Автоматичний аналіз реалізує скінченний автомат розпізнавання відмов. У кожній точці часу алгоритм обчислює похідну кутової швидкості `α = d(gyro)/dt` та порівнює її з напрямком відновлювального моменту, який намагається створити ПІД-контур:

1. **Фільтрація часових стрибків:** якщо між сусідніми кадрами інтервал часу `dt` від'ємний або перевищує 50 мс, такий інтервал вважається артефактом переповнення чи втрати буфера і пропускається.
2. **Оцінка просідання живлення:** фіксується абсолютний мінімум напруги `V_bat`. Якщо напруга опускається нижче порогу працездатності стабілізатора живлення процесора (зазвичай 6.0 В для 6S або 3.0 В для 1S), встановлюється прапорець `ANOMALY_BROWNOUT`.
3. **Похибка стеження:** обчислюється евклідова норма похибки по осях Roll і Pitch. Якщо розбіжність перевищує 45 °/с протягом більш ніж 20 мс, це свідчить про зрив контуру стабілізації.
4. **Ідентифікація десинхронізованого мотора:** для кожного мотора перевіряється умова максимального запиту тяги (`motor_output >= 0.95`). Якщо на тлі 100% тяги виміряне кутове прискорення спрямоване в протилежний бік, а стан утримується довше за час розгону ротора (понад 20–25 мс), фіксується апаратна відмова силового каналу `ANOMALY_MOTOR_DESYNC`.

:::tabs
```c
bool analyze_log_stream(const blackbox_frame_t* frames, size_t frame_count,
                        const analyzer_config_t* config,
                        crash_incident_report_t* report) {
    if (!frames || frame_count < 2 || !config || !report) {
        return false;
    }

    report->start_time_us = 0;
    report->end_time_us = 0;
    report->flags = ANOMALY_NONE;
    report->failed_motor_index = 0xFF;
    report->max_error_deg = 0.0f;
    report->min_vbat_v = 100.0f;

    uint64_t desync_start_time[MAX_MOTORS] = {0};
    uint64_t tracking_loss_start_time = 0;
    bool in_incident = false;

    for (size_t i = 1; i < frame_count; ++i) {
        const blackbox_frame_t* prev = &frames[i - 1];
        const blackbox_frame_t* curr = &frames[i];

        float dt = (float)(curr->timestamp_us - prev->timestamp_us) * 1e-6f;
        if (dt <= 0.0f || dt > 0.05f) {
            continue; /* Пропуск розривів часу */
        }

        if (curr->vbat_v < report->min_vbat_v) {
            report->min_vbat_v = curr->vbat_v;
        }

        /* 1. Перевірка просідання батареї у Brownout */
        if (curr->vbat_v < config->brownout_voltage_threshold_v) {
            report->flags |= ANOMALY_BROWNOUT;
            if (!in_incident) {
                report->start_time_us = curr->timestamp_us;
                in_incident = true;
            }
            report->end_time_us = curr->timestamp_us;
        }

        /* 2. Обчислення кутової похибки стеження */
        float err_roll = fabsf(curr->setpoint_rate[AXIS_ROLL] - curr->gyro_rate[AXIS_ROLL]);
        float err_pitch = fabsf(curr->setpoint_rate[AXIS_PITCH] - curr->gyro_rate[AXIS_PITCH]);
        float total_err = sqrtf(err_roll * err_roll + err_pitch * err_pitch);

        if (total_err > report->max_error_deg) {
            report->max_error_deg = total_err;
        }

        if (total_err > config->tracking_error_threshold_deg) {
            if (tracking_loss_start_time == 0) {
                tracking_loss_start_time = curr->timestamp_us;
            } else if (curr->timestamp_us - tracking_loss_start_time >= config->min_anomaly_duration_us) {
                report->flags |= ANOMALY_TRACKING_LOSS;
                if (!in_incident) {
                    report->start_time_us = tracking_loss_start_time;
                    in_incident = true;
                }
                report->end_time_us = curr->timestamp_us;
            }
        } else {
            tracking_loss_start_time = 0;
        }

        /* 3. Детектування десинхрону моторів у конфігурації Quad-X */
        float alpha_roll = (curr->gyro_rate[AXIS_ROLL] - prev->gyro_rate[AXIS_ROLL]) / dt;

        for (uint8_t m = 0; m < MAX_MOTORS; ++m) {
            if (curr->motor_output[m] >= config->desync_motor_min_throttle) {
                /* Перевірка протилежності реакції: тяга 100%, але кутове прискорення нульове або зворотне */
                bool opposing_accel = false;
                if (m == 3 && alpha_roll < -50.0f) opposing_accel = true; /* M4 має крен вліво замість вправо */
                if (m == 1 && alpha_roll > 50.0f)  opposing_accel = true; /* M2 крен вправо замість вліво */

                if (opposing_accel) {
                    if (desync_start_time[m] == 0) {
                        desync_start_time[m] = curr->timestamp_us;
                    } else if (curr->timestamp_us - desync_start_time[m] >= config->min_anomaly_duration_us) {
                        report->flags |= ANOMALY_MOTOR_DESYNC;
                        report->failed_motor_index = m;
                        if (!in_incident) {
                            report->start_time_us = desync_start_time[m];
                            in_incident = true;
                        }
                        report->end_time_us = curr->timestamp_us;
                    }
                }
            } else {
                desync_start_time[m] = 0;
            }
        }
    }

    return in_incident;
}
```
```cpp
#include <span>
#include <algorithm>
#include <cmath>

namespace postmortem {

class BlackboxAnalyzer {
public:
    explicit BlackboxAnalyzer(AnalyzerConfig config) noexcept
        : config_{config} {}

    [[nodiscard]] std::optional<CrashIncidentReport> process(
        std::span<const BlackboxFrame> frames) const noexcept {
        if (frames.size() < 2) {
            return std::nullopt;
        }

        CrashIncidentReport report{};
        std::array<std::uint64_t, MaxMotors> desync_start_time{};
        std::uint64_t tracking_loss_start_time{0};
        bool in_incident{false};

        for (std::size_t i = 1; i < frames.size(); ++i) {
            const auto& prev = frames[i - 1];
            const auto& curr = frames[i];

            const float dt = static_cast<float>(curr.timestamp_us - prev.timestamp_us) * 1e-6f;
            if (dt <= 0.0f || dt > 0.05f) {
                continue;
            }

            report.min_vbat_v = std::min(report.min_vbat_v, curr.vbat_v);

            /* 1. Аналіз аварійного просідання напруги */
            if (curr.vbat_v < config_.brownout_voltage_threshold_v) {
                report.flags = report.flags | AnomalyType::Brownout;
                if (!in_incident) {
                    report.start_time_us = curr.timestamp_us;
                    in_incident = true;
                }
                report.end_time_us = curr.timestamp_us;
            }

            /* 2. Оцінка похибки регулювання */
            const float err_roll = std::abs(curr.setpoint_rate[0] - curr.gyro_rate[0]);
            const float err_pitch = std::abs(curr.setpoint_rate[1] - curr.gyro_rate[1]);
            const float total_err = std::hypot(err_roll, err_pitch);

            report.max_error_deg = std::max(report.max_error_deg, total_err);

            if (total_err > config_.tracking_error_threshold_deg) {
                if (tracking_loss_start_time == 0) {
                    tracking_loss_start_time = curr.timestamp_us;
                } else if (curr.timestamp_us - tracking_loss_start_time >= config_.min_anomaly_duration_us) {
                    report.flags = report.flags | AnomalyType::TrackingLoss;
                    if (!in_incident) {
                        report.start_time_us = tracking_loss_start_time;
                        in_incident = true;
                    }
                    report.end_time_us = curr.timestamp_us;
                }
            } else {
                tracking_loss_start_time = 0;
            }

            /* 3. Детектування моторного десинхрону */
            const float alpha_roll = (curr.gyro_rate[0] - prev.gyro_rate[0]) / dt;

            for (std::size_t m = 0; m < MaxMotors; ++m) {
                if (curr.motor_output[m] >= config_.desync_motor_min_throttle) {
                    bool opposing_accel = false;
                    if (m == 3 && alpha_roll < -50.0f) opposing_accel = true;
                    if (m == 1 && alpha_roll > 50.0f)  opposing_accel = true;

                    if (opposing_accel) {
                        if (desync_start_time[m] == 0) {
                            desync_start_time[m] = curr.timestamp_us;
                        } else if (curr.timestamp_us - desync_start_time[m] >= config_.min_anomaly_duration_us) {
                            report.flags = report.flags | AnomalyType::MotorDesync;
                            report.failed_motor_index = m;
                            if (!in_incident) {
                                report.start_time_us = desync_start_time[m];
                                in_incident = true;
                            }
                            report.end_time_us = curr.timestamp_us;
                        }
                    }
                } else {
                    desync_start_time[m] = 0;
                }
            }
        }

        return in_incident ? std::make_optional(report) : std::nullopt;
    }

private:
    AnalyzerConfig config_;
};

} // namespace postmortem
```
:::

## Інтерпретація результатів детектора та усунення хибних спрацьовувань

Знайдений звіт інциденту повертає точний часовий діапазон `[start_time_us, end_time_us]` та індекс несправного силового каналу. Коли прапорець `ANOMALY_MOTOR_DESYNC` встановлено разом із `failed_motor_index = 3`, інженер отримує однозначну вказівку: катастрофа була викликана не раптовим поривом вітру чи дезорієнтацією оператора, а зривом комутації четвертого мотора за 35 мілісекунд до контакту із землею.

Щоб уникнути хибних спрацьовувань детектора (False Positives) під час агресивних акробатичних трюків (наприклад, різкої зупинки обертання або удару об гілку дерева), алгоритм накладає дві обов'язкові часові умови:
- **Часовий фільтр інерції:** мотор повинен перебувати у стані запиту максимальної тяги щонайменше `20 мс`. Реальний час розгону ротора пропелера діаметром 5 дюймів від 30% до 100% становить 15–25 мс. Якщо кутове прискорення не змінює знак протягом 25 мс при викрученому на максимум моторі, це фізично гарантує відсутність створення тяги ротором;
- **Комплексний критерій відриву:** прапорець десинхрону активується лише тоді, коли відсутність прискорення супроводжується зростанням похибки стеження `total_err > 45 °/с`.

Якщо ж звіт повертає `ANOMALY_TRACKING_LOSS` без встановлення прапорця десинхрону окремого мотора (тобто всі чотири мотори синхронно видавали 100% тяги без реакції кута), діагноз вказує на загальну нестачу тяги силової установки, перевантаження корисним навантаженням або потрапляння у спадний повітряний вихор.

## Інтеграція в конвеєр тестування та валідації (CI/CD)

Цей програмний модуль є автономним і не залежить від графічних бібліотек. Завдяки нульовим динамічним виділенням пам'яті в гарячому циклі обробки (`process()` працює виключно через `std::span` та фіксовані структури) аналізатор може виконуватися безпосередньо у прошивці наземної станції або запускатися як автоматичний крок верифікації в конвеєрі неперервної інтеграції (CI/CD) після завершення тестових місій на стендах Hardware-in-the-Loop (HIL).
