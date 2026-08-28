# ⚙️ Автоматичний передпольотний чекер: валідація телеметрії та безпекових блокувань

У польотних випробуваннях людська увага перед стартом неминуче розсіюється: шум гвинтів, перевірка радіозв'язку, хвилювання та поспіх часто призводять до того, що оператори забувають активувати геозону, не помічають просідання напруги одного осередку акумулятора або ігнорують підвищений рівень вібраційного шуму в оцінювачі стану. Автоматичний передпольотний чекер (англ. *pre-flight validator*) — це автономна програмна перевірка, яка безпосередньо перед надсиланням команди озброєння моторів (`ARM`) опитує телеметричні потоки автопілота, зіставляє стан сенсорів і конфігурації безпеки із заздалегідь визначеними граничними допусками та видає однозначний бінарний вердикт «GO» (дозвіл на зліт) або «NO-GO» (блокування старту із зазначенням конкретної причини).

Програмний валідатор виключає людський фактор і автоматизує контроль шести критичних контурів безпеки планера перед кожним включенням двигунів.

## Шість бар'єрів передпольотної верифікації

Розглянемо фізичну та алгоритмічну суть кожного параметричного бар'єра, який перевіряє модуль.

### 1. Якість супутникового позиціонування (GNSS/GPS)

Наявність базового супутникового захоплення (англ. *3D Fix*) не гарантує безпеки автономного польоту. За умов низького стояння супутників над горизонтом або наявності радіозавад геометричний фактор зниження точності (англ. *Horizontal Dilution of Precision*, скорочено HDOP) може досягати значень 2.5–4.0. Це означає, що реальна горизонтальна похибка визначення координат становить 5–10 метрів, що неприпустимо для старту в обмеженому коридорі. Валідатор вимагає комбінації трьох умов:
- тип навігаційного рішення `gps_fix_type >= 3` (повноцінний 3D-Fix або вище: DGPS, RTK);
- кількість активних супутників у рішенні `gps_satellites >= 12`;
- горизонтальний фактор розмиття точності `gps_hdop <= 1.20`.

### 2. Узгодженість розширеного фільтра Калмана (EKF Innovations)

Розширений фільтр Калмана (EKF) об'єднує високочастотні дані інерціальних датчиків (гіроскопів та акселерометрів) із низькочастотними вимірюваннями GPS, компаса та барометра. У кожному такті фільтр обчислює інновацію (англ. *innovation* — вектор нев'язки між прогнозом стану та новим вимірюванням датчика). Якщо сенсор забруднений шумом або компас зазнає впливу магнітних мас, нормована похибка інновації (англ. *innovation test ratio*) починає різко зростати. Валідатор перевіряє, щоб статичне розходження за вектором положення, швидкості та магнітного курсу не перевищувало порога `0.30`. Перевищення цього рівня свідчить про наявність прихованого дрейфу ще до зльоту.

### 3. Внутрішній опір та перекіс осередків акумулятора

Загальна напруга акумулятора під час простою на землі може здаватися достатньою (наприклад, 15.2 В для 4S LiPo), але наявність одного деградованого осередку з підвищеним внутрішнім опором призведе до катастрофічного просідання напруги під час різкої дачі газу на зльоті. Валідатор зіставляє загальну напругу силової шини (`battery_voltage >= 14.8 В`), перевіряє максимальний перекіс між окремими банками (`cell_delta_v <= 0.05 В`) та контролює температуру акумулятора (`battery_temp_c >= 5.0 °C`), запобігаючи використанню переморожених батарей із заблокованою електрохімією.

### 4. Цілісність та активація жорсткої геозони (Geofence)

Поширена помилка польотних груп — завантаження полігону місії без фактичної активації прапорця примусового контролю меж у параметрах автопілота. Валідатор перевіряє:
- системний прапорець `geofence_enabled == true`;
- кількість завантажених вершин полігону `geofence_points >= 4` (замкнений тривимірний контур безпеки);
- наявність налаштованої дії при порушенні межі `geofence_action >= 1` (RTL або автоматична керована посадка).

### 5. Апаратний канал перехоплення та Kill Switch

Перед стартом критично перевірити, чи знаходиться тумблер аварійного вимкнення двигунів у безпечному положенні готовності (ШІМ 1000 мкс), а також оцінити запас потужності сигналу радіокерування на місці стоянки (`rc_rssi_dbm >= -85 дБм`). Якщо рівень зв'язку на старті вже близький до межі чутливості приймача, виліт категорично блокується через загрозу втрати контролю над апаратом на перших метрах віддалення.

