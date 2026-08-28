# Перегляд поточних параметрів таймерів та лімітів
sysctl -a | grep net.sctp

# Оптимізація для низьколатентних сигнальних мереж
sudo sysctl -w net.sctp.rto_initial=1000       # Початковий RTO = 1000 мс (замість 3000)
sudo sysctl -w net.sctp.rto_min=100           # Мінімальний RTO = 100 мс (замість 1000)
sudo sysctl -w net.sctp.rto_max=5000          # Максимальний RTO = 5000 мс (замість 60000)
sudo sysctl -w net.sctp.path_max_retrans=3     # Поріг відмови фізичного шляху
sudo sysctl -w net.sctp.association_max_retrans=6 # Поріг розриву асоціації
sudo sysctl -w net.sctp.hb_interval=2000      # Інтервал зондування Heartbeat = 2 с
sudo sysctl -w net.sctp.rcvbuf_policy=1       # Індивідуальні буфери на кожну асоціацію
sudo sysctl -w net.sctp.cookie_preserve_time=30000 # Час життя State Cookie (30 с)
