#include "iec60751.hpp"
#include <iostream>
#include <iomanip>

int main() {
    IEC60751 sensor(100.0); // Pt100
    
    double t = -50.0;
    double r = sensor.temperature_to_resistance(t);
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Опір при " << t << " C: " << r << " Ом\n";
    
    double calc_t = sensor.resistance_to_temperature(r);
    std::cout << "Розрахована температура: " << calc_t << " C\n";
    
    LookupTable lut(sensor, -100.0, 200.0, 1.0);
    double lut_t = lut.lookup_temperature(r);
    
    std::cout << "Температура через LUT: " << lut_t << " C\n";
    
    return 0;
}
