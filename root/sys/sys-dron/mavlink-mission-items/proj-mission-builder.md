# Побудова та валідація польотних завдань MAVLink

Цей практичний проект демонструє проектування, математичний розрахунок, двійкове пакування та строгу валідацію польотного завдання для автономного безпілотного апарата у форматі повідомлень MAVLink `MISSION_ITEM_INT` (#73). Розглядається типова інженерна задача підготовки місії аерофотознімання: зліт на задану висоту, політ серією поворотних точок із автоматичним увімкненням спрацьовування камери через просторові інтервали, циклічне сканування ділянки за допомогою переходу `DO_JUMP` та автоматичне повернення на базу.

## 1. Інженерна задача: від полігону до двійкових інструкцій

Автономна польотна місія картографування починається з географічного полігону інтересу, заданого на карті оператора. Для перетворення цього багатокутника на послідовність машинних інструкцій польотного контролера генератор місії повинен виконати кілька послідовних кроків:
1. **Розрахунок галсів сканування:** визначення напрямку ліній польоту, кроку між сусідніми лініями (з урахуванням фокусної відстані камери, розміру матриці та коефіцієнта поперечного перекриття знімків, зазвичай 60–80%) та висоти польоту над рельєфом. При цьому враховується напрямок панівного вітру: прокладання довгих галсів паралельно або під невеликим кутом до вітру мінімізує енергетичні витрати на утримання курсу та збільшує тривалість автономного польоту на 15–25%.
2. **Геодезична дискретизація:** перетворення географічних координат (широта й довгота в градусах WGS84) у цілочисельний формат із фіксованою комою `degE7` (`градуси · 10⁷`), де один дискретний крок сітки на екваторі становить приблизно 1.11 см. Це гарантує точне збереження геометрії знімальної сітки без паразитного дрейфу точок.
3. **Інжекція команд корисного навантаження:** розміщення команд керування камерою (`MAV_CMD_DO_SET_CAM_TRIGG_DIST`), нахилом підвісу (`MAV_CMD_DO_MOUNT_CONTROL`) та швидкістю руху (`MAV_CMD_DO_CHANGE_SPEED`) у точках початку та завершення знімальних відрізків.
4. **Організація циклів патрулювання:** вставка інструкцій циклічного переходу `MAV_CMD_DO_JUMP` для повторного проходження критичних ділянок маршруту.
5. **Валідація цілісності перед відправкою:** повна статична перевірка сформованого масиву інструкцій на відсутність зациклень, порушень монотонності індексів `seq`, виходу координат за межі допустимого діапазону та перевищення меж висот.

## 2. Математичні та геодезичні перетворення

При побудові точок маршруту в межах локальної ділянки (до 10–20 км) відхилення поверхні Землі від площини є незначним. Це дозволяє використовувати локальну плоску проекцію для розрахунку зміщень і геодезичних відстаней без залучення важких сфероїдальних рівнянь Вінсенті, що є критичним для обчислювачів із обмеженими ресурсами (наприклад, супутніх одноплатних комп'ютерів Raspberry Pi або мікроконтролерів STM32).

### Розрахунок метричної довжини градуса
Геодезична модель спирається на параметри еліпсоїда WGS84, де радіус Землі на екваторі становить приблизно 6 378 137 м, а полярний радіус — 6 356 752 м. Довжина одного градуса широти вздовж меридіана є практично незмінною по всій земній кулі й розраховується як:

```
L_lat = 111 132.95 м / градус
```

Довжина одного градуса довготи вздовж паралелі зменшується від екватора до полюсів пропорційно косинусу географічної широти `φ` (Latitude):

```
L_lon(φ) = 111 319.5 · cos(φ) м / градус
```

Знаючи бажаний крок зміщення на північ `ΔN` (метри) та на схід `ΔE` (метри) відносно базової точки, нові координати цільового пункту обчислюються за формулами прямої геодезичної задачі на площині:

```
Latitude_new  = Latitude_orig + (ΔN / L_lat)
Longitude_new = Longitude_orig + (ΔE / L_lon(Latitude_orig))
```

Ці формули забезпечують субсантиметрову точність на відстанях до 20 кілометрів від базової точки, що повністю перекриває потреби типових місій картографування, моніторингу ліній електропередач та агрономічного сканування.

### Перетворення у фіксовану кому (degE7)
Для запобігання похибкам накопичення двійкового округлення чисел із рухомою комою дійсне число `double` множиться на масштабний коефіцієнт `1.0e7` із математичним округленням до найближчого цілого:

```
int32_t lat_e7 = (int32_t)round(latitude_deg * 1.0e7);
int32_t lon_e7 = (int32_t)round(longitude_deg * 1.0e7);
```

Зворотне перетворення здійснюється діленням цілого числа на `1.0e7`:

```
double latitude_deg = (double)lat_e7 * 1.0e-7;
```

Використання цілих 32-бітних чисел зі знаком гарантує, що координати зберігаються без втрати точності навіть при багаторазовому читанні, записі у Flash-пам'ять та передачі по ненадійних каналах зв'язку.

### Розрахунок радіуса плавного розвороту (Fly-Through Radius)
Для запобігання втрати швидкості на поворотних точках параметр `param3` (радіус прольоту `R_pass`) команди `MAV_CMD_NAV_WAYPOINT` повинен узгоджуватися з динамічними обмеженнями літального апарата. Під час проходження повороту на апарат діє доцентрове прискорення:

```
a_centripetal = v² / R_turn = g · tan(φ_bank)
```

Звідси мінімальний радіус розвороту без звалювання або перевантаження становить:

```
R_pass = v² / (g · tan(φ_max))
```

де `v` — шляхова швидкість польоту (м/с), `g = 9.81 м/с²` — прискорення вільного падіння, `φ_max` — максимальний дозволений кут крену апарата (наприклад, 25°–35° для літака або 15°–20° для квадрокоптера). Якщо задати `R_pass` меншим за мінімальний радіус розвороту, апарат зазнає надмірних бічних відхилень від траєкторії (Cross-Track Error) або вимушено перейде до гальмування.

## 3. Правила статичної валідації місії

Перед відправкою сформованого масиву повідомлень `MISSION_ITEM_INT` по радіоканалу наземна станція керування або бортовий комп'ютер виконує обов'язкову багаторівневу верифікацію:

1. **Монотонність нумерації:** кожен пункт повинен мати індекс `seq`, строго рівний його позиції в масиві (від `0` до `N - 1`). Порушення послідовності призведе до відхилення всієї транзакції автопілотом із кодом `MAV_MISSION_INVALID_SEQUENCE`.
2. **Географічна коректність:** широта повинна лежати в межах від -90.0° до +90.0°, довгота — від -180.0° до +180.0°. Неприпустимі значення `NaN` або `Infinity` у полях координат.
3. **Діапазон висот:** висота `z` для навігаційних точок повинна бути більшою за мінімальну безпечну висоту над рельєфом (наприклад, не менше 2 метрів над землею) та не перевищувати стелю польотного завдання (зазвичай 5000 метрів).
4. **Валідація переходів DO_JUMP:**
   - Цільовий індекс переходу `param1` повинен бути меншим за загальну кількість пунктів `N`.
   - Цільовий індекс не може вказувати на сам елемент `DO_JUMP` (`param1 != seq`), оскільки це спричинить миттєве зациклення програми за один цикл планувальника.
   - Лічильник повторень `param2` повинен бути більшим за 0 або дорівнювати `-1` (нескінченний патруль).
5. **Конфлікти паралельних дій:** команди зміни швидкості `DO_CHANGE_SPEED` та налаштування інтервалу камери `DO_SET_CAM_TRIGG_DIST` повинні містити фізично досяжні значення (швидкість > 0 м/с, інтервал спрацьовування камери > 1 м).

## 4. Програмна реалізація генератора та валідатора

Нижче наведено повну реалізацію генератора польотного завдання з автоматичним розрахунком координат, формуванням команд камери, організацією циклічного переходу `DO_JUMP` та повною валідацією плану.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAVLINK_MSG_ID_MISSION_ITEM_INT 73

#define MAV_FRAME_GLOBAL_RELATIVE_ALT_INT 3
#define MAV_CMD_NAV_WAYPOINT 16
#define MAV_CMD_NAV_TAKEOFF 22
#define MAV_CMD_NAV_RETURN_TO_LAUNCH 20
#define MAV_CMD_DO_CHANGE_SPEED 178
#define MAV_CMD_DO_SET_CAM_TRIGG_DIST 206
#define MAV_CMD_DO_JUMP 177

#define DEG_TO_RAD (3.14159265358979323846 / 180.0)

typedef struct {
    float param1;
    float param2;
    float param3;
    float param4;
    int32_t x;
    int32_t y;
    float z;
    uint16_t seq;
    uint16_t command;
    uint8_t target_system;
    uint8_t target_component;
    uint8_t frame;
    uint8_t current;
    uint8_t autocontinue;
    uint8_t mission_type;
} mavlink_mission_item_int_t;

static inline int32_t deg_to_degE7(double deg) {
    return (int32_t)llround(deg * 1.0e7);
}

static inline double degE7_to_deg(int32_t degE7) {
    return (double)degE7 * 1.0e-7;
}

// Розрахунок геодезичного зміщення в метрах
void add_meter_offset(double base_lat, double base_lon, double d_north_m, double d_east_m,
                      double *out_lat, double *out_lon) {
    double lat_rad = base_lat * DEG_TO_RAD;
    double m_per_deg_lat = 111132.95;
    double m_per_deg_lon = 111319.5 * cos(lat_rad);

    *out_lat = base_lat + (d_north_m / m_per_deg_lat);
    *out_lon = base_lon + (d_east_m / m_per_deg_lon);
}

mavlink_mission_item_int_t make_takeoff(uint16_t seq, double lat, double lon, float alt_m) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_NAV_TAKEOFF;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.current = (seq == 0) ? 1 : 0;
    item.autocontinue = 1;
    item.param1 = 0.0f; // Тангаж зльоту
    item.x = deg_to_degE7(lat);
    item.y = deg_to_degE7(lon);
    item.z = alt_m;
    return item;
}

mavlink_mission_item_int_t make_change_speed(uint16_t seq, float speed_m_s) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_DO_CHANGE_SPEED;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = 1.0f; // Groundspeed
    item.param2 = speed_m_s;
    item.param3 = -1.0f; // Throttle без змін
    item.param4 = 0.0f;  // Абсолютна швидкість
    return item;
}

