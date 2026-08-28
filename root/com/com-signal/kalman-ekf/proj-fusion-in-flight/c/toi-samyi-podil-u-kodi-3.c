static SensorHealth gnss_health;   // correct_position штампує його так само, як барометр

// Сторож здоров'я: давач, що замовк, більше не прив'язує свій зріз —
// хмара цього зрізу росте на самому IMU. Це й вмикає EKF-failsafe в авто-режимах.
void ekf_health_check(uint32_t now_us)
{
    if (now_us - gnss_health.last_us > 500000u)  // 0.5 с без свіжого GPS
        gnss_health.healthy = false;             // горизонталь тепер дрейфує на IMU
    // решті давачів — свої таймаути, кожному за його темпом
}
