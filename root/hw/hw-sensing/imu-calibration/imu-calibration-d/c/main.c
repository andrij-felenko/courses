#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define IMU_CALIB_MAGIC   0x494D5543  /* "IMUC" */
#define IMU_CALIB_VERSION 2

/* Структура температурного полінома 3-го порядку для трьох осей */
typedef struct {
    float c0[3];      /* Вільний член (зсув при базовій температурі T0) */
    float c1[3];      /* Лінійний коефіцієнт (1/°C) */
    float c2[3];      /* Квадратичний коефіцієнт (1/°C^2) */
    float c3[3];      /* Кубічний коефіцієнт (1/°C^3) */
    float t0;         /* Базова температура калібрування, °C */
} imu_temp_poly_t;

/* Повна структура калібрувального профілю для Flash/EEPROM */
typedef struct {
    uint32_t magic;           /* Магічне число валідації */
    uint16_t version;         /* Версія структури даних */
    uint16_t reserved;        /* Вирівнювання на 4 байти */
    
    float accel_matrix[3][3]; /* 3x3 матриця масштабу та неортогональності K_acc */
    float accel_bias[3];      /* Статичний зсув нуля акселерометра */
    
    float gyro_matrix[3][3];  /* 3x3 матриця калібрування гіроскопа K_gyro */
    imu_temp_poly_t gyro_poly;/* Поліноми температурного зсуву гіроскопа */
    
    uint32_t crc32;           /* Контрольна сума CRC32 заголовка й даних */
} imu_calib_profile_t;

/* Обчислення швидкого апаратного або табличного CRC32 */
uint32_t imu_calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

/* Ініціалізація профілю за замовчуванням (одиничні матриці, нульові зсуви) */
void imu_calib_set_defaults(imu_calib_profile_t *prof) {
    memset(prof, 0, sizeof(imu_calib_profile_t));
    prof->magic = IMU_CALIB_MAGIC;
    prof->version = IMU_CALIB_VERSION;
    
    prof->accel_matrix[0][0] = 1.0f;
    prof->accel_matrix[1][1] = 1.0f;
    prof->accel_matrix[2][2] = 1.0f;
    
    prof->gyro_matrix[0][0] = 1.0f;
    prof->gyro_matrix[1][1] = 1.0f;
    prof->gyro_matrix[2][2] = 1.0f;
    
    prof->gyro_poly.t0 = 25.0f;
    prof->crc32 = imu_calc_crc32((const uint8_t*)prof, sizeof(imu_calib_profile_t) - sizeof(uint32_t));
}

/* Перевірка цілісності профілю в пам'яті */
bool imu_calib_validate(const imu_calib_profile_t *prof) {
    if (prof->magic != IMU_CALIB_MAGIC || prof->version != IMU_CALIB_VERSION) {
        return false;
    }
    uint32_t calculated_crc = imu_calc_crc32((const uint8_t*)prof, 
                                            sizeof(imu_calib_profile_t) - sizeof(uint32_t));
    return (calculated_crc == prof->crc32);
}

/* Високопродуктивний конвеєр корекції вектора прискорення */
void imu_apply_accel_calib(const imu_calib_profile_t *prof, const float raw[3], float out_cal[3]) {
    /* Крок 1: Віднімання зсуву нуля */
    float zx = raw[0] - prof->accel_bias[0];
    float zy = raw[1] - prof->accel_bias[1];
    float zz = raw[2] - prof->accel_bias[2];
    
    /* Крок 2: Множення на 3x3 матрицю корекції */
    out_cal[0] = prof->accel_matrix[0][0] * zx + prof->accel_matrix[0][1] * zy + prof->accel_matrix[0][2] * zz;
    out_cal[1] = prof->accel_matrix[1][0] * zx + prof->accel_matrix[1][1] * zy + prof->accel_matrix[1][2] * zz;
    out_cal[2] = prof->accel_matrix[2][0] * zx + prof->accel_matrix[2][1] * zy + prof->accel_matrix[2][2] * zz;
}

/* Високопродуктивний конвеєр корекції гіроскопа з температурною компенсацією */
void imu_apply_gyro_calib(const imu_calib_profile_t *prof, const float raw[3], float temp_c, float out_cal[3]) {
    float dt = temp_c - prof->gyro_poly.t0;
    float bias[3];
    
    /* Крок 1: Обчислення температурного зсуву за схемою Горнера для 3 осей */
    for (int i = 0; i < 3; ++i) {
        bias[i] = prof->gyro_poly.c0[i] + dt * (prof->gyro_poly.c1[i] + 
                  dt * (prof->gyro_poly.c2[i] + dt * prof->gyro_poly.c3[i]));
    }
    
    /* Крок 2: Віднімання зсуву нуля */
    float zx = raw[0] - bias[0];
    float zy = raw[1] - bias[1];
    float zz = raw[2] - bias[2];
    
    /* Крок 3: Множення на 3x3 матрицю корекції */
    out_cal[0] = prof->gyro_matrix[0][0] * zx + prof->gyro_matrix[0][1] * zy + prof->gyro_matrix[0][2] * zz;
    out_cal[1] = prof->gyro_matrix[1][0] * zx + prof->gyro_matrix[1][1] * zy + prof->gyro_matrix[1][2] * zz;
    out_cal[2] = prof->gyro_matrix[2][0] * zx + prof->gyro_matrix[2][1] * zy + prof->gyro_matrix[2][2] * zz;
}
