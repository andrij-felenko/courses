# telemetry_shared_mem.py
import time
import numpy as np
from multiprocessing import shared_memory, Process
from telemetry_serial import calibrate_chunk

def worker_process(shm_in_name, shm_out_name, shape, dtype, start_idx, end_idx):
    """Дочірній процес монтує існуючу спільну пам'ять за іменем."""
    shm_in = shared_memory.SharedMemory(name=shm_in_name)
    shm_out = shared_memory.SharedMemory(name=shm_out_name)
    
    # Створення масивів NumPy поверх сирих байтів спільної пам'яті
    input_arr = np.ndarray(shape, dtype=dtype, buffer=shm_in.buf)
    output_arr = np.ndarray((shape[0], 4), dtype=np.float64, buffer=shm_out.buf)
    
    # Виконання обчислень над виділеним діапазоном без копіювання
    chunk_result = calibrate_chunk(input_arr[start_idx:end_idx])
    output_arr[start_idx:end_idx] = chunk_result
    
    shm_in.close()
    shm_out.close()

def run_multiprocessing_shm(data, num_workers=4):
    n_rows, n_cols = data.shape
    
    # Створення спільних сегментів пам'яті ОС
    shm_in = shared_memory.SharedMemory(create=True, size=data.nbytes)
    shm_out = shared_memory.SharedMemory(create=True, size=n_rows * 4 * np.float64().itemsize)
    
    # Одноразове копіювання вхідних даних у спільний сегмент
    shm_in_arr = np.ndarray(data.shape, dtype=data.dtype, buffer=shm_in.buf)
    shm_in_arr[:] = data[:]
    
    chunk_size = n_rows // num_workers
    processes = []
    
    start = time.perf_counter()
    for w in range(num_workers):
        start_idx = w * chunk_size
        end_idx = (w + 1) * chunk_size if w != num_workers - 1 else n_rows
        p = Process(
            target=worker_process,
            args=(shm_in.name, shm_out.name, data.shape, data.dtype, start_idx, end_idx)
        )
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()
        
    elapsed = time.perf_counter() - start
    
    # Зчитування результату
    shm_out_arr = np.ndarray((n_rows, 4), dtype=np.float64, buffer=shm_out.buf)
    final_result = np.copy(shm_out_arr)
    
    # Обов'язкове звільнення системних дескрипторів та видалення shm
    shm_in.close()
    shm_in.unlink()
    shm_out.close()
    shm_out.unlink()
    
    return final_result, elapsed
