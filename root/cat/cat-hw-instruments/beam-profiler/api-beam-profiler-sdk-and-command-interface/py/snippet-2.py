import pyvisa
import time

rm = pyvisa.ResourceManager()
# Відкриття VISA-сесії з лінійним переміщувачем по засобу USB/RS-232
stage = rm.open_resource('USB0::0x1AB1::0x0111::STAGE12345::INSTR')

# Запит ідентифікації контролера позиціонера
print("Пристрій:", stage.query('*IDN?').strip())

z_positions_mm = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]

for z in z_positions_mm:
    # Надсилання SCPI-команди позиціонування вздовж оптичної осі
    stage.write(f'POSITION:MOVE:ABSOLUTE {z}')
    
    # Очікування завершення руху актуатора
    while stage.query('POSITION:STATE?').strip() != 'READY':
        time.sleep(0.1)
    
    print(f"Позиціонер переміщено в Z = {z} мм. Захоплення профілю пучка...")
    # Тут виконується виклик захоплення кадру SDK та зчитування діаметра D4σ

stage.close()
