// СЛАБША й ЛОКАЛІЗОВАНА: за іменем замість за позицією/змістом.
// Іменовані поля — переставити неможливо; константи — угода в тексті.
struct SensorConfig {
    int  channel;
    Gain gain      = Gain::High;    // було "3" — тепер має ім'я
    bool interrupt = true;
    int  periodMs  = 500;
};
setupSensor({ .channel = 1 });      // читається саме собою, решта — типові
setupSensor({ .channel = 2 });      // спільні значення живуть в ОДНОМУ місці
