import numpy as np

class ErrorAnalyzer:
    def __init__(self, reference_sensor, lut_sensor):
        self.ref = reference_sensor
        self.lut = lut_sensor

    def analyze(self, t_values: np.ndarray):
        r_exact = self.ref.temperature_to_resistance(t_values)
        t_lut = self.lut.lookup_temperature(r_exact)
        
        errors = np.abs(t_values - t_lut)
        
        return {
            'max_error_celsius': np.max(errors),
            'mean_error_celsius': np.mean(errors),
            'max_error_idx': np.argmax(errors)
        }