### 6. Фоновий вібраційний шум та кліпінг акселерометрів

У статичному положенні на землі (до розкрутки пропелерів) вібраційний шум акселерометра не повинен перевищувати `0.40 м/с²`. Якщо цей поріг перевищено при вимкнених двигунах, це вказує на механічний люфт плати польотного контролера, перетискання демпферів кріплення сигнальними проводами або вплив сильного поривчастого вітру на планер.

## Програмна реалізація діагностичного модуля

Нижче наведено повнофункціональну реалізацію чекера мовами C та C++. Обидві версії приймають телеметричний зліпок стану борту, проводять побітову валідацію за встановленими безпековими допусками та повертають структурований діагностичний звіт із деталізацією всіх виявлених дефектів.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_REASONS 8
#define REASON_BUF_LEN 96

/* Побітові прапорці критичних підсистем безпеки */
typedef enum {
    CHECK_GPS_FIX_OK       = (1 << 0),
    CHECK_EKF_HEALTHY      = (1 << 1),
    CHECK_BATTERY_OK       = (1 << 2),
    CHECK_GEOFENCE_ACTIVE  = (1 << 3),
    CHECK_RC_KILLSWITCH_OK = (1 << 4),
    CHECK_VIBRATION_OK     = (1 << 5)
} PreflightCheckMask;

/* Телеметричні параметри, зчитані з борту перед армінгом */
typedef struct {
    uint8_t  gps_fix_type;      /* 3 = 3D Fix, 4 = DGPS, 5 = RTK Float, 6 = RTK Fixed */
    uint8_t  gps_satellites;    /* Кількість захоплених супутників */
    float    gps_hdop;          /* Horizontal Dilution of Precision */
    
    float    ekf_pos_innov;     /* Нормована похибка інновації позиції EKF (0.0 .. 1.0) */
    float    ekf_vel_innov;     /* Нормована похибка інновації швидкості EKF */
    float    ekf_yaw_innov;     /* Нормована похибка інновації курсу EKF */
    
    float    battery_voltage;   /* Загальна напруга силового акумулятора (В) */
    float    cell_delta_v;      /* Максимальна різниця напруг між осередками (В) */
    float    battery_temp_c;    /* Температура акумулятора (°C) */
    
    bool     geofence_enabled;  /* Чи активована жорстка геозона в параметрах */
    uint16_t geofence_points;   /* Кількість завантажених точок межі полігону */
    uint8_t  geofence_action;   /* 1 = RTL, 2 = Land, 3 = Terminate */
    
    int16_t  rc_rssi_dbm;       /* Рівень сигналу пульта керування (дБм) */
    uint16_t rc_kill_channel;   /* Значення ШІМ аварійного каналу (1000..2000 мкс) */
    
    float    acc_vibe_floor;    /* Фонова амплітуда шуму акселерометра в спокої (м/с²) */
} VehicleTelemetryState;

/* Результат передпольотної діагностики */
typedef struct {
    bool     is_go;             /* Загальний дозвіл на виліт (true = GO, false = NO-GO) */
    uint32_t passed_mask;       /* Маска успішно пройдених перевірок */
    uint8_t  failure_count;     /* Кількість виявлених дефектів */
    char     reasons[MAX_REASONS][REASON_BUF_LEN]; /* Текстові пояснення відхилень */
} PreflightReport;

static void add_failure(PreflightReport *rep, const char *msg) {
    if (rep->failure_count < MAX_REASONS) {
        strncpy(rep->reasons[rep->failure_count], msg, REASON_BUF_LEN - 1);
        rep->reasons[rep->failure_count][REASON_BUF_LEN - 1] = '\0';
        rep->failure_count++;
    }
    rep->is_go = false;
}

