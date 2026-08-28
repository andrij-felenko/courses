# Зчитування телеметрії DOM оптичного модуля інтерфейсу eth0
ethtool -m eth0

# Приклад виводу утиліти ethtool на основі реєстрів SFF-8472:
# Identifier                : 0x03 (SFP)
# Extended identifier       : 0x04 (GBIC/SFP defined AC coupling)
# Connector                 : 0x07 (LC)
# Transceiver type          : 10G Ethernet 10GBASE-LR
# Laser bias current        : 18.500 mA
# Laser output power        : 1.2589 mW / 1.00 dBm
# Receiver signal average optical power : 0.0199 mW / -17.01 dBm
# Module temperature        : 35.00 degrees C
# Module voltage            : 3.3100 V
# Alarm/warning flags implemented : Yes