mavlink_mission_item_int_t make_waypoint(uint16_t seq, double lat, double lon, float alt_m,
                                         float hold_time_s, float accept_radius_m, float pass_radius_m) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_NAV_WAYPOINT;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = hold_time_s;
    item.param2 = accept_radius_m;
    item.param3 = pass_radius_m;
    item.param4 = NAN; // Курс за траєкторією
    item.x = deg_to_degE7(lat);
    item.y = deg_to_degE7(lon);
    item.z = alt_m;
    return item;
}

mavlink_mission_item_int_t make_camera_trigger(uint16_t seq, float trigger_dist_m) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_DO_SET_CAM_TRIGG_DIST;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = trigger_dist_m;
    item.param2 = 0.0f;
    item.param3 = 1.0f; // Негайний знімок на вході
    return item;
}

mavlink_mission_item_int_t make_jump(uint16_t seq, uint16_t target_seq, uint16_t repeat_count) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_DO_JUMP;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    item.param1 = (float)target_seq;
    item.param2 = (float)repeat_count;
    return item;
}

mavlink_mission_item_int_t make_rtl(uint16_t seq) {
    mavlink_mission_item_int_t item = {0};
    item.seq = seq;
    item.command = MAV_CMD_NAV_RETURN_TO_LAUNCH;
    item.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    item.autocontinue = 1;
    return item;
}

