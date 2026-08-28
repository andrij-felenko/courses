from machine import Pin, SPI
from time import sleep
from sx127x import SX127x        # драйвер sx127x для MicroPython

# апаратний SPI + ті самі три вільні ніжки, що й в Arduino
spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
pins = {'ss': 5, 'reset': 14, 'dio_0': 2}   # NSS / RST / DIO0

# 868E6 для Європи, 915E6 для США, 433E6 — де дозволено.
# Частоту й SF на ОБОХ кінцях лінії треба виставити ОДНАКОВО.
lora = SX127x(spi, pins=pins, parameters={
    'frequency': 868_000_000,
    'spreading_factor': 9,        # SF7…SF12: більше = далі, але повільніше
    'tx_power_level': 17,         # дБм; межа залежить від виходу PA, див. нижче
})
# конструктор сам чіпає чип по SPI; якщо MISO/MOSI переплутані,
# не той NSS чи нема 3.3 В — читання версії поверне сміття

while True:
    lora.begin_packet()
    lora.write(b'hello')
    lora.end_packet()             # блокує, доки чип не передасть (DIO0 ↑)
    sleep(5)
