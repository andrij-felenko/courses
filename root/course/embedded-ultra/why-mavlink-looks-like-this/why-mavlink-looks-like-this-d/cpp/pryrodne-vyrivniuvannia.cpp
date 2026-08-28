// Канонічна структура MAVLink ATTITUDE на C++ з нульовим паддингом
struct alignas(4) AttitudeMessage {
    uint32_t time_boot_ms{0}; // 4 байти (зсув 0x00)
    float    roll{0.0f};      // 4 байти (зсув 0x04)
    float    pitch{0.0f};     // 4 байти (зсув 0x08)
    float    yaw{0.0f};       // 4 байти (зсув 0x0C)
    float    rollspeed{0.0f}; // 4 байти (зсув 0x10)
    float    pitchspeed{0.0f};// 4 байти (зсув 0x14)
    float    yawspeed{0.0f};  // 4 байти (зсув 0x18)
}; // Розмір: рівно 28 байтів. Нуль байтів паддингу!
