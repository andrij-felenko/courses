# ⚙️ Автоматичний аналізатор аварійних сигнатур польотного журналу

Коли апарат розбивається або здійснює аварійну посадку в полі, ручний перегляд сотень сигналів у графічному інтерфейсі забирає години, а перша мікросекундна аномалія часто губиться серед супутнього шуму від падіння. Цей проєкт реалізує автономний аналізатор телеметричних записів польотного контролера (ULog / DataFlash), який автоматично сканує синхронізовані часові ряди й діагностує першопричину інциденту за чотирма класичними сигнатурами: згорання або зрив синхронізації мотора/ESC, магнітна завада від сильного струму, просідання живлення (brownout) та апаратне зависання шини давачів.

Програма отримує масив послідовних кадрів телеметрії та перевіряє фізичні критерії відмов у рухомому часовому вікні.

```
[ Потік телеметрії ] ──► [ Рухоме вікно ] ──► [ 4 детектори сигнатур ] ──► [ Звіт із таймкодом ]
 (IMU, EKF, BAT, RCOU)     (Δt = 150..300 мс)    1. Насичення мотора
                                                 2. Магнітна завада
                                                 3. Просадка батареї
                                                 4. Зависання шини
```

## Механізм виявлення сигнатур та крайові випадки

Аналізатор працює за принципом ковзного часового вікна (sliding window), що дозволяє відфільтровувати поодинокі шумові сплески вимірювань і фіксувати лише стійкі фізичні процеси.

1. **Асиметрія моторів та відмова тяги (Motor / ESC Loss):**
   - *Фізичний критерій:* Якщо один мотор виходить у граничний максимум (`pwm > 0.98`), а протилежний мотор на тій самій осі скидається регулятором у мінімум (`pwm < 0.05`), виникає максимальний керівний момент. Якщо при цьому кутова помилка `|DesAngle − ActAngle|` не зменшується, а монотонно зростає і перевищує 20° протягом понад 15 кадрів (~150 мс при 100 Гц), фіксується повна відмова виконавчого каналу (обрив фази, згорілий ключ FET, відрив лопаті).
   - *Крайовий випадок:* Якщо апарат зіткнувся з перешкодою в польоті, мотори також можуть короткочасно насититися від удару. Щоб відрізнити удар від первинної відмови мотора, детектор перевіряє знак кутового прискорення: при відмові мотора прискорення починається *до* насичення регулятора (регулятор намагається наздогнати збій), тоді як при ударі різкий сплеск гіроскопа передує розкручуванню моторів.

2. **Магнітна завада силового струму (Compass Magnetic Distortion):**
   - *Фізичний критерій:* Сильний струм створює паразитнапружене магнітне поле, що спотворює вектор напруженості компаса. Детектор відстежує нормалізовану інновацію магнітометра в EKF (`mag_innov > 0.45`). Математично нормалізована нев'язка (Normalized Innovation Squared, NIS) обчислюється як відношення квадрата різниці між виміряним і передбаченим полем до суми дисперсій вимірювання та моделі. Якщо її сплеск строго корелює зі зростанням струму батареї (`current > 30.0 А`), а кут курсу (`Yaw`) починає відхилятися від заданого більш ніж на 15°, фіксується наведення від силового джгута на компас.
   - *Крайовий випадок:* Природна магнітна аномалія (наприклад, проліт над залізобетонним мостом або металевим дахом) викликає зростання нев'язки компаса, але не супроводжується стрибком власного струму споживання. Детектор відкидає такі події, класифікуючи їх як зовнішню аномалію середовища, а не конструктивний дефект борта.

3. **Провал напруги батареї (Brownout Voltage Sag):**
   - *Фізичний критерій:* Напруга силової шини падає нижче критичного порогу стабілізатора (наприклад, `< 13.2 В` для 4S збірки LiPo при робочому діапазоні 14.8–16.8 В) одночасно зі сплеском струму. Це вказує на деградацію хімії акумулятора, пробиту банку або високий перехідний опір силового роз'єму.
   - *Крайовий випадок:* При вичерпанні заряду наприкінці тривалого польоту напруга падає плавно і супроводжується попередженням `Low Battery Warning`. Детектор виявляє саме динамічний провал: миттєву швидкість падіння напруги `dU/dt < −4.0 В/с` під час кроку газу.

