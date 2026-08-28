# telemetry_threads.py
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from telemetry_serial import calibrate_chunk

def run_threads(data, num_workers=4):
    chunk_size = len(data) // num_workers
    chunks = [data[i * chunk_size : (i + 1) * chunk_size] for i in range(num_workers)]
    
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(calibrate_chunk, chunks))
        
    final_result = np.vstack(results)
    elapsed = time.perf_counter() - start
    return final_result, elapsed
