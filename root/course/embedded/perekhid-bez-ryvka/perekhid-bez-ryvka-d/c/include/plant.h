#ifndef PLANT_H
#define PLANT_H

#define PLANT_G 9.80665f

/* Вертикальний канал квадрокоптера: маса, тяга, лобовий опір по вертикалі.
   Тяга нормалізована: throttle = 1.0 віддає thrust_max_n ньютонів. */
typedef struct {
    float mass_kg;
    float thrust_max_n;
    float drag_coeff;   /* Н на (м/с) */
    float altitude_m;
    float vz_mps;
    float accel_mps2;   /* остання вертикальна прискорення — для перевантаги */
} quad_plant_t;

/* hover_throttle задає масштаб тяги: газ висіння точно врівноважує вагу. */
void quad_plant_init(quad_plant_t *p, float mass_kg, float hover_throttle, float alt0_m);
void quad_plant_step(quad_plant_t *p, float throttle, float dt);
float quad_plant_load_factor(const quad_plant_t *p);

/* Боковий канал: команда приводу задає кутову швидкість крену, кут дає
   горизонтальне прискорення. trim_bias — паразитний момент від зміщення ЦМ,
   саме його інтегратор внутрішнього контуру й тримає в пам'яті. */
typedef struct {
    float rate_gain;    /* рад/с на одиницю команди */
    float trim_bias;    /* сталий момент, од. команди */
    float wind_accel;   /* боковий вітер, м/с^2 */
    float drag;         /* 1/с */
    float position_m;
    float velocity_mps;
    float angle_rad;
} lat_plant_t;

void lat_plant_init(lat_plant_t *p, float rate_gain, float trim_bias,
                    float wind_accel, float drag);
void lat_plant_step(lat_plant_t *p, float actuator, float dt);

/* Сервопривід з обмеженою швидкістю перекладки й люфтом трансмісії:
   автопілот знає команду, вал живе своїм життям. */
typedef struct {
    float position_deg;
    float rate_max_dps;
    float deadband_deg;
} servo_t;

void servo_init(servo_t *s, float rate_max_dps, float deadband_deg, float position_deg);
float servo_step(servo_t *s, float command_deg, float dt);

#endif /* PLANT_H */