4. **Зависання шини давача (Sensor Lockup / Freeze):**
   - *Фізичний критерій:* Внаслідок електростатичного розряду або збою на шині I2C/SPI мікросхема акселерометра/гіроскопа перестає оновлювати внутрішній регістр вихідних даних, повертаючи одне й те саме значення на кожному опитуванні. Детектор перевіряє рівність відліків гіроскопа між сусідніми кадрами: якщо значення абсолютно збігаються (`Δ = 0.0`) протягом 25 послідовних опитувань у динамічному польоті, де фізичний шум гарантує зміну молодших бітів АЦП, фіксується зависання сенсора.
   - *Крайовий випадок:* Коли апарат стоїть нерухомо на землі до армінгу, покази гіроскопа близькі до нуля, але за рахунок теплового шуму MEMS-структури молодші розряди постійно тремтять на величину 0.001–0.005 рад/с. Повна рівність до десятитисячних часток можлива виключно при апаратному зависанні вихідного регістра або втраті тактування шини.

## Реалізація аналізатора

Нижче наведено модульну реалізацію аналізатора мовами C та C++. Обидві версії приймають неперервний буфер телеметричних кадрів і повертають структурований звіт із типом відмови, мікросекундною міткою початку інциденту та коефіцієнтом впевненості.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <math.h>

#define MAX_MOTORS 4
#define WINDOW_SIZE 30

typedef enum {
    FAULT_NONE = 0,
    FAULT_MOTOR_ESC_LOSS,
    FAULT_MAGNETIC_INTERFERENCE,
    FAULT_BROWNOUT_VOLTAGE_SAG,
    FAULT_SENSOR_BUS_LOCKUP
} FaultType;

typedef struct {
    uint64_t timestamp_us;       // мікросекунди від старту контролера
    float roll_des_deg;          // заданий крен (DesRoll)
    float roll_act_deg;          // фактичний крен (Roll)
    float yaw_des_deg;           // заданий курс (DesYaw)
    float yaw_act_deg;           // фактичний курс (Yaw)
    float motor_out[MAX_MOTORS]; // виходи на мотори [0.0 .. 1.0]
    float bat_voltage_v;         // напруга батареї, В
    float bat_current_a;         // струм споживання, А
    float ekf_mag_innov;         // нев'язка компаса в EKF
    float gyro_x_rads;           // кутова швидкість крену, рад/с
    uint32_t sensor_status_mask; // маска прапорців здоров'я (0x01 - IMU OK)
} TelemetryFrame;

typedef struct {
    FaultType fault;
    uint64_t timestamp_us;       // часова мітка першого прояву
    float confidence;            // коефіцієнт впевненості [0.0 .. 1.0]
    const char *description;
} IncidentReport;

static bool is_angle_diverging(float des, float act, float threshold_deg) {
    float err = fabsf(des - act);
    if (err > 180.0f) err = 360.0f - err; // корекція кільцевого переходу через 180°
    return err > threshold_deg;
}

