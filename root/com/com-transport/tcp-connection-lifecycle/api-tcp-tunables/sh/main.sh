# Підрахунок кількості сокетів у кожному стані FSM
ss -s

# Вибірка всіх з'єднань у стані TIME_WAIT з числовими адресами
ss -tan state time-wait

# Вибірка сокетів, що очікують закриття процесом (CLOSE_WAIT)
ss -tan state close-wait

# Інспекція черг слухаючого сокета (Send-Q = somaxconn, Recv-Q = поточна accept_queue)
ss -ltn '( sport = :80 or sport = :443 )'

# Перегляд внутрішніх таймерів TCP (таймаути TIME_WAIT, Keepalive, Retransmission)
ss -tano state time-wait
