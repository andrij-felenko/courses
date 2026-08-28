#include <stdint.h>

#define FAULT_RC_LOST       (1u << 0)  // Втрата сигналу пульта керування
#define FAULT_GCS_LOST      (1u << 1)  // Втрата телеметрії наземної станції
#define FAULT_GNSS_GLITCH   (1u << 2)  // Стрибок HDOP / втрата 3D Fix
#define FAULT_BATT_LOW      (1u << 3)  // Перший поріг розряду (Warning)
#define FAULT_BATT_CRIT     (1u << 4)  // Критичний поріг розряду (Land)
#define FAULT_GEOFENCE      (1u << 5)  // Вихід за межі дозволеного радіуса/стелі
#define FAULT_ACTUATOR      (1u << 6)  // Відмова мотора, ESC або сервоприводу
#define FAULT_ATTITUDE_LOSS (1u << 7)  // Втрата розрахунку просторової орієнтації
