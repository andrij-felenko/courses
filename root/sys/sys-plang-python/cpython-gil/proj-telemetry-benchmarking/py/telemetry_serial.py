# telemetry_serial.py
import time
import math
import numpy as np

def calibrate_chunk(data_slice):
    """Обробка порції телеметрії: матричні перетворення та поліном."""
    n_records = len(data_slice)
    results = np.empty((n_records, 4), dtype=np.float64)
    
    # Калібрувальні коефіцієнти сенсорного вузла
    bias = np.array([0.05, -0.02, 0.01], dtype=np.float64)
    scale_matrix = np.array([
        [1.02, 0.01, 0.00],
        [0.01, 0.99, -0.01],
        [0.00, 0.02, 1.01]
    ], dtype=np.float64)
    
    for i in range(n_records):
        raw_vec = data_slice[i, 0:3] - bias
        cal_vec = scale_matrix @ raw_vec
        
        # Поліноміальна температурна компенсація
        temp = data_slice[i, 3]
        temp_comp = 0.12 + 0.95 * temp + 0.003 * (temp ** 2) - 0.0001 * (temp ** 3)
        
        results[i, 0:3] = cal_vec * (1.0 + 0.001 * temp_comp)
        results[i, 3] = temp_comp
        
    return results

def run_serial(data):
    start = time.perf_counter()
    res = calibrate_chunk(data)
    elapsed = time.perf_counter() - start
    return res, elapsed
