import numpy as np
from iec60751 import IEC60751, LookupTable
from error_analysis import ErrorAnalyzer

def main():
    sensor = IEC60751(r0=100.0) # Pt100
    
    temperatures = np.array([-50.0, 0.0, 25.0, 100.0, 150.0])
    resistances = sensor.temperature_to_resistance(temperatures)
    print("Температури:", temperatures)
    print("Опори:", resistances)
    
    calc_t = sensor.resistance_to_temperature(resistances)
    print("Зворотне перетворення:", calc_t)
    
    lut = LookupTable(t_min=-100.0, t_max=200.0, step=1.0)
    lut_t = lut.lookup_temperature(resistances)
    print("Температури з LUT:", lut_t)
    
    analyzer = ErrorAnalyzer(sensor, lut)
    test_temps = np.linspace(-100, 200, 500)
    stats = analyzer.analyze(test_temps)
    print("Максимальна похибка LUT:", stats['max_error_celsius'], "°C")

if __name__ == "__main__":
    main()
