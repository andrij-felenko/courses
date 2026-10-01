import time
import pyvisa
import numpy as np

# 1. Підключення до осцилографа через VISA
rm = pyvisa.ResourceManager()
scope = rm.open_resource('TCPIP0::192.168.1.100::INSTR')
scope.timeout = 5000  # Тайм-аут 5 секунд

# 2. Налаштування розгортки у режим Roll Mode
scope.write(':TIMebase:MODE ROLL')
scope.write(':TIMebase:SCALe 1.0')  # 1 секунда на поділ

# 3. Налаштування параметрів вивантаження хвилі
scope.write(':WAVeform:SOURce CHANnel1')
scope.write(':WAVeform:FORMat BYTE')
scope.write(':WAVeform:POINts 1000')

# Зчитування коефіцієнтів перетворення напруги
y_inc = float(scope.query(':WAVeform:YINCrement?'))
y_origo = float(scope.query(':WAVeform:YORigin?'))
y_ref = float(scope.query(':WAVeform:YREFerence?'))

print("Розпочато безперервний моніторинг у режимі Roll Mode...")

# 4. Цикл безперервного моніторингу
try:
    for cycle in range(10):
        # Перевірка наявності даних у вихідному буфері (MAV біт у STB)
        stb = int(scope.query('*STB?'))
        
        # Запит масиву даних вибірок
        raw_data = scope.query_binary_values(':WAVeform:DATA?', datatype='B', container=np.array)
        
        # Перерахунок сирих відліків у фізичні вольти
        voltage = (raw_data.astype(np.float64) - y_origo) * y_inc + y_ref
        
        mean_v = np.mean(voltage)
        print(f"Кадр {cycle+1}: середнє значення напруги = {mean_v:.3f} В")
        time.sleep(1.0)

finally:
    scope.close()
    rm.close()