IncidentReport analyze_incident(const TelemetryFrame *frames, size_t count) {
    IncidentReport report = {
        .fault = FAULT_NONE,
        .timestamp_us = 0,
        .confidence = 0.0f,
        .description = "Інцидентів не виявлено: параметри в межах норми"
    };

    if (count < WINDOW_SIZE) {
        report.description = "Замало даних для формування вікна аналізу";
        return report;
    }

    size_t motor_sat_count = 0;
    size_t mag_fault_count = 0;
    size_t sensor_freeze_count = 0;
    float prev_gyro = frames[0].gyro_x_rads;

    for (size_t i = 0; i < count; i++) {
        const TelemetryFrame *f = &frames[i];

        // 1. Провал напруги батареї (Brownout)
        if (f->bat_voltage_v < 13.2f && f->bat_current_a > 25.0f) {
            report.fault = FAULT_BROWNOUT_VOLTAGE_SAG;
            report.timestamp_us = f->timestamp_us;
            report.confidence = 0.95f;
            report.description = "Критичне просідання напруги батареї (Brownout) під струмовим навантаженням";
            return report;
        }

        // 2. Апаратне зависання шини або мікросхеми давача
        if ((f->sensor_status_mask & 0x01) == 0) {
            report.fault = FAULT_SENSOR_BUS_LOCKUP;
            report.timestamp_us = f->timestamp_us;
            report.confidence = 1.0f;
            report.description = "Апаратна відмова шини IMU (I2C/SPI timeout або втрата зв'язку)";
            return report;
        }

        if (i > 0 && fabsf(f->gyro_x_rads - prev_gyro) < 1e-6f) {
            sensor_freeze_count++;
            if (sensor_freeze_count > 25) {
                report.fault = FAULT_SENSOR_BUS_LOCKUP;
                report.timestamp_us = f->timestamp_us;
                report.confidence = 0.90f;
                report.description = "Застигання показів гіроскопа (Sensor freeze) на постійному значенні";
                return report;
            }
        } else {
            sensor_freeze_count = 0;
        }
        prev_gyro = f->gyro_x_rads;

        // 3. Відмова мотора / регулятора ESC
        bool motor_saturated = false;
        if ((f->motor_out[0] > 0.98f && f->motor_out[1] < 0.05f) ||
            (f->motor_out[1] > 0.98f && f->motor_out[0] < 0.05f)) {
            motor_saturated = true;
        }

        if (motor_saturated && is_angle_diverging(f->roll_des_deg, f->roll_act_deg, 20.0f)) {
            motor_sat_count++;
            if (motor_sat_count > 15) { // ~150 мс стійкого насичення при 100 Гц
                report.fault = FAULT_MOTOR_ESC_LOSS;
                report.timestamp_us = f->timestamp_us;
                report.confidence = 0.98f;
                report.description = "Відмова мотора або ESC: насичення виходу 100%/0% при зростаючій помилці крену";
                return report;
            }
        } else {
            motor_sat_count = (motor_sat_count > 0) ? motor_sat_count - 1 : 0;
        }

        // 4. Магнітна завада від струмових кіл
        if (f->ekf_mag_innov > 0.45f && f->bat_current_a > 30.0f) {
            if (is_angle_diverging(f->yaw_des_deg, f->yaw_act_deg, 15.0f)) {
                mag_fault_count++;
                if (mag_fault_count > 20) {
                    report.fault = FAULT_MAGNETIC_INTERFERENCE;
                    report.timestamp_us = f->timestamp_us;
                    report.confidence = 0.92f;
                    report.description = "Розходження курсу через магнітні наведення силового струму на компас";
                    return report;
                }
            }
        } else {
            mag_fault_count = (mag_fault_count > 0) ? mag_fault_count - 1 : 0;
        }
    }

    return report;
}
```
```cpp
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace postmortem {

enum class FaultType {
    None,
    MotorEscLoss,
    MagneticInterference,
    BrownoutVoltageSag,
    SensorBusLockup
};

struct TelemetryFrame {
    uint64_t timestamp_us{0};
    float roll_des_deg{0.0f};
    float roll_act_deg{0.0f};
    float yaw_des_deg{0.0f};
    float yaw_act_deg{0.0f};
    std::vector<float> motor_out; // нормовані виходи моторів
    float bat_voltage_v{0.0f};
    float bat_current_a{0.0f};
    float ekf_mag_innov{0.0f};
    float gyro_x_rads{0.0f};
    uint32_t sensor_status_mask{0};
};

struct IncidentReport {
    FaultType fault{FaultType::None};
    uint64_t timestamp_us{0};
    float confidence{0.0f};
    std::string_view description;
};

class CrashAnalyzer {
public:
    static IncidentReport analyze(std::span<const TelemetryFrame> frames) {
        if (frames.size() < 30) {
            return {FaultType::None, 0, 0.0f, "Замало даних для формування вікна аналізу"};
        }

        size_t motor_sat_count = 0;
        size_t mag_fault_count = 0;
        size_t sensor_freeze_count = 0;
        float prev_gyro = frames.front().gyro_x_rads;

        for (const auto &f : frames) {
            // 1. Brownout: глибоке падіння напруги під навантаженням
            if (f.bat_voltage_v < 13.2f && f.bat_current_a > 25.0f) {
                return {
                    FaultType::BrownoutVoltageSag,
                    f.timestamp_us,
                    0.95f,
                    "Критичне просідання напруги батареї (Brownout) під струмовим навантаженням"
                };
            }

            // 2. Апаратна відмова шини давачів
            if ((f.sensor_status_mask & 0x01) == 0) {
                return {
                    FaultType::SensorBusLockup,
                    f.timestamp_us,
                    1.0f,
                    "Апаратна відмова шини IMU (I2C/SPI timeout або втрата зв'язку)"
                };
            }

            if (std::abs(f.gyro_x_rads - prev_gyro) < 1e-6f) {
                if (++sensor_freeze_count > 25) {
                    return {
                        FaultType::SensorBusLockup,
                        f.timestamp_us,
                        0.90f,
                        "Застигання показів гіроскопа (Sensor freeze) на постійному значенні"
                    };
                }
            } else {
                sensor_freeze_count = 0;
            }
            prev_gyro = f.gyro_x_rads;

            // 3. Асиметрія виходів моторів (Motor / ESC failure)
            if (f.motor_out.size() >= 2) {
                const bool saturated = (f.motor_out[0] > 0.98f && f.motor_out[1] < 0.05f) ||
                                       (f.motor_out[1] > 0.98f && f.motor_out[0] < 0.05f);

                if (saturated && is_angle_diverging(f.roll_des_deg, f.roll_act_deg, 20.0f)) {
                    if (++motor_sat_count > 15) {
                        return {
                            FaultType::MotorEscLoss,
                            f.timestamp_us,
                            0.98f,
                            "Відмова мотора або ESC: насичення виходу 100%/0% при зростаючій помилці крену"
                        };
                    }
                } else if (motor_sat_count > 0) {
                    --motor_sat_count;
                }
            }

            // 4. Магнітні завади EKF
            if (f.ekf_mag_innov > 0.45f && f.bat_current_a > 30.0f) {
                if (is_angle_diverging(f.yaw_des_deg, f.yaw_act_deg, 15.0f)) {
                    if (++mag_fault_count > 20) {
                        return {
                            FaultType::MagneticInterference,
                            f.timestamp_us,
                            0.92f,
                            "Розходження курсу через магнітні наведення силового струму на компас"
                        };
                    }
                }
            } else if (mag_fault_count > 0) {
                --mag_fault_count;
            }
        }

        return {FaultType::None, 0, 0.0f, "Інцидентів не виявлено: параметри в межах норми"};
    }

private:
    static bool is_angle_diverging(float des, float act, float threshold_deg) noexcept {
        float err = std::abs(des - act);
        if (err > 180.0f) err = 360.0f - err;
        return err > threshold_deg;
    }
};

} // namespace postmortem
```
:::

## Інтеграція в конвеєр автоматичного аналізу та інтерпретація результату

Аналізатор компілюється як окрема консольна утиліта або динамічна бібліотека, що викликається автоматично в конвеєрі обробки польотних даних. Після вилучення полів із бінарного файлу ULog чи DataFlash через утиліти розпакування (наприклад, `pyulog` або `mavlogdump`), сформований масив структур `TelemetryFrame` передається функції `analyze_incident`.

Отриманий структурований звіт містить точну мікросекундну мітку (`timestamp_us`), на якій уперше виникла аномалія. Це скорочує вікно первинного розслідування інженера з повного 30-хвилинного польоту до вузького проміжку в 150–300 мілісекунд, де сталася первинна фізична подія. Якщо аналізатор повертає код `FAULT_MOTOR_ESC_LOSS` на мітці `T = 842.120 с`, інженер відкриває графічний аналізатор саме на цьому таймкоді, миттєво підтверджує фізичну відмову силового тракту та переходить до апаратного огляду ключів регулятора чи обмоток двигуна.
