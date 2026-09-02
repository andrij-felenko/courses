#pragma once

#include <cstdint>
#include <expected>
#include <iosfwd>
#include <string>

// Зліпок телеметрії борту, знятий безпосередньо перед командою ARM.
// Значення за замовчуванням навмисно «погані»: недочитане поле не має
// шансу виглядати справним, навіть якщо парсер колись пропустить помилку.
struct TelemetrySnapshot {
    std::uint8_t  gps_fix_type{0};       // 3 = 3D Fix, 4 = DGPS, 5/6 = RTK
    std::uint8_t  gps_satellites{0};
    float         gps_hdop{99.0F};

    float         ekf_pos_innov{1.0F};   // нормовані похибки інновацій EKF
    float         ekf_vel_innov{1.0F};
    float         ekf_yaw_innov{1.0F};

    float         battery_voltage{0.0F}; // В
    float         cell_delta_v{9.0F};    // перекіс між осередками, В
    float         battery_temp_c{-40.0F};

    bool          geofence_enabled{false};
    std::uint16_t geofence_points{0};
    std::uint8_t  geofence_action{0};    // 1 = RTL, 2 = Land, 3 = Terminate

    std::int16_t  rc_rssi_dbm{-120};
    std::uint16_t rc_kill_channel{0};    // ШІМ аварійного каналу, мкс

    float         acc_vibe_floor{9.0F};  // фоновий шум акселерометра, м/с²
};

// Розбирає текстовий зліпок «ключ=значення» (імена ключів — імена полів
// структури, «#» починає коментар). Зліпок мусить бути повним: бракує поля —
// це помилка, а не привід лишити значення за замовчуванням.
//
// Помилку віддаємо через std::expected: у передпольотній перевірці «-1 і
// дивись errno» рано чи пізно закінчується проігнорованим кодом повернення.
[[nodiscard]] std::expected<TelemetrySnapshot, std::string> parse_snapshot(std::istream& in);
