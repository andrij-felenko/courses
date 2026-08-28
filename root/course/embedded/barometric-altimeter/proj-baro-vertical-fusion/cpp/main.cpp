class BaroAltitude {
    float p0_ = 0.0f;    // опорний тиск, запам'ятований на зброєнні (Па)

public:
    // Запам'ятати нуль: викликати РАЗ, коли апарат нерухомий і зброєний.
    void set_zero(float pressure_now_pa) {
        p0_ = pressure_now_pa;
    }

    // Відносна висота над точкою старту (м). Біля землі досить лінійного кроку
    // ~12 Па/м; для більших висот тут стояла б повна степенева формула ISA.
    float relative_altitude(float pressure_now_pa) const {
        constexpr float kPaPerMeter = 12.0f;
        return (p0_ - pressure_now_pa) / kPaPerMeter;
    }
};