PreflightReport run_preflight_validation(const VehicleTelemetryState *telemetry) {
    PreflightReport report;
    memset(&report, 0, sizeof(PreflightReport));
    report.is_go = true;

    /* 1. Перевірка навігаційної підсистеми GNSS */
    if (telemetry->gps_fix_type >= 3 && telemetry->gps_satellites >= 12 && telemetry->gps_hdop <= 1.20f) {
        report.passed_mask |= CHECK_GPS_FIX_OK;
    } else {
        add_failure(&report, "GNSS: Недостатня точність (вимагається 3D-Fix, sats >= 12, HDOP <= 1.20)");
    }

    /* 2. Перевірка здоров'я розширеного фільтра Калмана */
    if (telemetry->ekf_pos_innov < 0.30f && telemetry->ekf_vel_innov < 0.30f && telemetry->ekf_yaw_innov < 0.30f) {
        report.passed_mask |= CHECK_EKF_HEALTHY;
    } else {
        add_failure(&report, "EKF: Розходження інновацій перевищує поріг 0.30 (дрейф оцінки стану)");
    }

    /* 3. Перевірка живлення */
    if (telemetry->battery_voltage >= 14.8f && telemetry->cell_delta_v <= 0.05f &&
        telemetry->battery_temp_c >= 5.0f && telemetry->battery_temp_c <= 50.0f) {
        report.passed_mask |= CHECK_BATTERY_OK;
    } else {
        add_failure(&report, "BATTERY: Небезпечний рівень напруги, перекіс осередків > 0.05 В або мороз");
    }

    /* 4. Перевірка жорсткої геозони */
    if (telemetry->geofence_enabled && telemetry->geofence_points >= 4 && telemetry->geofence_action >= 1) {
        report.passed_mask |= CHECK_GEOFENCE_ACTIVE;
    } else {
        add_failure(&report, "GEOFENCE: Геозона не активована або містить менше 4 опорних точок");
    }

    /* 5. Перевірка каналу аварійного відключення (Kill Switch) */
    if (telemetry->rc_rssi_dbm >= -85 && telemetry->rc_kill_channel >= 980 && telemetry->rc_kill_channel <= 1050) {
        report.passed_mask |= CHECK_RC_KILLSWITCH_OK;
    } else {
        add_failure(&report, "SAFETY: Тумблер Kill Switch активований або зв'язок пульта слабкий (< -85 дБм)");
    }

    /* 6. Перевірка статичного шуму акселерометра */
    if (telemetry->acc_vibe_floor <= 0.40f) {
        report.passed_mask |= CHECK_VIBRATION_OK;
    } else {
        add_failure(&report, "IMU: Підвищений рівень фонових вібрацій (перевірити демпфери автопілота)");
    }

    return report;
}

void print_report(const PreflightReport *report) {
    if (report->is_go) {
        printf("==========================================\n");
        printf(">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ GO ] <<<\n");
        printf("Усі 6 систем безпеки валідовано. Дозвіл на ARM надано.\n");
        printf("==========================================\n");
    } else {
        printf("==========================================\n");
        printf(">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ NO-GO ] <<<\n");
        printf("Виявлено критичні блокування (%u відхилень):\n", report->failure_count);
        for (uint8_t i = 0; i < report->failure_count; i++) {
            printf("  [!] %s\n", report->reasons[i]);
        }
        printf("Старт категорично заборонено до усунення зауважень!\n");
        printf("==========================================\n");
    }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <cstdint>

enum class CheckFlag : uint32_t {
    GpsOk        = 1 << 0,
    EkfOk        = 1 << 1,
    BatteryOk    = 1 << 2,
    GeofenceOk   = 1 << 3,
    KillSwitchOk = 1 << 4,
    VibrationOk  = 1 << 5
};

struct TelemetrySnapshot {
    uint8_t     gps_fix_type{0};
    uint8_t     gps_satellites{0};
    float       gps_hdop{99.0f};

    float       ekf_pos_innov{1.0f};
    float       ekf_vel_innov{1.0f};
    float       ekf_yaw_innov{1.0f};

    float       battery_voltage{0.0f};
    float       cell_delta_v{0.0f};
    float       battery_temp_c{0.0f};

    bool        geofence_enabled{false};
    uint16_t    geofence_points{0};
    uint8_t     geofence_action{0};

    int16_t     rc_rssi_dbm{-120};
    uint16_t    rc_kill_channel{0};

    float       acc_vibe_floor{0.0f};
};

struct PreflightResult {
    bool                     is_go{true};
    uint32_t                 passed_mask{0};
    std::vector<std::string> failures;

    void add_failure(std::string_view reason) {
        failures.emplace_back(reason);
        is_go = false;
    }
};

class PreflightValidator {
public:
    static PreflightResult evaluate(const TelemetrySnapshot& state) {
        PreflightResult result;

        // 1. Валідація GNSS
        if (state.gps_fix_type >= 3 && state.gps_satellites >= 12 && state.gps_hdop <= 1.20f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::GpsOk);
        } else {
            result.add_failure("GNSS: Недостатня точність (вимагається 3D-Fix, sats >= 12, HDOP <= 1.20)");
        }

        // 2. Валідація фільтра Калмана (EKF)
        if (state.ekf_pos_innov < 0.30f && state.ekf_vel_innov < 0.30f && state.ekf_yaw_innov < 0.30f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::EkfOk);
        } else {
            result.add_failure("EKF: Розходження інновацій перевищує поріг 0.30 (дрейф оцінки стану)");
        }

        // 3. Валідація акумулятора
        if (state.battery_voltage >= 14.8f && state.cell_delta_v <= 0.05f &&
            state.battery_temp_c >= 5.0f && state.battery_temp_c <= 50.0f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::BatteryOk);
        } else {
            result.add_failure("BATTERY: Небезпечний рівень напруги, перекіс осередків > 0.05 В або мороз");
        }

        // 4. Валідація жорсткої геозони
        if (state.geofence_enabled && state.geofence_points >= 4 && state.geofence_action >= 1) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::GeofenceOk);
        } else {
            result.add_failure("GEOFENCE: Геозона не активована або містить менше 4 опорних точок");
        }

        // 5. Валідація апаратного каналу перехоплення / Kill Switch
        if (state.rc_rssi_dbm >= -85 && state.rc_kill_channel >= 980 && state.rc_kill_channel <= 1050) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::KillSwitchOk);
        } else {
            result.add_failure("SAFETY: Тумблер Kill Switch активований або зв'язок пульта слабкий (< -85 дБм)");
        }

        // 6. Валідація фонового вібраційного шуму
        if (state.acc_vibe_floor <= 0.40f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::VibrationOk);
        } else {
            result.add_failure("IMU: Підвищений рівень фонових вібрацій (перевірити демпфери автопілота)");
        }

        return result;
    }
};

