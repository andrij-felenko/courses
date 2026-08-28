// Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
class HardIronCalib {
    std::int16_t xmin = 32767, xmax = -32768;
    std::int16_t ymin = 32767, ymax = -32768;
public:
    void update(std::int16_t x, std::int16_t y) {   // виклик у циклі під час обертання
        xmin = std::min(xmin, x);  xmax = std::max(xmax, x);
        ymin = std::min(ymin, y);  ymax = std::max(ymax, y);
    }

    float heading(std::int16_t x, std::int16_t y, float declination_deg) const {
        std::int16_t xoff = (xmax + xmin) / 2;  // центр кола по X = зсув твердого заліза
        std::int16_t yoff = (ymax + ymin) / 2;
        return compass_heading(x - xoff, y - yoff, declination_deg);
    }
};
