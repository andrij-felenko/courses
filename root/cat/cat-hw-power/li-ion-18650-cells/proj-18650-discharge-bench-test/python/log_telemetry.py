# Автоматизоване зчитування телеметрії струму, напруги та температури з електронного навантаження через Serial-порт, збереження CSV-журналу та побудова розрядних кривих
import serial
import csv
import matplotlib.pyplot as plt
import time

def log_discharge(port, baudrate, filename):
    times, voltages, currents = [], [], []
    
    with serial.Serial(port, baudrate, timeout=1) as ser, \
         open(filename, 'w', newline='') as csvfile:
        
        writer = csv.writer(csvfile)
        writer.writerow(['Time(s)', 'Voltage(V)', 'Current(A)', 'Capacity(mAh)', 'Temp(C)'])
        
        start_time = time.time()
        capacity_mah = 0.0
        
        try:
            while True:
                line = ser.readline().decode('utf-8').strip()
                if not line: continue
                
                # Очікується формат: V,I,T
                parts = line.split(',')
                if len(parts) == 3:
                    v, i, t = map(float, parts)
                    elapsed = time.time() - start_time
                    
                    # Інтегрування ємності: I(A) * dt(s) / 3600 = Ah -> mAh
                    capacity_mah += (i * 1000) * (1.0 / 3600.0) 
                    
                    writer.writerow([elapsed, v, i, capacity_mah, t])
                    
                    times.append(elapsed)
                    voltages.append(v)
                    currents.append(i)
                    
                    if v <= 2.75:
                        print(f"Cutoff voltage reached. Total Capacity: {capacity_mah:.1f} mAh")
                        break
                        
        except KeyboardInterrupt:
            print("Stopped manually.")
            
    plt.plot(times, voltages)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('Discharge Curve')
    plt.show()
