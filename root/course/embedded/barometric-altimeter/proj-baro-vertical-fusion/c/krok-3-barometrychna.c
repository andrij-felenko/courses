static float baro_p0 = 0.0f;    // опорний тиск, запам'ятований на зброєнні (Па)

// Запам'ятати нуль: викликати РАЗ, коли апарат нерухомий і зброєний.
void baro_set_zero(float pressure_now_pa) {
    baro_p0 = pressure_now_pa;
}

// Відносна висота над точкою старту (м). Біля землі досить лінійного кроку
// ~12 Па/м; для більших висот тут стояла б повна степенева формула ISA.
float baro_relative_altitude(float pressure_now_pa) {
    const float PA_PER_METER = 12.0f;
    return (baro_p0 - pressure_now_pa) / PA_PER_METER;
}
