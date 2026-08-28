typedef enum HL_FAILURE_FLAG {
    HL_FAILURE_FLAG_GPS                   = 1,     // Біт 0: Втрата фіксації GPS або вихід похибки за межі
    HL_FAILURE_FLAG_DIFFERENTIAL_PRESSURE = 2,     // Біт 1: Відмова датчика повітряної швидкості (трубка Піто)
    HL_FAILURE_FLAG_ABSOLUTE_PRESSURE     = 4,     // Біт 2: Відмова барометра (абсолютний тиск)
    HL_FAILURE_FLAG_3D_ACCEL              = 8,     // Біт 3: Збій або розкалібрування акселерометра IMU
    HL_FAILURE_FLAG_3D_GYRO               = 16,    // Біт 4: Збій гіроскопа IMU (дрейф кутової швидкості)
    HL_FAILURE_FLAG_3D_MAG                = 32,    // Біт 5: Магнітна аномалія або відмова компаса
    HL_FAILURE_FLAG_TERRAIN               = 64,    // Біт 6: Недоступні дані висоти рельєфу (Terrain DB)
    HL_FAILURE_FLAG_BATTERY               = 128,   // Біт 7: Критичний рівень розряду батареї або перегрів
    HL_FAILURE_FLAG_RC_RECEIVER           = 256,   // Біт 8: Втрата сигналу апаратури радіокерування (RC)
    HL_FAILURE_FLAG_OFFBOARD              = 512,   // Біт 9: Втрата зв'язку з супутнім бортовим комп'ютером
    HL_FAILURE_FLAG_ENGINE                = 1024,  // Біт 10: Зупинка двигуна, відмова ESC або збій палива
    HL_FAILURE_FLAG_GEOFENCE              = 2048,  // Біт 11: Порушення кордону геозони (Geofence Breach)
    HL_FAILURE_FLAG_ESTIMATOR             = 4096,  // Біт 12: Розбіжність або деградація навігаційного фільтра EKF
    HL_FAILURE_FLAG_MISSION               = 8192   // Біт 13: Некоректне польотне завдання або недосяжна точка
} HL_FAILURE_FLAG;
