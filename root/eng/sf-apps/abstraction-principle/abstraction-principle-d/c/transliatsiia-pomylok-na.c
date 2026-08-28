// ── Погана абстракція: сира помилка ядра Linux протікає в бізнес-логіку
int altitude_bad = get_raw_sensor_altitude();
if (altitude_bad == -110) { // -ETIMEDOUT: бізнес-логіка знає коди POSIX!
    trigger_failsafe();
}

// ── Правильна абстракція: трансляція в типізовані доменні стани
typedef enum {
    ALTITUDE_OK = 0,
    ALTITUDE_SENSOR_UNAVAILABLE,
    ALTITUDE_DATA_CORRUPTED
} altitude_status_t;

typedef struct {
    int32_t altitude_mm;
    altitude_status_t status;
} altitude_reading_t;

altitude_reading_t reading = read_altitude_abstract();
if (reading.status == ALTITUDE_SENSOR_UNAVAILABLE) {
    trigger_failsafe();
}
