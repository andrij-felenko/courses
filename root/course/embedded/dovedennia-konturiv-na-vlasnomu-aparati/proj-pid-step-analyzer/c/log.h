#ifndef LOG_H
#define LOG_H

#include <stddef.h>
#include <stdint.h>

/* Один відлік бортового логу польотного контролера.
   Час у мікросекундах від старту прошивки, кути — deg/s, D-терм — одиниці мікшера. */
typedef struct {
    uint64_t t_us;
    double   setpoint;   /* завдання кутової швидкості */
    double   gyro;       /* виміряна кутова швидкість */
    double   d_term;     /* вихід диференційної гілки контуру */
    double   vbat;       /* напруга батареї під навантаженням, В */
} LogSample;

typedef struct {
    LogSample *s;
    size_t     count;
    size_t     cap;
} FlightLog;

/* Читає CSV зі стовпчиками t_us,setpoint,gyro,d_term,vbat.
   Порожні рядки, коментарі з '#' і рядок-шапка пропускаються.
   Повертає 0; на помилці — -1, а пояснення кладе в err (не більше err_size байтів). */
int flightlog_load(const char *path, FlightLog *log, char *err, size_t err_size);

void flightlog_free(FlightLog *log);

/* Середній період дискретизації в мікросекундах; 0, якщо відліків менше двох. */
double flightlog_mean_dt_us(const FlightLog *log);

#endif /* LOG_H */
