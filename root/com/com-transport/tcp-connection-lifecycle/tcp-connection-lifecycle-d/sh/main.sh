# Підрахунок з'єднань у кожному стані FSM
ss -s

# Перегляд усіх сокетів у стані TIME_WAIT з числовими портами
ss -tan state time-wait

# Пошук з'єднань, завислих у CLOSE_WAIT (помилка виклику close() у коді застосунку)
ss -tan state close-wait

# Інспекція внутрішніх таймерів TCP (відображення часу до виходу з TIME_WAIT)
ss -tano state time-wait