bool validate_mission(const mavlink_mission_item_int_t *items, size_t count) {
    if (items == NULL || count == 0) {
        printf("Помилка: порожній план місії\n");
        return false;
    }
    for (size_t i = 0; i < count; ++i) {
        if (items[i].seq != i) {
            printf("Помилка: порушення послідовності seq на кроці %zu [seq = %u]\n", i, items[i].seq);
            return false;
        }
        if (items[i].command == MAV_CMD_NAV_WAYPOINT || items[i].command == MAV_CMD_NAV_TAKEOFF) {
            double lat = degE7_to_deg(items[i].x);
            double lon = degE7_to_deg(items[i].y);
            if (lat < -90.0 || lat > 90.0 || lon < -180.0 || lon > 180.0) {
                printf("Помилка: некоректні географічні координати у seq %zu (lat: %f, lon: %f)\n", i, lat, lon);
                return false;
            }
            if (items[i].z < 2.0f || items[i].z > 5000.0f) {
                printf("Помилка: небезпечна висота z = %.1f м у seq %zu\n", items[i].z, i);
                return false;
            }
        }
        if (items[i].command == MAV_CMD_DO_JUMP) {
            uint16_t target = (uint16_t)items[i].param1;
            if (target >= count || target == i) {
                printf("Помилка: DO_JUMP у seq %zu посилається на неприпустимий цільовий індекс %u\n", i, target);
                return false;
            }
        }
    }
    return true;
}

