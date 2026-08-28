enum class HlFailureFlag : uint16_t {
    Gps                  = 1,     // Біт 0: Втрата фіксації GPS або деградація точності
    DifferentialPressure = 2,     // Біт 1: Відмова датчика повітряної швидкості (трубка Піто)
    AbsolutePressure     = 4,     // Біт 2: Відмова барометра
    Accel3D              = 8,     // Біт 3: Збій акселерометра IMU
    Gyro3D               = 16,    // Біт 4: Збій гіроскопа IMU
    Mag3D                = 32,    // Біт 5: Відмова магнітометра / компаса
    Terrain              = 64,    // Біт 6: Відсутність даних висоти рельєфу
    Battery              = 128,   // Біт 7: Критичний розряд батареї або перегрів
    RcReceiver           = 256,   // Біт 8: Втрата сигналу апаратури радіокерування
    Offboard             = 512,   // Біт 9: Втрата зв'язку з супутнім бортовим комп'ютером
    Engine               = 1024,  // Біт 10: Відмова силової установки або регулятора ESC
    Geofence             = 2048,  // Біт 11: Порушення меж дозволеної геозони
    Estimator            = 4096,  // Біт 12: Розбіжність навігаційного фільтра EKF
    Mission              = 8192   // Біт 13: Помилка польотного завдання
};

constexpr HlFailureFlag operator|(HlFailureFlag a, HlFailureFlag b) noexcept {
    return static_cast<HlFailureFlag>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

constexpr bool operator&(HlFailureFlag a, HlFailureFlag b) noexcept {
    return (static_cast<uint16_t>(a) & static_cast<uint16_t>(b)) != 0;
}
