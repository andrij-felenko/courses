# 1. Перевірка стану серверів у пулах
echo "show stat" | socat stdio /var/run/haproxy.sock | cut -d ',' -f 1,2,18,19

# 2. Активація зеленого середовища (переведення вузлів у статус ready)
echo "set server backend_green/srv_g1 state ready" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g2 state ready" | socat stdio /var/run/haproxy.sock

# 3. Встановлення повної ваги для зеленого пулу
echo "set server backend_green/srv_g1 weight 100" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g2 weight 100" | socat stdio /var/run/haproxy.sock

# 4. Переведення синього пулу в режим дренажу (нові запити не йдуть, старі добігають)
echo "set server backend_blue/srv_b1 state drain" | socat stdio /var/run/haproxy.sock
echo "set server backend_blue/srv_b2 state drain" | socat stdio /var/run/haproxy.sock

# 5. ЕКСТРЕНИЙ ВІДКАТ НА СИНІЙ (виконується за 1 мс у разі збою)
echo "set server backend_blue/srv_b1 state ready" | socat stdio /var/run/haproxy.sock
echo "set server backend_blue/srv_b2 state ready" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g1 state maint" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g2 state maint" | socat stdio /var/run/haproxy.sock