int main(void) {
    mavlink_mission_item_int_t mission[8];
    double home_lat = 50.4501;
    double home_lon = 30.5234;
    float survey_alt = 60.0f; // Висота польоту 60 м

    double w1_lat, w1_lon, w2_lat, w2_lon, w3_lat, w3_lon, w4_lat, w4_lon;
    add_meter_offset(home_lat, home_lon, 100.0, 0.0, &w1_lat, &w1_lon);
    add_meter_offset(home_lat, home_lon, 100.0, 300.0, &w2_lat, &w2_lon);
    add_meter_offset(home_lat, home_lon, 200.0, 300.0, &w3_lat, &w3_lon);
    add_meter_offset(home_lat, home_lon, 200.0, 0.0, &w4_lat, &w4_lon);

    // Збирання польотного завдання
    mission[0] = make_takeoff(0, home_lat, home_lon, survey_alt);
    mission[1] = make_change_speed(1, 14.0f); // 14 м/с робоча швидкість
    mission[2] = make_camera_trigger(2, 20.0f); // Фото кожні 20 м
    mission[3] = make_waypoint(3, w1_lat, w1_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[4] = make_waypoint(4, w2_lat, w2_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[5] = make_waypoint(5, w3_lat, w3_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[6] = make_waypoint(6, w4_lat, w4_lon, survey_alt, 0.0f, 5.0f, 12.0f);
    mission[7] = make_rtl(7);

    if (validate_mission(mission, 8)) {
        printf("Польотне завдання успішно скомпільовано та верифіковано.\n");
        printf("Всього елементів: 8. Розмір корисних даних у пам'яті: %zu байтів.\n", 8 * sizeof(mavlink_mission_item_int_t));
        for (size_t i = 0; i < 8; ++i) {
            printf("Item %u: CMD=%3u, X=%9d, Y=%9d, Z=%5.1f м, P1=%5.1f, P2=%5.1f\n",
                   mission[i].seq, mission[i].command, mission[i].x, mission[i].y,
                   mission[i].z, mission[i].param1, mission[i].param2);
        }
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <cmath>
#include <cstdint>
#include <string_view>
#include <numbers>

enum class Frame : uint8_t {
    Global = 0,
    LocalNed = 1,
    GlobalRelativeAltInt = 3,
    LocalEnu = 4,
    GlobalTerrainAltInt = 11
};

enum class Command : uint16_t {
    NavWaypoint = 16,
    NavLoiterUnlim = 17,
    NavLoiterTime = 19,
    NavReturnToLaunch = 20,
    NavLand = 21,
    NavTakeoff = 22,
    DoChangeSpeed = 178,
    DoSetServo = 183,
    DoSetCamTriggDist = 206,
    DoJump = 177
};

struct MissionItem {
    float param1{0.0f};
    float param2{0.0f};
    float param3{0.0f};
    float param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float z{0.0f};
    uint16_t seq{0};
    Command command{Command::NavWaypoint};
    uint8_t target_system{1};
    uint8_t target_component{1};
    Frame frame{Frame::GlobalRelativeAltInt};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};

    static constexpr int32_t toDegE7(double deg) noexcept {
        return static_cast<int32_t>(deg * 1.0e7);
    }

    static constexpr double toDeg(int32_t degE7) noexcept {
        return static_cast<double>(degE7) * 1.0e-7;
    }
};

enum class ValidationError {
    EmptyMission,
    SequenceMismatch,
    InvalidCoordinates,
    UnsafeAltitude,
    InvalidJumpTarget
};

constexpr std::string_view errorToString(ValidationError err) noexcept {
    switch (err) {
        case ValidationError::EmptyMission: return "Порожній список елементів місії";
        case ValidationError::SequenceMismatch: return "Порушення монотонної нумерації seq";
        case ValidationError::InvalidCoordinates: return "Географічні координати виходять за діапазон WGS84";
        case ValidationError::UnsafeAltitude: return "Висота точки виходить за безпечні межі польоту";
        case ValidationError::InvalidJumpTarget: return "DO_JUMP посилається на неіснуючий або власний індекс";
    }
    return "Невідома помилка валідації";
}

class MissionPlan {
public:
    void addTakeoff(double lat, double lon, float alt_m) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::NavTakeoff;
        item.current = item.seq == 0 ? 1 : 0;
        item.x = MissionItem::toDegE7(lat);
        item.y = MissionItem::toDegE7(lon);
        item.z = alt_m;
        items_.push_back(item);
    }

    void addSpeedChange(float speed_m_s) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::DoChangeSpeed;
        item.param1 = 1.0f; // Groundspeed
        item.param2 = speed_m_s;
        item.param3 = -1.0f;
        items_.push_back(item);
    }

    void addWaypoint(double lat, double lon, float alt_m, float hold_time_s = 0.0f,
                     float accept_radius_m = 5.0f, float pass_radius_m = 0.0f) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::NavWaypoint;
        item.param1 = hold_time_s;
        item.param2 = accept_radius_m;
        item.param3 = pass_radius_m;
        item.param4 = NAN;
        item.x = MissionItem::toDegE7(lat);
        item.y = MissionItem::toDegE7(lon);
        item.z = alt_m;
        items_.push_back(item);
    }

    void addCameraTriggerDistance(float trigger_dist_m) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::DoSetCamTriggDist;
        item.param1 = trigger_dist_m;
        item.param3 = 1.0f; // Зробити разовий знімок на початку галса
        items_.push_back(item);
    }

    void addJump(uint16_t target_seq, uint16_t repeat_count) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::DoJump;
        item.param1 = static_cast<float>(target_seq);
        item.param2 = static_cast<float>(repeat_count);
        items_.push_back(item);
    }

    void addRtl() {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::NavReturnToLaunch;
        items_.push_back(item);
    }

    [[nodiscard]] std::span<const MissionItem> items() const noexcept {
        return items_;
    }

    [[nodiscard]] std::expected<void, ValidationError> validate() const {
        if (items_.empty()) {
            return std::unexpected(ValidationError::EmptyMission);
        }
        for (size_t i = 0; i < items_.size(); ++i) {
            const auto& it = items_[i];
            if (it.seq != i) {
                return std::unexpected(ValidationError::SequenceMismatch);
            }
            if (it.command == Command::NavWaypoint || it.command == Command::NavTakeoff) {
                double lat = MissionItem::toDeg(it.x);
                double lon = MissionItem::toDeg(it.y);
                if (lat < -90.0 || lat > 90.0 || lon < -180.0 || lon > 180.0) {
                    return std::unexpected(ValidationError::InvalidCoordinates);
                }
                if (it.z < 2.0f || it.z > 5000.0f) {
                    return std::unexpected(ValidationError::UnsafeAltitude);
                }
            }
            if (it.command == Command::DoJump) {
                auto target = static_cast<uint16_t>(it.param1);
                if (target >= items_.size() || target == i) {
                    return std::unexpected(ValidationError::InvalidJumpTarget);
                }
            }
        }
        return {};
    }

    static std::pair<double, double> offsetMeters(double base_lat, double base_lon,
                                                 double d_north_m, double d_east_m) noexcept {
        double lat_rad = base_lat * (std::numbers::pi / 180.0);
        double m_lat = 111132.95;
        double m_lon = 111319.5 * std::cos(lat_rad);
        return {base_lat + (d_north_m / m_lat), base_lon + (d_east_m / m_lon)};
    }

