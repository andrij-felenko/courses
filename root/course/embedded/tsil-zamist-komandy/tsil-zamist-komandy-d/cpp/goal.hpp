#pragma once

// Типи диспетчера автономних цілей. Пам'ять статична: черга фіксованого
// розміру, жодного динамічного виділення в польоті.

#include <cmath>
#include <cstdint>

namespace autonomy {

using Seconds = float; // секунди; окремий псевдонім, щоб не плутати з метрами

// Світова система координат NED: x — на північ, y — на схід, z — УНИЗ.
// Висота над точкою старту дорівнює -(z - home.z).
struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    friend constexpr Vec3 operator-(Vec3 a, Vec3 b) noexcept
    {
        return {a.x - b.x, a.y - b.y, a.z - b.z};
    }
    friend constexpr Vec3 operator*(Vec3 v, float k) noexcept
    {
        return {v.x * k, v.y * k, v.z * k};
    }
};

[[nodiscard]] constexpr float dot(Vec3 a, Vec3 b) noexcept
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

[[nodiscard]] inline float norm(Vec3 v) noexcept
{
    return std::sqrt(dot(v, v));
}

// Строгий тип ідентифікатора: ціль не переплутати з індексом слота чи лічильником.
enum class GoalId : std::uint32_t { None = 0 };

enum class GoalType : std::uint8_t { Waypoint, SurveyArea, HoldPosition, EmergencyRth };

enum class GoalState : std::uint8_t {
    Free, // слот у черзі порожній
    Pending,
    Validating,
    Active,
    Preempted,
    Completed,
    Aborted,
    Rejected
};

// Шкала пріоритетів із таблиці статті.
enum class Priority : std::uint8_t {
    Service = 10,   // фонові сервісні завдання
    Mission = 50,   // основна польотна місія
    Subtask = 100,  // динамічні підзадачі, дорозвідка
    Operator = 150, // оперативне переривання оператором
    Emergency = 255 // аварійне повернення, ухилення від зіткнення
};

[[nodiscard]] constexpr int raw(Priority p) noexcept
{
    return static_cast<int>(p);
}

// Причина відмови в допуску або зняття цілі з виконання.
enum class RejectReason : std::uint8_t {
    BadRequest,      // ціль сформовано неправильно
    EkfDiverged,     // дисперсія навігаційної оцінки поза допуском
    OutsideGeofence, // точка за межами дозволеної зони
    NoEnergy,        // не вистачить на «дійти й повернутися»
    Headwind,        // вітер сильніший за апарат: треку не витримати
    Timeout,         // ціль не встигла у відведений час
    PathBlocked,     // прохід заблоковано, обходу не знайдено
    SensorFailure,   // критична: відмова давачів
    MotorFailure,    // критична: відмова силової установки
    Cancelled        // знято оператором
};

// Критична причина веде ціль в Aborted, решта — у Rejected.
[[nodiscard]] constexpr bool is_critical(RejectReason r) noexcept
{
    return r == RejectReason::SensorFailure || r == RejectReason::MotorFailure;
}

struct Goal {
    GoalId id{GoalId::None};
    GoalType type{GoalType::Waypoint};
    Priority priority{Priority::Mission};
    Vec3 target{};
    float acceptance_radius{2.0F}; // R_tol, метри
    Seconds timeout{0.0F};         // 0 — без обмеження часу
    float cruise_airspeed{12.0F};  // повітряна швидкість на маршруті, м/с
};

// Зріз стану апарата від оцінювача (EKF) і монітора живлення. Диспетчер читає.
struct Vehicle {
    Vec3 pos{};
    float battery_voltage{25.2F};
    float battery_energy_wh{200.0F};
    float cruise_power_w{450.0F};
    Vec3 wind{};                  // швидкість повітряної маси, м/с, NED
    float ekf_pos_variance{0.1F}; // дисперсія оцінки позиції, м²
    bool sensors_ok{true};
    bool motors_ok{true};
};

} // namespace autonomy