void print_diagnostic_report(const PreflightResult& report) {
    if (report.is_go) {
        std::cout << "==========================================\n"
                  << ">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ GO ] <<<\n"
                  << "Усі 6 систем безпеки валідовано. Дозвіл на ARM надано.\n"
                  << "==========================================\n";
    } else {
        std::cout << "==========================================\n"
                  << ">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ NO-GO ] <<<\n"
                  << "Виявлено критичні блокування (" << report.failures.size() << " відхилень):\n";
        for (const auto& reason : report.failures) {
            std::cout << "  [!] " << reason << "\n";
        }
        std::cout << "Старт категорично заборонено до усунення зауважень!\n"
                  << "==========================================\n";
    }
}
```
:::

## Порядок дій польотної групи при отриманні статусу NO-GO

Отримання статусу `NO-GO` є нормальною робочою подією польотного дня і не вважається зривом випробувань. Польотна група діє за стандартним діагностичним алгоритмом:

1. **Відхилення за EKF**: якщо чекер фіксує `ekf_yaw_innov > 0.30`, перевіряють відсутність поблизу апарата металевих предметів (автомобілів, залізобетонних плит, інструментів), які спотворюють магнітне поле компаса. Якщо перенесення дрона на чистий ґрунт не допомагає, виконують повторне калібрування компаса. Також очікують 60–90 секунд для досягнення стаціонарного температурного режиму кристалів гіроскопів.
2. **Відхилення за GNSS**: при значенні `HDOP > 1.20` або кількості супутників `< 12` забороняється форсувати старт. Необхідно зачекати 2–3 хвилини для завантаження свіжого альманаху супутників або перевірити, чи не екранується антена GNSS елементами конструкції чи корисним навантаженням.
3. **Відхилення за акумулятором**: при перекосі напруги `cell_delta_v > 0.05 В` акумулятор негайно вилучається з експлуатації та відправляється на балансувальний заряд або утилізацію. Підключення іншого, свіжозарядженого силового акумулятора є обов'язковим.
4. **Відхилення за рівнем сигналу RC**: якщо `rc_rssi_dbm < -85 дБм` на відстані кількох метрів від пілота, перевіряють цілісність коаксіальних кабелів антен на передавачі та бортовому приймачі, а також виключають взаємне затінення антен вуглепластиковими деталями.

Після усунення виявлених дефектів валідатор запускається повторно. Лише отримання однозначного звіту зі статусом `GO` дає право оператору GCS запросити дозвіл на армінг у страхувального пілота.