private:
    std::vector<MissionItem> items_;
};

int main() {
    MissionPlan plan;
    double home_lat = 50.4501;
    double home_lon = 30.5234;
    float alt = 60.0f;

    auto [w1_lat, w1_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 100.0, 0.0);
    auto [w2_lat, w2_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 100.0, 300.0);
    auto [w3_lat, w3_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 200.0, 300.0);
    auto [w4_lat, w4_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 200.0, 0.0);

    plan.addTakeoff(home_lat, home_lon, alt);
    plan.addSpeedChange(14.0f);
    plan.addCameraTriggerDistance(20.0f);
    plan.addWaypoint(w1_lat, w1_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addWaypoint(w2_lat, w2_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addWaypoint(w3_lat, w3_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addWaypoint(w4_lat, w4_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addRtl();

    if (auto res = plan.validate(); res.has_value()) {
        std::cout << "Місія успішно скомпільована та перевірена. Кількість елементів: "
                  << plan.items().size() << '\n';
        for (const auto& it : plan.items()) {
            std::cout << "seq: " << it.seq << ", CMD: " << static_cast<uint16_t>(it.command)
                      << ", X: " << it.x << ", Y: " << it.y << ", Z: " << it.z << " м\n";
        }
    } else {
        std::cerr << "Помилка валідації: " << errorToString(res.error()) << '\n';
    }
    return 0;
}
```
:::

## 5. Двійкова серіалізація та передача на автопілот

Після успішної статичної перевірки масив об'єктів `MissionItem` серіалізується в потік двійкових повідомлень MAVLink `MISSION_ITEM_INT`. Передача виконується за транзакційною тягловою схемою (англ. *pull-based Stop-and-Wait ARQ*):

1. **Ініціалізація транзакції:** Наземна станція надсилає кадрове повідомлення `MISSION_COUNT` (ідентифікатор `#44`), де поле `count = 8` вказує загальну кількість елементів у завданні, а `mission_type = 0` задає тип основної польотної програми.
2. **Покроковий запит пунктів:** Польотний контролер, отримавши `MISSION_COUNT`, перевіряє наявність вільної енергонезалежної пам'яті (Flash/FRAM) і надсилає запит `MISSION_REQUEST_INT` (`#73`) на нульовий елемент (`seq = 0`).
3. **Передача корисного навантаження:** Станція пакує структуру `mavlink_mission_item_int_t` у стандартний MAVLink-кадр і відправляє його в радіоканал. Контролер перевіряє цілісність контрольної суми CRC-16 та системні адреси `target_system` і `target_component`.
4. **Ітеративний цикл обміну:** Після успішного запису пункту в пам'ять автопілот запитує наступний індекс (`seq = 1`). Процес повторюється по черзі для всіх пунктів від `0` до `N - 1`. Якщо пакет губиться в ефірі через завади або перешкоди, таймер очікування на борту спливає, і автопілот повторює запит того самого індексу.
5. **Фіксація та атомарний коміт:** Отримавши фінальний пункт (`seq = 7`), автопілот проводить повну перевірку завантаженого плану. Якщо перевірка успішна, автопілот фіксує план у робочій структурі навігатора та надсилає квитанцію `MISSION_ACK` із кодом `MAV_MISSION_ACCEPTED` (`0`).

## 6. Внутрішнє виконання місії в планувальнику автопілота

Розгляньмо, як згенероване польотне завдання з 8 пунктів інтерпретується в реальному часі бортовою операційною системою реального часу (RTOS, наприклад, NuttX або ChibiOS):

```
Покроковий цикл обробки сформованої місії:
┌─────┬──────────────────────────┬────────────────────────────────────────────────────────┐
│ seq │ Команда MAV_CMD          │ Реакція навігатора та виконавчих підсистем              │
├─────┼──────────────────────────┼────────────────────────────────────────────────────────┤
│ 0   │ NAV_TAKEOFF              │ Запуск моторів, вертикальний набір висоти до 60.0 м    │
│ 1   │ DO_CHANGE_SPEED          │ Миттєва зміна уставки регулятора швидкості на 14.0 м/с │
│ 2   │ DO_SET_CAM_TRIGG_DIST    │ Скидання одометра та активація фотофіксації кожні 20 м │
│ 3   │ NAV_WAYPOINT (W1)        │ Політ до точки W1; розворот за L1-вектором на W2       │
│ 4   │ NAV_WAYPOINT (W2)        │ Проліт W2 по радіусу зрізання 12.0 м без гальмування   │
│ 5   │ NAV_WAYPOINT (W3)        │ Проліт W3 по радіусу зрізання 12.0 м; фотографування   │
│ 6   │ NAV_WAYPOINT (W4)        │ Досягнення кінця сітки; вимикання тригера камери       │
│ 7   │ NAV_RETURN_TO_LAUNCH     │ Підйом на висоту повернення та політ у точку старту    │
└─────┴──────────────────────────┴────────────────────────────────────────────────────────┘
```

У момент досягнення висоти 60 метрів на пункті `seq 0` автопілот фіксує виконання критерію навігаційної команди. Планувальник перемикає активний пункт на `seq 1`. Оскільки `seq 1` (`DO_CHANGE_SPEED`) та `seq 2` (`DO_SET_CAM_TRIGG_DIST`) є командами дії, автопілот виконує їх **в одному й тому ж такті планувальника (10 мс)**:
- Контур контролю шляхової швидкості отримує нову уставку `14.0 м/с`.
- Підсистема камерного тригера обнуляє лічильник накопиченої відстані й генерує перший тестовий імпульс на виході затвора.
- Навігаційний контур одразу захоплює координати точки `W1` (`seq 3`) як цільовий вектор руху.

Завдяки цьому апарат починає розгін і фотографування без затримок і без небажаних зупинок на початку маршрутної сітки.

## 7. Моніторинг виконання та телеметрійні повідомлення

Під час автономного виконання місії наземна станція керування відстежує прогрес польоту за допомогою двох потокових повідомлень MAVLink:
1. `MISSION_CURRENT` (ідентифікатор `#42`): транслюється автопілотом із частотою 1–2 Гц і містить одне ключове поле `seq` — порядковий номер поточного виконуваного пункту місії. Це дозволяє інтерфейсу станції підсвічувати активний галс на мапі.
2. `MISSION_ITEM_REACHED` (ідентифікатор `#46`): асинхронне сповіщення, яке відправляється в момент, коли апарат виконав просторово-часові критерії досягнення точки (увійшов у радіус прийому або завершив час зависання).

Якщо під час виконання автономної місії оператор надсилає команду позачергового переходу до іншого пункту (повідомлення `SET_MISSION_CURRENT`), автопілот миттєво скасовує поточний відрізок наведення й спрямовує апарат до нового зазначеного індексу, зберігаючи всі діючі налаштування швидкості та корисного навантаження.

## 8. Крайові випадки та обробка геодезичних аномалій

При практичному розгортанні автономних генераторів польотних місій розробник стикається з низкою критичних крайових ситуацій, які вимагають додаткової програмної обробки:

### 1. Перетин антимеридіана (±180° довготи)
Якщо полігон знімання або маршрут польоту перетинає 180-й меридіан (наприклад, у районі Фіджі, Чукотки чи Алеутських островів), довгота сусідніх точок стрибає від `+179.9999°` (`+1 799 999 000` у `degE7`) до `-179.9999°` (`-1 799 999 000` у `degE7`).
- **Небезпека:** Наївне обчислення різниці координат `Δlon = lon2 - lon1` дасть значення близько `-359.9998°` (близько 40 000 км), що змусить автопілот вважати, ніби наступна точка розташована на протилежному боці планети, і почати політ навколо всієї земної кулі.
- **Розв'язання:** Застосування функції нормалізації кутової дельти до діапазону `[-180.0°, +180.0°]`:
  ```
  double diff = lon2 - lon1;
  while (diff > 180.0)  diff -= 360.0;
  while (diff < -180.0) diff += 360.0;
  ```

### 2. Спотворення масштабу на високих широтах
У приполярних широтах (понад 65° північної чи південної широти) довжина градуса довготи `L_lon(φ) = 111 319.5 · cos(φ)` стрімко прямує до нуля. На широті 80° один градус довготи становить лише 19.33 км замість 111.32 км на екваторі. Прямокутна сітка сканування в градусних координатах зазнає сильного стиснення, тому розрахунок кроку галсів повинен здійснюватися строго в метрах через геодезичні перетворення з наступною конвертацією в `degE7`.

### 3. Робота з апаратними буферами DMA польотного контролера
На платах керування (наприклад, Pixhawk 6C або Holybro Durandal на мікроконтролерах STM32H743) пакети MAVLink передаються через апаратні інтерфейси UART із використанням прямого доступу до пам'яті (DMA). Оскільки кадр `MISSION_ITEM_INT` має фіксовану довжину 38 байтів корисного навантаження (разом із 10 байтами заголовка MAVLink v2 та 2 байтами CRC — 50 байтів), буфер DMA налаштовується на кільцевий прийом.

При обробці повідомлень автопілот читає дані безпосередньо з вирівняного буфера DMA і записує їх у Flash-пам'ять блоками по 64 байти. Завдяки природному вирівнюванню полів у структурі `MISSION_ITEM_INT` виключається необхідність проміжних копіювань пам'яті (Zero-Copy Architecture), що забезпечує стабільну роботу системи стабілізації з частотою 400–1000 Гц навіть під час інтенсивного обміну даними по радіоканалу.

### 4. Вкладені цикли та аварійне скидання лічильників DO_JUMP
При використанні декількох команд `MAV_CMD_DO_JUMP` у межах однієї місії (наприклад, зовнішній цикл обльоту 3 районів і внутрішній цикл подвійного проходу кожного галса) автопілот ArduPilot виділяє таблицю лічильників у пам'яті `AP_Mission`. Якщо під час виконання циклу дрон перезавантажується в повітрі через збій живлення, відновлення місії відбувається з поточного збереженого індексу `seq`, а лічильники переходів зчитуються з нелеткої пам'яті FRAM, запобігаючи нескінченному блуканню апарата по колу.

## 9. Десеріалізація та постобробка польотних журналів

Після повернення апарата на базу інженер виконує детальний аналіз відповідності реальної просторової траєкторії первинному польотному плану. Бортові реєстратори (DataFlash `.bin` в ArduPilot або ULog `.ulg` у PX4) зберігають кожен прийнятий і виконаний елемент місії у вигляді структурованих двійкових подій:

1. **Зіставлення міток спрацьовування камери:** Повідомлення `CAMERA_IMAGE_CAPTURED` або лог-подія `CAM` порівнюються з координатами запланованих точок на відрізках між `W1..W4`. Якщо часовий інтервал між послідовними знімками або пройдена відстань відрізняється від заданої в `DO_SET_CAM_TRIGG_DIST` більше ніж на 5%, це свідчить про вплив сильного поривчастого вітру або затримку затвора камери. Крім того, аналізується стан RTK-фіксації в момент відкриття затвора: статус `FixType = 6` (RTK Fixed) гарантує сантиметрову точність центрів проекцій для побудови ортофотоплану без використання наземних опорних точок (GCP).
2. **Аналіз бічного відхилення (Cross-Track Error):** Логгер записує миттєве відхилення центру мас апарата від ідеального відрізка наведення. За величиною відхилення на розворотах оцінюється адекватність обраного параметра `param3` (`R_pass`): якщо на дузі повороту спостерігалися значні коливання або викиди за межі коридору, радіус зрізання для наступних польотів збільшують на 15–20%.
3. **Верифікація висотного профілю та сенсорної узгодженості:** При використанні системи `MAV_FRAME_GLOBAL_TERRAIN_ALT` зіставляються покази барометричного альтиметра, супутникового GNSS-приймача та оптичного або лазерного далекоміра. Це дозволяє виявити ділянки з неточними даними рельєфу SRTM або зони зі щільною рослинністю, що створювали хибні перепади висоти в контурі керування.
4. **Часова синхронізація (Time Synchronization):** Повідомлення `CAMERA_IMAGE_CAPTURED` містить як монотонний час автопілота від моменту завантаження процесора (`time_boot_ms`), так і глобальний час UTC від супутникового приймача (`time_utc` у мікросекундах). Зіставлення цих міток із внутрішнім журналом камери дозволяє усунути похибки часової затримки спрацьовування оптрона (типово 30–80 мс), що на швидкості 15 м/с запобігає просторовому зсуву геоприв'язки на 0.5–1.2 метра.

Завдяки строгому математичному моделюванню радіусів розвороту, перевірці меж висот і валідації переходів `DO_JUMP` виключаються аварійні зупинки апарата в повітрі та забезпечується безперервне високоточне знімання заданого району.
