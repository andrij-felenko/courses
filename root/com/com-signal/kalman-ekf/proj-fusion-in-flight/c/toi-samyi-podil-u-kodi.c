#include <stdint.h>
#include <stdbool.h>

typedef struct { float gx, gy, gz;              // гіроскоп, рад/с  → веде передбачення
                 float ax, ay, az; } ImuSample; // акселерометр, м/с² → тримає нахил
typedef struct { float mx, my, mz; } MagSample;         // магнітометр → курс
typedef struct { float alt, var;   } BaroSample;        // висота (м) та шум виміру (м²)
typedef struct { float n, e, vn, ve, var; } GnssSample; // положення й швидкість

// Стан оцінювача поділено на зрізи — кожен прив'язує свій коректор.
typedef struct {
    float roll, pitch;          // нахил       <- акселерометр
    float yaw;                  // курс        <- магнітометр
    float alt,  P_alt;          // висота      <- барометр (і хмара висоти)
    float pos_n, pos_e;         // горизонталь <- GNSS
    float vel_n, vel_e;         // швидкість
    // повну коваріацію P тут опущено — на видноті сама диспетчеризація
} State;

// Шина давачів: прапор fresh піднятий лише в того, для кого цей такт — новий відлік.
typedef struct {
    ImuSample imu;                                 // є ЗАВЖДИ (веде передбачення)
    struct { bool fresh; MagSample  s; } mag;
    struct { bool fresh; BaroSample s; } baro;
    struct { bool fresh; GnssSample s; } gnss;
} SensorBus;

// Один такт оцінювача. Викликають на кожен тик IMU (сотні разів на секунду).
void ekf_step(State *x, const SensorBus *bus, uint32_t now_us)
{
    // 1. ПЕРЕДБАЧЕННЯ — завжди. Гіроскоп жене увесь стан і роздуває хмару (додає Q).
    ekf_predict(x, &bus->imu);

    // 2. КОРЕКЦІЯ — кожен коректор осаджує СВІЙ зріз стану.
    correct_tilt(x, &bus->imu, now_us);            // акселерометр того ж IMU -> нахил
    if (bus->mag.fresh)  correct_heading (x, &bus->mag.s,  now_us);   // -> курс
    if (bus->baro.fresh) correct_altitude(x, &bus->baro.s, now_us);   // -> висота
    if (bus->gnss.fresh) correct_position(x, &bus->gnss.s, now_us);   // -> горизонталь
}
