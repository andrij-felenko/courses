# Встановлення швидкості 500 кбіт/с для класичного CAN
sudo ip link set can0 type can bitrate 500000

# Включення CAN FD: номінальна швидкість 500 кбіт/с, швидкість даних 2 Мбіт/с
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on

# Автоматичне відновлення зі стану Bus-Off через 100 мс
sudo ip link set can0 type can restart-ms 100

# Активація мережевого інтерфейсу
sudo ip link set can0 up
