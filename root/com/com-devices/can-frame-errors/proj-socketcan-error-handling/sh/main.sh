# Встановлення номінальної швидкості 500 кбіт/с та автоматичного виходу з Bus-Off через 100 мс
sudo ip link set can0 type can bitrate 500000 restart-ms 100

# Для інтерфейсів CAN FD: номінальна швидкість 500 кбіт/с, фаза даних 2 Мбіт/с
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on restart-ms 100

# Підняття інтерфейсу
sudo ip link set can0 up

# Перевірка поточного стану контролера, лічильників та розширеної статистики
ip -details -statistics link show can0
